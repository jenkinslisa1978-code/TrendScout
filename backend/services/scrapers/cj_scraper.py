"""
CJ Dropshipping Scraper

Scrapes product data from CJ Dropshipping including:
- Product listings
- Supplier prices
- Product images
- Category data

Rate limited to 1 request per second with 24-hour caching.
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from . import BaseScraper, ScraperConfig, DataIngestionResult


class CJDropshippingScraper(BaseScraper):
    """
    CJ Dropshipping product scraper.
    
    Scrapes products from CJ Dropshipping's public catalog.
    """
    
    SEARCH_URL = "https://cjdropshipping.com/search.html"
    HOT_PRODUCTS_URL = "https://cjdropshipping.com/hot-selling.html"
    NEW_ARRIVALS_URL = "https://cjdropshipping.com/new-arrivals.html"
    
    # Popular categories
    CATEGORIES = {
        'electronics': 'Electronics',
        'home': 'Home & Garden',
        'fashion': 'Fashion',
        'beauty': 'Beauty & Health',
        'toys': 'Toys & Hobbies',
        'sports': 'Sports & Outdoors',
        'pets': 'Pet Products',
        'automotive': 'Automotive',
    }
    
    def __init__(self, db):
        config = ScraperConfig(
            name="cj_dropshipping",
            base_url="https://cjdropshipping.com",
            rate_limit_per_second=1.0,
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
        max_products: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape products from CJ Dropshipping.
        
        Args:
            query: Search query
            category: Category to scrape
            max_products: Maximum products to fetch
            
        Returns:
            List of scraped product data
        """
        products = []
        
        # Scrape hot selling products
        hot_products = await self._scrape_hot_products(max_products // 2)
        products.extend(hot_products)
        
        # Scrape new arrivals
        new_products = await self._scrape_new_arrivals(max_products // 4)
        products.extend(new_products)
        
        # Search for specific terms if provided
        if query:
            search_results = await self._scrape_search(query, max_products // 4)
            products.extend(search_results)
        
        return products[:max_products]
    
    async def _scrape_hot_products(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape hot selling products"""
        products = []
        
        self.logger.info("Scraping CJ Dropshipping hot products")
        
        html, success = await self.fetch_with_retry(self.HOT_PRODUCTS_URL)
        
        if not success or not html:
            self.logger.warning("Failed to fetch CJ hot products")
            return products
        
        try:
            products = self._parse_product_listing(html, 'Hot Selling')
        except Exception as e:
            self.logger.error(f"Error parsing CJ hot products: {e}")
        
        return products[:limit]
    
    async def _scrape_new_arrivals(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape new arrivals"""
        products = []
        
        self.logger.info("Scraping CJ Dropshipping new arrivals")
        
        html, success = await self.fetch_with_retry(self.NEW_ARRIVALS_URL)
        
        if not success or not html:
            self.logger.warning("Failed to fetch CJ new arrivals")
            return products
        
        try:
            products = self._parse_product_listing(html, 'New Arrivals')
        except Exception as e:
            self.logger.error(f"Error parsing CJ new arrivals: {e}")
        
        return products[:limit]
    
    async def _scrape_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape search results"""
        products = []
        
        url = f"{self.SEARCH_URL}?key={query.replace(' ', '+')}"
        
        self.logger.info(f"Scraping CJ Dropshipping search: {query}")
        
        html, success = await self.fetch_with_retry(url)
        
        if not success or not html:
            self.logger.warning(f"Failed to fetch CJ search for: {query}")
            return products
        
        try:
            products = self._parse_product_listing(html, query.title())
        except Exception as e:
            self.logger.error(f"Error parsing CJ search results: {e}")
        
        return products[:limit]
    
    def _parse_product_listing(self, html: str, source_type: str) -> List[Dict[str, Any]]:
        """Parse CJ product listing page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try JSON data first
        json_data = self._extract_json_data(html)
        if json_data:
            products = self._parse_json_products(json_data, source_type)
            if products:
                return products
        
        # Parse HTML product cards
        product_selectors = [
            '.product-item',
            '.goods-item',
            '[class*="product"]',
            '[class*="item"]',
        ]
        
        for selector in product_selectors:
            items = soup.select(selector)
            for item in items:
                try:
                    product = self._parse_product_card(item, source_type)
                    if product and product.get('product_name') and len(product['product_name']) > 5:
                        products.append(product)
                except Exception as e:
                    self.logger.debug(f"Failed to parse CJ product card: {e}")
        
        # Deduplicate
        seen = set()
        unique = []
        for p in products:
            key = p['product_name'][:50].lower()
            if key not in seen:
                seen.add(key)
                unique.append(p)
        
        return unique
    
    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Extract JSON data from page"""
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'var\s+productData\s*=\s*({.+?});',
            r'"products":\s*(\[.+?\])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_json_products(self, data: Dict, source_type: str) -> List[Dict[str, Any]]:
        """Parse products from JSON data"""
        products = []
        
        product_list = None
        
        if isinstance(data, list):
            product_list = data
        elif 'products' in data:
            product_list = data['products']
        elif 'items' in data:
            product_list = data['items']
        
        if product_list:
            for item in product_list[:50]:
                product = self._normalize_json_product(item, source_type)
                if product:
                    products.append(product)
        
        return products
    
    def _normalize_json_product(self, item: Dict, source_type: str) -> Optional[Dict[str, Any]]:
        """Normalize JSON product data"""
        try:
            # Extract price
            price = 0
            for key in ['price', 'sellPrice', 'cost']:
                if key in item:
                    try:
                        price = float(item[key])
                        break
                    except (ValueError, TypeError, AttributeError):
                        continue
            
            return {
                'product_name': item.get('productName', item.get('name', '')),
                'cj_product_id': str(item.get('productId', item.get('id', ''))),
                'category': item.get('category', item.get('categoryName', source_type)),
                'supplier_cost': price,
                'estimated_retail_price': round(price * 2.5, 2) if price > 0 else 0,
                'image_url': item.get('image', item.get('imageUrl', '')),
                'product_url': item.get('url', item.get('productUrl', '')),
                'data_source': 'cj_dropshipping',
                'data_source_type': 'scraped',
                'cj_source_type': source_type,
                'is_real_data': True,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.logger.debug(f"Failed to normalize CJ JSON product: {e}")
            return None
    
    def _parse_product_card(self, card, source_type: str) -> Optional[Dict[str, Any]]:
        """Parse a product card HTML element"""
        # Extract product name
        title_selectors = [
            '.product-name',
            '.goods-name',
            '[class*="title"]',
            'h3', 'h4',
            'a.name',
        ]
        
        product_name = ''
        for selector in title_selectors:
            elem = card.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 5:
                    product_name = text
                    break
        
        if not product_name:
            return None
        
        # Extract price
        price = 0
        price_selectors = [
            '.price',
            '[class*="price"]',
            '.cost',
        ]
        
        for selector in price_selectors:
            elem = card.select_one(selector)
            if elem:
                price = self._parse_price(elem.get_text(strip=True))
                if price > 0:
                    break
        
        # Extract image
        image_url = ''
        img_elem = card.select_one('img')
        if img_elem:
            image_url = img_elem.get('src', '') or img_elem.get('data-src', '')
            if image_url.startswith('//'):
                image_url = f"https:{image_url}"
        
        # Extract product ID from link
        product_id = ''
        link_elem = card.select_one('a[href*="product"]')
        if link_elem:
            href = link_elem.get('href', '')
            id_match = re.search(r'/product/(\d+)', href)
            if id_match:
                product_id = id_match.group(1)
        
        return {
            'product_name': product_name[:200],
            'cj_product_id': product_id,
            'category': source_type,
            'supplier_cost': price,
            'estimated_retail_price': round(price * 2.5, 2) if price > 0 else 0,
            'image_url': image_url,
            'data_source': 'cj_dropshipping',
            'data_source_type': 'scraped',
            'cj_source_type': source_type,
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        if not price_text:
            return 0
        
        clean = re.sub(r'[^\d.,]', '', price_text)
        if clean:
            try:
                if ',' in clean and '.' not in clean:
                    clean = clean.replace(',', '.')
                elif ',' in clean and '.' in clean:
                    clean = clean.replace(',', '')
                return float(clean)
            except (ValueError, TypeError, AttributeError):
                pass
        return 0
    
    def parse_product(self, raw_html: Any, **kwargs) -> Dict[str, Any]:
        """Parse a single product page"""
        return {}
    
    async def ingest_products(self, max_products: int = 30) -> DataIngestionResult:
        """
        Full ingestion pipeline.
        
        Args:
            max_products: Maximum products to ingest
            
        Returns:
            DataIngestionResult with statistics
        """
        result = DataIngestionResult(source_name=self.config.name)
        
        try:
            self.logger.info(f"Starting CJ Dropshipping ingestion (max: {max_products})")
            products = await self.scrape(max_products=max_products)
            
            result.products_fetched = len(products)
            self.logger.info(f"Fetched {result.products_fetched} products from CJ Dropshipping")
            
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
            
            result.confidence_level = "medium"
            result.health_status = self._health.status
            result.complete(success=True)
            
        except Exception as e:
            result.errors.append(str(e))
            result.complete(success=False)
            self.logger.error(f"CJ Dropshipping ingestion failed: {e}")
        
        await self.save_health_to_db()
        
        return result
    
    async def _save_product(self, product: Dict[str, Any], result: DataIngestionResult):
        """Save or update product in database"""
        import uuid
        
        # Check for existing product
        existing = None
        if product.get('cj_product_id'):
            existing = await self.db.products.find_one({"cj_product_id": product['cj_product_id']})
        
        if not existing:
            existing = await self.db.products.find_one({
                "product_name": {"$regex": f"^{re.escape(product['product_name'][:40])}.*$", "$options": "i"}
            })
        
        if existing:
            # Update existing
            update_fields = {
                'cj_product_id': product.get('cj_product_id') or existing.get('cj_product_id'),
                'supplier_cost': product.get('supplier_cost', 0) or existing.get('supplier_cost', 0),
                'cj_source_type': product.get('cj_source_type'),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'is_real_data': True
            }
            
            update_fields['confidence_score'] = self._calculate_confidence(product, existing)
            
            await self.db.products.update_one(
                {"id": existing['id']},
                {"$set": update_fields}
            )
            result.products_updated += 1
        else:
            # Create new
            product['id'] = str(uuid.uuid4())
            product['created_at'] = datetime.now(timezone.utc).isoformat()
            product['updated_at'] = product['created_at']
            product['stores_created'] = 0
            product['exports_count'] = 0
            product['confidence_score'] = self._calculate_confidence(product)
            
            if product.get('supplier_cost', 0) > 0 and product.get('estimated_retail_price', 0) > 0:
                product['estimated_margin'] = product['estimated_retail_price'] - product['supplier_cost']
            
            await self.db.products.insert_one(product)
            result.products_created += 1
    
    def _calculate_confidence(self, product: Dict[str, Any], existing: Dict[str, Any] = None) -> int:
        """Calculate confidence score"""
        score = 0
        
        if product.get('product_name'):
            score += 15
        
        if product.get('cj_product_id'):
            score += 15
        
        if product.get('supplier_cost', 0) > 0:
            score += 20
        
        if product.get('image_url'):
            score += 10
        
        if product.get('is_real_data'):
            score += 15
        
        # Bonus if from hot selling
        if product.get('cj_source_type') == 'Hot Selling':
            score += 15
        
        return min(100, score)
