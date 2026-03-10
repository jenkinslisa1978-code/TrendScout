"""
TikTok Creative Center Trend Scraper

Scrapes trending product data from TikTok Creative Center including:
- Trending hashtags
- Popular products
- Engagement metrics
- Trend velocity signals

Rate limited to 1 request per second with 24-hour caching.
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from . import BaseScraper, ScraperConfig, DataIngestionResult


class TikTokTrendsScraper(BaseScraper):
    """
    TikTok Creative Center trends scraper.
    
    Scrapes publicly available trend data including:
    - Trending hashtags
    - Product trends
    - Engagement metrics
    """
    
    # TikTok Creative Center URLs
    TRENDS_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
    PRODUCTS_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/product/pc/en"
    
    # Popular product-related hashtags to monitor
    TRENDING_HASHTAGS = [
        "tiktokmademebuyit",
        "amazonfinds",
        "musthave",
        "viralproducts",
        "productreview",
        "homehacks",
        "kitchengadgets",
        "beautyhacks",
        "techgadgets",
        "giftideas",
        "aliexpressfinds",
        "shopwithme"
    ]
    
    def __init__(self, db):
        config = ScraperConfig(
            name="tiktok_trends",
            base_url="https://ads.tiktok.com",
            rate_limit_per_second=0.5,  # Slower rate for TikTok
            cache_ttl_hours=24,
            retry_attempts=3,
            timeout_seconds=45,
            enabled=True
        )
        super().__init__(db, config)
    
    async def scrape(
        self,
        hashtag: Optional[str] = None,
        region: str = "GB",
        max_items: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape trending data from TikTok Creative Center.
        
        Args:
            hashtag: Specific hashtag to scrape (if None, uses trending hashtags)
            region: Region code (GB, US, etc.)
            max_items: Maximum items to fetch
            
        Returns:
            List of trend data
        """
        trends = []
        
        # Scrape trending hashtags first
        hashtag_trends = await self._scrape_trending_hashtags(region)
        trends.extend(hashtag_trends)
        
        # Scrape product trends
        product_trends = await self._scrape_product_trends(region)
        trends.extend(product_trends)
        
        # Scrape specific hashtags
        if not hashtag:
            for tag in self.TRENDING_HASHTAGS[:5]:  # Limit hashtags per run
                tag_data = await self._scrape_hashtag(tag, region)
                if tag_data:
                    trends.append(tag_data)
        else:
            tag_data = await self._scrape_hashtag(hashtag, region)
            if tag_data:
                trends.append(tag_data)
        
        return trends[:max_items]
    
    async def _scrape_trending_hashtags(self, region: str) -> List[Dict[str, Any]]:
        """Scrape trending hashtags from Creative Center"""
        trends = []
        
        self.logger.info("Scraping TikTok trending hashtags")
        
        html, success = await self.fetch_with_retry(self.TRENDS_URL)
        
        if not success or not html:
            self.logger.warning("Failed to fetch TikTok trending hashtags")
            return trends
        
        try:
            trends = self._parse_hashtag_trends(html)
        except Exception as e:
            self.logger.error(f"Error parsing TikTok hashtag trends: {e}")
        
        return trends
    
    async def _scrape_product_trends(self, region: str) -> List[Dict[str, Any]]:
        """Scrape trending products from Creative Center"""
        trends = []
        
        self.logger.info("Scraping TikTok product trends")
        
        html, success = await self.fetch_with_retry(self.PRODUCTS_URL)
        
        if not success or not html:
            self.logger.warning("Failed to fetch TikTok product trends")
            return trends
        
        try:
            trends = self._parse_product_trends(html)
        except Exception as e:
            self.logger.error(f"Error parsing TikTok product trends: {e}")
        
        return trends
    
    async def _scrape_hashtag(self, hashtag: str, region: str) -> Optional[Dict[str, Any]]:
        """Scrape data for a specific hashtag"""
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        html, success = await self.fetch_with_retry(url)
        
        if not success or not html:
            return None
        
        return self._parse_hashtag_page(html, hashtag)
    
    def _parse_hashtag_trends(self, html: str) -> List[Dict[str, Any]]:
        """Parse trending hashtags page"""
        trends = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to extract JSON data from page
        json_data = self._extract_json_data(html)
        if json_data:
            trends = self._parse_json_hashtags(json_data)
            if trends:
                return trends
        
        # Parse HTML elements
        hashtag_elements = soup.select('[class*="hashtag"], [class*="trend"], [data-hashtag]')
        
        for elem in hashtag_elements:
            try:
                trend = self._parse_hashtag_element(elem)
                if trend:
                    trends.append(trend)
            except Exception as e:
                self.logger.debug(f"Failed to parse hashtag element: {e}")
        
        return trends
    
    def _parse_product_trends(self, html: str) -> List[Dict[str, Any]]:
        """Parse trending products page"""
        trends = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to extract JSON data
        json_data = self._extract_json_data(html)
        if json_data:
            trends = self._parse_json_products(json_data)
            if trends:
                return trends
        
        # Parse product elements
        product_elements = soup.select('[class*="product"], [class*="item"], [data-product]')
        
        for elem in product_elements:
            try:
                product = self._parse_product_element(elem)
                if product:
                    trends.append(product)
            except Exception as e:
                self.logger.debug(f"Failed to parse product element: {e}")
        
        return trends
    
    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """Extract JSON data from page scripts"""
        patterns = [
            r'window\.__INIT_PROPS__\s*=\s*({.+?});',
            r'window\.__DATA__\s*=\s*({.+?});',
            r'"pageProps":\s*({.+?})\s*,\s*"_',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_json_hashtags(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse hashtags from JSON data"""
        trends = []
        
        # Navigate possible data structures
        hashtags_list = None
        
        if 'hashtags' in data:
            hashtags_list = data['hashtags']
        elif 'trendingList' in data:
            hashtags_list = data['trendingList']
        elif 'data' in data:
            hashtags_list = data['data'].get('hashtags', [])
        
        if hashtags_list:
            for item in hashtags_list[:20]:
                trend = {
                    'hashtag': item.get('name', item.get('hashtag', '')),
                    'views': self._parse_views(item.get('views', item.get('viewCount', 0))),
                    'posts': item.get('posts', item.get('postCount', 0)),
                    'trend_score': item.get('trendScore', 0),
                    'growth_rate': item.get('growthRate', 0),
                    'data_source': 'tiktok_trends',
                    'data_type': 'hashtag',
                    'is_real_data': True,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                if trend['hashtag']:
                    trends.append(trend)
        
        return trends
    
    def _parse_json_products(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse products from JSON data"""
        products = []
        
        products_list = None
        
        if 'products' in data:
            products_list = data['products']
        elif 'trendingProducts' in data:
            products_list = data['trendingProducts']
        
        if products_list:
            for item in products_list[:20]:
                product = {
                    'product_name': item.get('name', item.get('productName', '')),
                    'category': item.get('category', 'General'),
                    'tiktok_views': self._parse_views(item.get('views', item.get('totalViews', 0))),
                    'engagement_rate': item.get('engagementRate', 0),
                    'growth_rate': item.get('growthRate', 0),
                    'ad_count': item.get('adCount', 0),
                    'trend_score': item.get('trendScore', 0),
                    'image_url': item.get('image', item.get('coverImage', '')),
                    'data_source': 'tiktok_trends',
                    'data_type': 'product',
                    'is_real_data': True,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                if product['product_name']:
                    products.append(product)
        
        return products
    
    def _parse_hashtag_element(self, elem) -> Optional[Dict[str, Any]]:
        """Parse a hashtag element from HTML"""
        # Extract hashtag name
        name_elem = elem.select_one('[class*="name"], h3, h4, span')
        name = name_elem.get_text(strip=True) if name_elem else ''
        
        if not name or len(name) < 2:
            return None
        
        # Remove # if present
        name = name.lstrip('#')
        
        # Extract view count
        views_elem = elem.select_one('[class*="view"], [class*="count"]')
        views_text = views_elem.get_text(strip=True) if views_elem else '0'
        views = self._parse_views(views_text)
        
        return {
            'hashtag': name,
            'views': views,
            'data_source': 'tiktok_trends',
            'data_type': 'hashtag',
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_product_element(self, elem) -> Optional[Dict[str, Any]]:
        """Parse a product element from HTML"""
        # Extract product name
        name_elem = elem.select_one('[class*="name"], [class*="title"], h3, h4')
        name = name_elem.get_text(strip=True) if name_elem else ''
        
        if not name or len(name) < 3:
            return None
        
        # Extract image
        img_elem = elem.select_one('img')
        image_url = img_elem.get('src', '') if img_elem else ''
        if image_url.startswith('//'):
            image_url = f"https:{image_url}"
        
        # Extract view count
        views_elem = elem.select_one('[class*="view"], [class*="count"]')
        views_text = views_elem.get_text(strip=True) if views_elem else '0'
        views = self._parse_views(views_text)
        
        return {
            'product_name': name,
            'tiktok_views': views,
            'image_url': image_url,
            'data_source': 'tiktok_trends',
            'data_type': 'product',
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_hashtag_page(self, html: str, hashtag: str) -> Optional[Dict[str, Any]]:
        """Parse a specific hashtag page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract view count
        views = 0
        views_patterns = [
            r'(\d+(?:\.\d+)?[KMB]?)\s*views',
            r'Views:\s*(\d+(?:\.\d+)?[KMB]?)',
        ]
        
        for pattern in views_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                views = self._parse_views(match.group(1))
                break
        
        # Try to find video count
        videos = 0
        videos_elem = soup.select_one('[class*="video-count"], [data-videos]')
        if videos_elem:
            videos = self._parse_views(videos_elem.get_text(strip=True))
        
        return {
            'hashtag': hashtag,
            'views': views,
            'video_count': videos,
            'data_source': 'tiktok_trends',
            'data_type': 'hashtag_detail',
            'is_real_data': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _parse_views(self, views_input) -> int:
        """Parse view count from text or number"""
        if isinstance(views_input, (int, float)):
            return int(views_input)
        
        views_text = str(views_input).upper().strip()
        
        # Handle K/M/B suffixes
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, mult in multipliers.items():
            if suffix in views_text:
                match = re.search(r'([\d.]+)', views_text)
                if match:
                    try:
                        return int(float(match.group(1)) * mult)
                    except (ValueError, TypeError, AttributeError):
                        pass
        
        # Plain number
        match = re.search(r'[\d,]+', views_text)
        if match:
            try:
                return int(match.group().replace(',', ''))
            except (ValueError, TypeError, AttributeError):
                pass
        
        return 0
    
    def parse_product(self, raw_html: Any, **kwargs) -> Dict[str, Any]:
        """Parse a single product/trend element"""
        return {}
    
    async def ingest_trends(self, max_items: int = 30) -> DataIngestionResult:
        """
        Full ingestion pipeline: scrape, normalize, and save trend data.
        
        Args:
            max_items: Maximum items to ingest
            
        Returns:
            DataIngestionResult with statistics
        """
        result = DataIngestionResult(source_name=self.config.name)
        
        try:
            self.logger.info(f"Starting TikTok trends ingestion (max: {max_items})")
            trends = await self.scrape(max_items=max_items)
            
            result.products_fetched = len(trends)
            self.logger.info(f"Fetched {result.products_fetched} trend items from TikTok")
            
            if not trends:
                result.errors.append("No trends scraped")
                result.complete(success=False)
                return result
            
            # Process and save trends
            for trend in trends:
                try:
                    await self._process_trend(trend, result)
                except Exception as e:
                    result.products_failed += 1
                    self.logger.error(f"Failed to process trend: {e}")
            
            result.confidence_level = "medium"
            result.health_status = self._health.status
            result.complete(success=True)
            
        except Exception as e:
            result.errors.append(str(e))
            result.complete(success=False)
            self.logger.error(f"TikTok trends ingestion failed: {e}")
        
        await self.save_health_to_db()
        
        return result
    
    async def _process_trend(self, trend: Dict[str, Any], result: DataIngestionResult):
        """Process and save a trend item"""
        import uuid
        
        if trend.get('data_type') == 'hashtag':
            # Save hashtag data for reference
            await self.db.tiktok_hashtags.update_one(
                {"hashtag": trend['hashtag']},
                {
                    "$set": {
                        **trend,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
            result.products_updated += 1
            
        elif trend.get('data_type') == 'product':
            # Try to match with existing product or create signal
            existing = await self.db.products.find_one({
                "product_name": {"$regex": f".*{trend['product_name'][:30]}.*", "$options": "i"}
            })
            
            if existing:
                # Update with TikTok signals
                await self.db.products.update_one(
                    {"id": existing['id']},
                    {
                        "$set": {
                            "tiktok_views": trend.get('tiktok_views', 0),
                            "tiktok_engagement_rate": trend.get('engagement_rate', 0),
                            "tiktok_growth_rate": trend.get('growth_rate', 0),
                            "tiktok_trend_score": trend.get('trend_score', 0),
                            "last_updated": datetime.now(timezone.utc).isoformat(),
                            "is_real_data": True
                        }
                    }
                )
                result.products_updated += 1
            else:
                # Create new product from TikTok trend
                product = {
                    'id': str(uuid.uuid4()),
                    'product_name': trend['product_name'],
                    'category': trend.get('category', 'Trending'),
                    'tiktok_views': trend.get('tiktok_views', 0),
                    'engagement_rate': trend.get('engagement_rate', 0),
                    'tiktok_growth_rate': trend.get('growth_rate', 0),
                    'ad_count': trend.get('ad_count', 0),
                    'image_url': trend.get('image_url', ''),
                    'data_source': 'tiktok_trends',
                    'is_real_data': True,
                    'confidence_score': 50,  # Medium confidence for trend-only data
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'stores_created': 0,
                    'exports_count': 0
                }
                await self.db.products.insert_one(product)
                result.products_created += 1
