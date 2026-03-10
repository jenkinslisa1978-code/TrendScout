"""
Amazon Movers & Shakers Scraper

Scrapes trending product data from Amazon's Movers & Shakers pages:
- Best Seller Rank changes
- Product names and categories
- Prices
- Review counts and ratings

Rate limited to 1 request per second with 24-hour caching.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from . import BaseScraper, ScraperConfig, DataIngestionResult


class AmazonMoversScraper(BaseScraper):
    """
    Amazon Movers & Shakers scraper.
    
    Scrapes products that are rapidly climbing the bestseller charts,
    indicating strong demand signals.
    """
    
    # Amazon UK Movers & Shakers URLs by category
    MOVERS_BASE_URL = "https://www.amazon.co.uk/gp/movers-and-shakers"
    
    CATEGORY_URLS = {
        'all': '/gp/movers-and-shakers',
        'home_kitchen': '/gp/movers-and-shakers/kitchen',
        'electronics': '/gp/movers-and-shakers/electronics',
        'beauty': '/gp/movers-and-shakers/beauty',
        'health': '/gp/movers-and-shakers/drugstore',
        'sports': '/gp/movers-and-shakers/sports',
        'garden': '/gp/movers-and-shakers/outdoors',
        'pet_supplies': '/gp/movers-and-shakers/pet-supplies',
        'toys': '/gp/movers-and-shakers/toys',
        'office': '/gp/movers-and-shakers/office-products',
    }
    
    def __init__(self, db):
        config = ScraperConfig(
            name="amazon_movers",
            base_url="https://www.amazon.co.uk",
            rate_limit_per_second=0.5,  # Slower rate for Amazon
            cache_ttl_hours=24,
            retry_attempts=3,
            timeout_seconds=45,
            enabled=True
        )
        super().__init__(db, config)
    
    async def scrape(
        self,
        category: Optional[str] = None,
        max_products: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape products from Amazon Movers & Shakers.
        
        Args:
            category: Specific category to scrape (if None, scrapes multiple)
            max_products: Maximum products to fetch
            
        Returns:
            List of scraped product data
        """
        products = []
        
        if category and category in self.CATEGORY_URLS:
            # Scrape specific category
            cat_products = await self._scrape_category(category, max_products)
            products.extend(cat_products)
        else:
            # Scrape main movers page and top categories
            main_products = await self._scrape_category('all', max_products // 3)
            products.extend(main_products)
            
            # Add from specific categories
            priority_categories = ['electronics', 'home_kitchen', 'beauty', 'health']
            products_per_cat = max(5, (max_products - len(products)) // len(priority_categories))
            
            for cat in priority_categories:
                if len(products) >= max_products:
                    break
                cat_products = await self._scrape_category(cat, products_per_cat)
                products.extend(cat_products)
        
        return products[:max_products]
    
    async def _scrape_category(self, category: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape products from a specific category"""
        products = []
        
        url_path = self.CATEGORY_URLS.get(category, self.CATEGORY_URLS['all'])
        url = f"{self.config.base_url}{url_path}"
        
        self.logger.info(f"Scraping Amazon Movers & Shakers: {category}")
        
        html, success = await self.fetch_with_retry(url)
        
        if not success or not html:
            self.logger.warning(f"Failed to fetch Amazon Movers for: {category}")
            return products
        
        try:
            products = self._parse_movers_page(html, category)
        except Exception as e:
            self.logger.error(f"Error parsing Amazon Movers page: {e}")
        
        return products[:limit]
    
    def _parse_movers_page(self, html: str, category: str) -> List[Dict[str, Any]]:
        """Parse Amazon Movers & Shakers page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product items
        item_selectors = [
            '[data-asin]',
            '.zg-item-immersion',
            '.zg-bdg-item',
            '[class*="a-carousel-card"]',
            '.p13n-sc-uncoverable-faceout',
            '.a-section.a-spacing-none'
        ]
        
        for selector in item_selectors:
            items = soup.select(selector)
            for item in items:
                try:
                    product = self._parse_product_item(item, category)
                    if product and product.get('product_name') and len(product['product_name']) > 5:
                        products.append(product)
                except Exception as e:
                    self.logger.debug(f"Failed to parse product item: {e}")
        
        # Deduplicate by name
        seen_names = set()
        unique_products = []
        for p in products:
            name_key = p['product_name'][:50].lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_products.append(p)
        
        return unique_products
    
    def _parse_product_item(self, item, category: str) -> Optional[Dict[str, Any]]:
        """Parse a single product item"""
        # Extract ASIN
        asin = item.get('data-asin', '')
        
        # Extract product name
        title_selectors = [
            '.p13n-sc-truncate',
            '.p13n-sc-truncate-desktop-type2',
            '[class*="a-link-normal"] span',
            '.a-size-base',
            'a.a-link-normal',
        ]
        
        product_name = ''
        for selector in title_selectors:
            elem = item.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 10 and not text.startswith('£'):
                    product_name = text
                    break
        
        if not product_name:
            return None
        
        # Extract price
        price = 0
        price_selectors = [
            '.p13n-sc-price',
            '.a-price .a-offscreen',
            '[class*="a-price"]',
            '.a-color-price',
        ]
        
        for selector in price_selectors:
            elem = item.select_one(selector)
            if elem:
                price = self._parse_price(elem.get_text(strip=True))
                if price > 0:
                    break
        
        # Extract BSR change (rank movement)
        bsr_change = 0
        rank_selectors = [
            '.zg-bdg-text',
            '[class*="a-badge-text"]',
            '.a-icon-alt',
        ]
        
        for selector in rank_selectors:
            elem = item.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if '%' in text:
                    bsr_change = self._parse_percentage(text)
                    break
        
        # Extract rating
        rating = 0
        rating_elem = item.select_one('[class*="a-icon-star"], .a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            match = re.search(r'(\d+\.?\d*)\s*out of\s*5', rating_text)
            if match:
                rating = float(match.group(1))
        
        # Extract reviews count
        reviews = 0
        reviews_elem = item.select_one('[class*="a-size-small"]:has([href*="customerReviews"])')
        if reviews_elem:
            reviews = self._parse_number(reviews_elem.get_text(strip=True))
        
        # Extract image
        image_url = ''
        img_elem = item.select_one('img')
        if img_elem:
            image_url = img_elem.get('src', '') or img_elem.get('data-src', '')
        
        # Calculate estimated metrics
        category_name = category.replace('_', ' ').title()
        if category == 'all':
            category_name = 'General'
        
        return {
            'product_name': product_name[:200],  # Truncate long names
            'amazon_asin': asin,
            'category': category_name,
            'supplier_cost': round(price * 0.4, 2) if price > 0 else 0,  # Estimate supplier cost
            'estimated_retail_price': price,
            'amazon_bsr_change': bsr_change,
            'amazon_rating': rating,
            'amazon_reviews': reviews,
            'image_url': image_url,
            'data_source': 'amazon_movers',
            'data_source_type': 'scraped',
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text"""
        if not price_text:
            return 0
        
        # Remove currency symbols and extract number
        clean = re.sub(r'[^\d.,]', '', price_text)
        if clean:
            try:
                # Handle different decimal separators
                if ',' in clean and '.' not in clean:
                    clean = clean.replace(',', '.')
                elif ',' in clean and '.' in clean:
                    clean = clean.replace(',', '')
                return float(clean)
            except (ValueError, TypeError, AttributeError):
                pass
        return 0
    
    def _parse_percentage(self, text: str) -> int:
        """Parse percentage change from text like '+125%' or '↑ 125%'"""
        match = re.search(r'(\d+)\s*%', text)
        if match:
            return int(match.group(1))
        return 0
    
    def _parse_number(self, text: str) -> int:
        """Parse number from text, handling K/M suffixes"""
        text = text.upper()
        
        if 'K' in text:
            match = re.search(r'([\d.]+)\s*K', text)
            if match:
                return int(float(match.group(1)) * 1000)
        
        if 'M' in text:
            match = re.search(r'([\d.]+)\s*M', text)
            if match:
                return int(float(match.group(1)) * 1000000)
        
        match = re.search(r'[\d,]+', text)
        if match:
            try:
                return int(match.group().replace(',', ''))
            except (ValueError, TypeError, AttributeError):
                pass
        
        return 0
    
    def parse_product(self, raw_html: Any, **kwargs) -> Dict[str, Any]:
        """Parse a single product (not used for Movers pages)"""
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
            self.logger.info(f"Starting Amazon Movers ingestion (max: {max_products})")
            products = await self.scrape(max_products=max_products)
            
            result.products_fetched = len(products)
            self.logger.info(f"Fetched {result.products_fetched} products from Amazon Movers")
            
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
            self.logger.error(f"Amazon Movers ingestion failed: {e}")
        
        await self.save_health_to_db()
        
        return result
    
    async def _save_product(self, product: Dict[str, Any], result: DataIngestionResult):
        """Save or update product in database"""
        import uuid
        
        # Check if product exists by ASIN or similar name
        existing = None
        if product.get('amazon_asin'):
            existing = await self.db.products.find_one({"amazon_asin": product['amazon_asin']})
        
        if not existing:
            # Try matching by name
            existing = await self.db.products.find_one({
                "product_name": {"$regex": f"^{re.escape(product['product_name'][:40])}.*$", "$options": "i"}
            })
        
        if existing:
            # Update existing product with Amazon data
            update_fields = {
                'amazon_asin': product.get('amazon_asin') or existing.get('amazon_asin'),
                'amazon_bsr_change': product.get('amazon_bsr_change', 0),
                'amazon_rating': product.get('amazon_rating', 0),
                'amazon_reviews': product.get('amazon_reviews', 0),
                'estimated_retail_price': product.get('estimated_retail_price') or existing.get('estimated_retail_price', 0),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'is_real_data': True
            }
            
            # Update supplier cost if we have a better estimate
            if product.get('supplier_cost', 0) > 0 and existing.get('supplier_cost', 0) == 0:
                update_fields['supplier_cost'] = product['supplier_cost']
            
            # Recalculate confidence
            update_fields['confidence_score'] = self._calculate_confidence(product, existing)
            
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
            
            # Estimate margin
            if product.get('supplier_cost', 0) > 0 and product.get('estimated_retail_price', 0) > 0:
                product['estimated_margin'] = product['estimated_retail_price'] - product['supplier_cost']
            
            await self.db.products.insert_one(product)
            result.products_created += 1
    
    def _calculate_confidence(self, product: Dict[str, Any], existing: Dict[str, Any] = None) -> int:
        """Calculate confidence score"""
        score = 0
        
        # Real product name
        if product.get('product_name'):
            score += 15
        
        # Has ASIN (verified Amazon product)
        if product.get('amazon_asin'):
            score += 15
        
        # Has price
        if product.get('estimated_retail_price', 0) > 0:
            score += 15
        
        # Has BSR change (trending signal)
        if product.get('amazon_bsr_change', 0) > 0:
            score += 20
        
        # Has reviews
        if product.get('amazon_reviews', 0) > 0:
            score += 15
        
        # Has image
        if product.get('image_url'):
            score += 10
        
        # Real data bonus
        if product.get('is_real_data'):
            score += 10
        
        return min(100, score)
