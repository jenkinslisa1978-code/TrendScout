"""
AliExpress Data Scraper

Scrapes product data from AliExpress including:
- Product names and descriptions
- Supplier costs
- Order counts (demand signals)
- Reviews and ratings
- Images

Rate limited to 1 request per second with 24-hour caching.
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from . import BaseScraper, ScraperConfig, DataIngestionResult


class AliExpressScraper(BaseScraper):
    """
    AliExpress product data scraper.
    
    Scrapes product listings and details to extract:
    - Product name, description
    - Supplier cost (original price)
    - Order count (demand signal)
    - Review count and rating
    - Product images
    """
    
    SEARCH_URL = "https://www.aliexpress.com/wholesale"
    PRODUCT_URL_TEMPLATE = "https://www.aliexpress.com/item/{product_id}.html"
    
    # Popular dropshipping categories
    TRENDING_CATEGORIES = [
        "home decor",
        "portable electronics", 
        "beauty tools",
        "kitchen gadgets",
        "pet supplies",
        "fitness accessories",
        "car accessories",
        "phone accessories",
        "office supplies",
        "fashion accessories"
    ]
    
    def __init__(self, db):
        config = ScraperConfig(
            name="aliexpress",
            base_url="https://www.aliexpress.com",
            rate_limit_per_second=1.0,  # 1 request per second
            cache_ttl_hours=24,
            retry_attempts=3,
            timeout_seconds=30,
            enabled=True
        )
        super().__init__(db, config)
    
    async def scrape(
        self, 
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_products: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape products from AliExpress.
        
        Args:
            query: Search query (if None, uses trending categories)
            category: Specific category to search
            max_products: Maximum products to fetch
            
        Returns:
            List of scraped product data
        """
        products = []
        
        # If no query, scrape from trending categories
        if not query and not category:
            for cat in self.TRENDING_CATEGORIES[:3]:  # Limit categories per run
                cat_products = await self._scrape_category(cat, max_products // 3)
                products.extend(cat_products)
                
                if len(products) >= max_products:
                    break
        else:
            search_term = query or category
            products = await self._scrape_search(search_term, max_products)
        
        return products[:max_products]
    
    async def _scrape_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape search results for a query"""
        products = []
        
        # Build search URL
        params = {
            'SearchText': query.replace(' ', '+'),
            'sortType': 'total_tranpro_desc',  # Sort by orders
        }
        url = f"{self.SEARCH_URL}?SearchText={params['SearchText']}&sortType={params['sortType']}"
        
        self.logger.info(f"Scraping AliExpress search: {query}")
        
        html, success = await self.fetch_with_retry(url)
        
        if not success or not html:
            self.logger.warning(f"Failed to fetch AliExpress search for: {query}")
            return products
        
        # Parse search results
        try:
            products = self._parse_search_results(html, query)
        except Exception as e:
            self.logger.error(f"Error parsing AliExpress search results: {e}")
        
        return products[:limit]
    
    async def _scrape_category(self, category: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape products from a category"""
        return await self._scrape_search(category, limit)
    
    def _parse_search_results(self, html: str, search_query: str) -> List[Dict[str, Any]]:
        """Parse AliExpress search results HTML"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find product data in various formats
        # AliExpress uses multiple page structures
        
        # Method 1: Look for __INIT_DATA__ script
        script_data = self._extract_json_data(html)
        if script_data:
            products = self._parse_json_products(script_data, search_query)
            if products:
                return products
        
        # Method 2: Parse HTML product cards
        product_cards = soup.select('[class*="product-card"], [class*="list-item"], [data-product-id]')
        
        for card in product_cards:
            try:
                product = self._parse_product_card(card, search_query)
                if product and product.get('product_name'):
                    products.append(product)
            except Exception as e:
                self.logger.debug(f"Failed to parse product card: {e}")
        
        # Method 3: Try alternative selectors
        if not products:
            products = self._parse_alternative_format(soup, search_query)
        
        return products
    
    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Extract JSON data embedded in page"""
        patterns = [
            r'window\.__INIT_DATA__\s*=\s*({.+?});',
            r'window\.runParams\s*=\s*({.+?});',
            r'"mods":\s*({.+?})\s*,\s*"pageConfig"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_json_products(self, data: Dict, search_query: str) -> List[Dict[str, Any]]:
        """Parse products from JSON data"""
        products = []
        
        # Navigate through possible data structures
        items_list = None
        
        if 'data' in data and 'root' in data['data']:
            # New structure
            mods = data['data']['root'].get('fields', {})
            items_list = mods.get('mods', {}).get('itemList', {}).get('content', [])
        elif 'mods' in data:
            # Alternative structure
            items_list = data['mods'].get('itemList', {}).get('content', [])
        elif 'itemList' in data:
            items_list = data['itemList'].get('content', [])
        
        if items_list:
            for item in items_list:
                product = self._normalize_json_product(item, search_query)
                if product:
                    products.append(product)
        
        return products
    
    def _normalize_json_product(self, item: Dict, search_query: str) -> Optional[Dict[str, Any]]:
        """Normalize JSON product data"""
        try:
            # Extract price (convert from cents if needed)
            price_str = item.get('price', {}).get('minPrice') or item.get('prices', {}).get('salePrice', {}).get('minPrice', '0')
            try:
                price = float(str(price_str).replace('£', '').replace('$', '').replace(',', ''))
            except (ValueError, TypeError, AttributeError):
                price = 0
            
            # Extract orders
            orders_str = item.get('trade', {}).get('tradeDesc', '') or item.get('trade', '0')
            orders = self._parse_order_count(str(orders_str))
            
            # Extract rating
            rating_str = item.get('evaluation', {}).get('starRating', '0') or '0'
            try:
                rating = float(rating_str)
            except (ValueError, TypeError, AttributeError):
                rating = 0
            
            return {
                'product_name': item.get('title', {}).get('displayTitle', '') or item.get('title', ''),
                'aliexpress_id': str(item.get('productId', '') or item.get('itemId', '')),
                'supplier_cost': price,
                'estimated_retail_price': round(price * 2.5, 2) if price > 0 else 0,  # Estimate retail markup
                'order_count': orders,
                'reviews_count': item.get('evaluation', {}).get('starCount', 0),
                'rating': rating,
                'image_url': item.get('image', {}).get('imgUrl', '') or item.get('image', ''),
                'product_url': f"https://www.aliexpress.com/item/{item.get('productId', '')}.html",
                'category': search_query.title(),
                'data_source': 'aliexpress',
                'data_source_type': 'scraped',
                'is_real_data': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.debug(f"Failed to normalize JSON product: {e}")
            return None
    
    def _parse_product_card(self, card, search_query: str) -> Dict[str, Any]:
        """Parse a product card HTML element"""
        # Extract product name
        title_elem = card.select_one('[class*="title"], h1, h2, h3, [class*="name"]')
        product_name = title_elem.get_text(strip=True) if title_elem else ''
        
        # Extract price
        price_elem = card.select_one('[class*="price"], [class*="cost"]')
        price_text = price_elem.get_text(strip=True) if price_elem else '0'
        price = self._parse_price(price_text)
        
        # Extract orders
        orders_elem = card.select_one('[class*="order"], [class*="sold"]')
        orders_text = orders_elem.get_text(strip=True) if orders_elem else '0'
        orders = self._parse_order_count(orders_text)
        
        # Extract image
        img_elem = card.select_one('img')
        image_url = img_elem.get('src', '') if img_elem else ''
        if image_url.startswith('//'):
            image_url = f"https:{image_url}"
        
        # Extract product ID
        link_elem = card.select_one('a[href*="/item/"]')
        product_id = ''
        if link_elem:
            href = link_elem.get('href', '')
            id_match = re.search(r'/item/(\d+)', href)
            if id_match:
                product_id = id_match.group(1)
        
        return {
            'product_name': product_name,
            'aliexpress_id': product_id,
            'supplier_cost': price,
            'estimated_retail_price': round(price * 2.5, 2) if price > 0 else 0,
            'order_count': orders,
            'image_url': image_url,
            'category': search_query.title(),
            'data_source': 'aliexpress',
            'data_source_type': 'scraped',
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_alternative_format(self, soup: BeautifulSoup, search_query: str) -> List[Dict[str, Any]]:
        """Try alternative parsing methods for different page layouts"""
        products = []
        
        # Look for any elements with price-like content
        elements = soup.find_all(['div', 'article', 'li'], attrs={'class': True})
        
        for elem in elements:
            class_str = ' '.join(elem.get('class', []))
            
            # Check if this looks like a product element
            if any(keyword in class_str.lower() for keyword in ['product', 'item', 'card', 'result']):
                try:
                    product = self._parse_product_card(elem, search_query)
                    if product.get('product_name') and len(product['product_name']) > 5:
                        products.append(product)
                except (ValueError, TypeError, AttributeError):
                    continue
        
        return products
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        # Remove currency symbols and extract number
        clean = re.sub(r'[^\d.,]', '', price_text)
        if clean:
            try:
                # Handle comma as decimal separator
                if ',' in clean and '.' not in clean:
                    clean = clean.replace(',', '.')
                elif ',' in clean and '.' in clean:
                    clean = clean.replace(',', '')
                return float(clean)
            except (ValueError, TypeError, AttributeError):
                pass
        return 0
    
    def _parse_order_count(self, orders_text: str) -> int:
        """Parse order count from text like '10K+ sold' or '1,234 orders'"""
        orders_text = orders_text.lower()
        
        # Handle K/M suffixes
        if 'k' in orders_text:
            match = re.search(r'([\d.,]+)\s*k', orders_text)
            if match:
                num = float(match.group(1).replace(',', ''))
                return int(num * 1000)
        
        if 'm' in orders_text:
            match = re.search(r'([\d.,]+)\s*m', orders_text)
            if match:
                num = float(match.group(1).replace(',', ''))
                return int(num * 1000000)
        
        # Extract plain number
        match = re.search(r'[\d,]+', orders_text)
        if match:
            try:
                return int(match.group().replace(',', ''))
            except (ValueError, TypeError, AttributeError):
                pass
        
        return 0
    
    def parse_product(self, raw_html: Any, **kwargs) -> Dict[str, Any]:
        """Parse a single product detail page"""
        # This would be used for detailed product pages
        # For now, we primarily use search results
        return {}
    
    async def ingest_products(self, max_products: int = 50) -> DataIngestionResult:
        """
        Full ingestion pipeline: scrape, normalize, and save products.
        
        Args:
            max_products: Maximum products to ingest
            
        Returns:
            DataIngestionResult with statistics
        """
        result = DataIngestionResult(source_name=self.config.name)
        
        try:
            # Scrape products
            self.logger.info(f"Starting AliExpress ingestion (max: {max_products})")
            products = await self.scrape(max_products=max_products)
            
            result.products_fetched = len(products)
            self.logger.info(f"Fetched {result.products_fetched} products from AliExpress")
            
            if not products:
                result.errors.append("No products scraped")
                result.complete(success=False)
                return result
            
            # Save to database
            for product in products:
                try:
                    await self._save_product(product, result)
                except Exception as e:
                    result.products_failed += 1
                    self.logger.error(f"Failed to save product: {e}")
            
            result.confidence_level = "medium"  # Scraped data
            result.health_status = self._health.status
            result.complete(success=True)
            
        except Exception as e:
            result.errors.append(str(e))
            result.complete(success=False)
            self.logger.error(f"AliExpress ingestion failed: {e}")
        
        # Save health status
        await self.save_health_to_db()
        
        return result
    
    async def _save_product(self, product: Dict[str, Any], result: DataIngestionResult):
        """Save or update product in database"""
        import uuid
        
        # Check if product exists
        existing = await self.db.products.find_one({
            "$or": [
                {"aliexpress_id": product.get('aliexpress_id')},
                {"product_name": {"$regex": f"^{re.escape(product['product_name'][:50])}.*$", "$options": "i"}}
            ]
        }) if product.get('aliexpress_id') or product.get('product_name') else None
        
        if existing:
            # Update existing
            update_fields = {
                'supplier_cost': product['supplier_cost'],
                'order_count': product.get('order_count', 0),
                'aliexpress_orders': product.get('order_count', 0),
                'supplier_order_velocity': product.get('order_count', 0),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'data_source': 'aliexpress',
                'is_real_data': True
            }
            
            # Calculate confidence score
            update_fields['confidence_score'] = self._calculate_confidence(product)
            
            await self.db.products.update_one(
                {"id": existing['id']},
                {"$set": update_fields}
            )
            result.products_updated += 1
        else:
            # Create new product
            product['id'] = str(uuid.uuid4())
            product['created_at'] = datetime.now(timezone.utc).isoformat()
            product['updated_at'] = product['created_at']
            product['stores_created'] = 0
            product['exports_count'] = 0
            product['confidence_score'] = self._calculate_confidence(product)
            
            # Calculate initial scores
            product['aliexpress_orders'] = product.get('order_count', 0)
            product['supplier_order_velocity'] = product.get('order_count', 0)
            
            # Estimate other fields
            if product['supplier_cost'] > 0:
                product['estimated_margin'] = product.get('estimated_retail_price', 0) - product['supplier_cost']
            
            await self.db.products.insert_one(product)
            result.products_created += 1
    
    def _calculate_confidence(self, product: Dict[str, Any]) -> int:
        """Calculate confidence score for scraped product"""
        score = 0
        
        # Has real name
        if product.get('product_name'):
            score += 15
        
        # Has real price
        if product.get('supplier_cost', 0) > 0:
            score += 20
        
        # Has order count (strong signal)
        if product.get('order_count', 0) > 0:
            score += 25
        
        # Has image
        if product.get('image_url'):
            score += 10
        
        # Has product ID
        if product.get('aliexpress_id'):
            score += 10
        
        # Real data bonus
        if product.get('is_real_data'):
            score += 20
        
        return min(100, score)
