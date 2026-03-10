"""
Product Merger

Merges duplicate products into canonical records while preserving
source-level signals and data provenance.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SourceData:
    """Data from a specific source for a product"""
    source_name: str  # aliexpress, amazon_movers, tiktok_trends, etc.
    source_product_id: Optional[str] = None  # Original ID in source
    supplier_cost: float = 0
    estimated_retail_price: float = 0
    order_count: int = 0
    reviews_count: int = 0
    rating: float = 0
    trend_score: float = 0
    bsr_change: int = 0  # Amazon BSR change
    tiktok_views: int = 0
    engagement_rate: float = 0
    ad_count: int = 0
    confidence_score: int = 0
    last_updated: str = ""
    is_real_data: bool = False
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalProduct:
    """Canonical product record with merged data from multiple sources"""
    canonical_id: str
    product_name: str
    category: str
    image_url: str
    
    # Merged metrics (best available from sources)
    supplier_cost: float = 0
    estimated_retail_price: float = 0
    estimated_margin: float = 0
    total_orders: int = 0
    total_reviews: int = 0
    avg_rating: float = 0
    
    # Computed scores
    trend_score: float = 0
    margin_score: float = 0
    competition_score: float = 0
    market_score: float = 0
    win_score: float = 0
    success_probability: float = 0
    
    # Provenance
    contributing_sources: List[str] = field(default_factory=list)
    source_data: List[SourceData] = field(default_factory=list)
    primary_source: str = ""
    canonical_confidence: int = 0
    
    # Status
    is_canonical: bool = True
    merged_product_ids: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class ProductMerger:
    """
    Merges duplicate products into canonical records.
    
    Merge Strategy:
    - Use highest-confidence source for primary data
    - Combine metrics where meaningful (orders, reviews)
    - Keep best prices (lowest supplier, highest retail)
    - Preserve all source-level signals
    - Calculate canonical confidence from all sources
    """
    
    # Source priority for resolving conflicts
    SOURCE_PRIORITY = {
        'aliexpress': 1,    # Highest - actual supplier data
        'cj_dropshipping': 2,
        'amazon_movers': 3,
        'tiktok_trends': 4,
        'amazon_trends': 5,
        'simulated': 10,    # Lowest
    }
    
    def __init__(self, db):
        self.db = db
    
    def merge_products(
        self, 
        products: List[Dict[str, Any]],
        primary_product_id: Optional[str] = None
    ) -> CanonicalProduct:
        """
        Merge a list of duplicate products into one canonical record.
        
        Args:
            products: List of products to merge
            primary_product_id: ID of product to use as primary (optional)
            
        Returns:
            CanonicalProduct with merged data
        """
        if not products:
            raise ValueError("No products to merge")
        
        if len(products) == 1:
            # Single product - just convert to canonical format
            return self._single_to_canonical(products[0])
        
        # Sort by source priority
        sorted_products = sorted(
            products,
            key=lambda p: self.SOURCE_PRIORITY.get(p.get('data_source', 'simulated'), 10)
        )
        
        # Use specified primary or highest priority
        if primary_product_id:
            primary = next((p for p in products if p.get('id') == primary_product_id), sorted_products[0])
        else:
            primary = sorted_products[0]
        
        # Create canonical product
        canonical_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Extract source data from all products
        source_data_list = []
        contributing_sources = set()
        merged_ids = []
        
        for product in products:
            source_name = product.get('data_source', 'unknown')
            contributing_sources.add(source_name)
            merged_ids.append(product.get('id', ''))
            
            source_data = SourceData(
                source_name=source_name,
                source_product_id=self._get_source_id(product),
                supplier_cost=product.get('supplier_cost', 0),
                estimated_retail_price=product.get('estimated_retail_price', 0),
                order_count=product.get('order_count', 0) or product.get('aliexpress_orders', 0),
                reviews_count=product.get('reviews_count', 0) or product.get('amazon_reviews', 0),
                rating=product.get('rating', 0) or product.get('amazon_rating', 0),
                trend_score=product.get('trend_score', 0),
                bsr_change=product.get('amazon_bsr_change', 0),
                tiktok_views=product.get('tiktok_views', 0),
                engagement_rate=product.get('engagement_rate', 0),
                ad_count=product.get('ad_count', 0),
                confidence_score=product.get('confidence_score', 0),
                last_updated=product.get('last_updated', product.get('updated_at', '')),
                is_real_data=product.get('is_real_data', False),
                raw_data={
                    k: v for k, v in product.items() 
                    if k not in ['id', '_id', 'source_data', 'contributing_sources']
                }
            )
            source_data_list.append(source_data)
        
        # Merge metrics
        merged_supplier_cost = self._merge_supplier_cost(products)
        merged_retail_price = self._merge_retail_price(products)
        merged_orders = self._merge_orders(products)
        merged_reviews = self._merge_reviews(products)
        merged_rating = self._merge_rating(products)
        
        # Calculate canonical confidence
        canonical_confidence = self._calculate_canonical_confidence(source_data_list)
        
        canonical = CanonicalProduct(
            canonical_id=canonical_id,
            product_name=primary.get('product_name', ''),
            category=primary.get('category', ''),
            image_url=self._select_best_image(products),
            
            supplier_cost=merged_supplier_cost,
            estimated_retail_price=merged_retail_price,
            estimated_margin=merged_retail_price - merged_supplier_cost if merged_retail_price > merged_supplier_cost else 0,
            total_orders=merged_orders,
            total_reviews=merged_reviews,
            avg_rating=merged_rating,
            
            contributing_sources=list(contributing_sources),
            source_data=source_data_list,
            primary_source=primary.get('data_source', 'unknown'),
            canonical_confidence=canonical_confidence,
            
            is_canonical=True,
            merged_product_ids=merged_ids,
            created_at=now,
            updated_at=now
        )
        
        return canonical
    
    def _single_to_canonical(self, product: Dict[str, Any]) -> CanonicalProduct:
        """Convert a single product to canonical format"""
        canonical_id = product.get('canonical_id') or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        source_name = product.get('data_source', 'unknown')
        
        source_data = SourceData(
            source_name=source_name,
            source_product_id=self._get_source_id(product),
            supplier_cost=product.get('supplier_cost', 0),
            estimated_retail_price=product.get('estimated_retail_price', 0),
            order_count=product.get('order_count', 0) or product.get('aliexpress_orders', 0),
            reviews_count=product.get('reviews_count', 0) or product.get('amazon_reviews', 0),
            rating=product.get('rating', 0) or product.get('amazon_rating', 0),
            confidence_score=product.get('confidence_score', 0),
            last_updated=product.get('last_updated', product.get('updated_at', '')),
            is_real_data=product.get('is_real_data', False)
        )
        
        return CanonicalProduct(
            canonical_id=canonical_id,
            product_name=product.get('product_name', ''),
            category=product.get('category', ''),
            image_url=product.get('image_url', ''),
            
            supplier_cost=product.get('supplier_cost', 0),
            estimated_retail_price=product.get('estimated_retail_price', 0),
            estimated_margin=product.get('estimated_margin', 0),
            total_orders=source_data.order_count,
            total_reviews=source_data.reviews_count,
            avg_rating=source_data.rating,
            
            trend_score=product.get('trend_score', 0),
            margin_score=product.get('margin_score', 0),
            competition_score=product.get('competition_score', 0),
            market_score=product.get('market_score', 0),
            win_score=product.get('win_score', 0),
            success_probability=product.get('success_probability', 0),
            
            contributing_sources=[source_name],
            source_data=[source_data],
            primary_source=source_name,
            canonical_confidence=product.get('confidence_score', 0),
            
            is_canonical=True,
            merged_product_ids=[product.get('id', '')],
            created_at=product.get('created_at', now),
            updated_at=now
        )
    
    def _get_source_id(self, product: Dict[str, Any]) -> Optional[str]:
        """Get the source-specific product ID"""
        for field in ['aliexpress_id', 'amazon_asin', 'cj_product_id', 'tiktok_id']:
            if product.get(field):
                return product[field]
        return product.get('id')
    
    def _merge_supplier_cost(self, products: List[Dict[str, Any]]) -> float:
        """Merge supplier costs - use lowest non-zero value"""
        costs = [
            p.get('supplier_cost', 0) 
            for p in products 
            if p.get('supplier_cost', 0) > 0
        ]
        return min(costs) if costs else 0
    
    def _merge_retail_price(self, products: List[Dict[str, Any]]) -> float:
        """Merge retail prices - use highest for profit estimation"""
        prices = [
            p.get('estimated_retail_price', 0) 
            for p in products 
            if p.get('estimated_retail_price', 0) > 0
        ]
        return max(prices) if prices else 0
    
    def _merge_orders(self, products: List[Dict[str, Any]]) -> int:
        """Merge order counts - use highest as demand signal"""
        orders = []
        for p in products:
            order_count = (
                p.get('order_count', 0) or 
                p.get('aliexpress_orders', 0) or 
                p.get('supplier_order_velocity', 0)
            )
            if order_count > 0:
                orders.append(order_count)
        
        return max(orders) if orders else 0
    
    def _merge_reviews(self, products: List[Dict[str, Any]]) -> int:
        """Merge review counts - use highest"""
        reviews = [
            p.get('reviews_count', 0) or p.get('amazon_reviews', 0)
            for p in products
        ]
        return max(reviews) if reviews else 0
    
    def _merge_rating(self, products: List[Dict[str, Any]]) -> float:
        """Merge ratings - weighted average by review count"""
        weighted_sum = 0
        total_reviews = 0
        
        for p in products:
            rating = p.get('rating', 0) or p.get('amazon_rating', 0)
            reviews = p.get('reviews_count', 0) or p.get('amazon_reviews', 0) or 1
            
            if rating > 0:
                weighted_sum += rating * reviews
                total_reviews += reviews
        
        if total_reviews > 0:
            return round(weighted_sum / total_reviews, 1)
        return 0
    
    def _select_best_image(self, products: List[Dict[str, Any]]) -> str:
        """Select best image URL"""
        for p in sorted(
            products, 
            key=lambda x: self.SOURCE_PRIORITY.get(x.get('data_source', 'simulated'), 10)
        ):
            image_url = p.get('image_url', '')
            if image_url and image_url.startswith('http'):
                return image_url
        return ''
    
    def _calculate_canonical_confidence(self, source_data_list: List[SourceData]) -> int:
        """
        Calculate canonical confidence score based on all sources.
        
        Higher confidence when:
        - Multiple real data sources agree
        - Higher individual source confidence
        - More recent data
        """
        if not source_data_list:
            return 0
        
        # Base score from individual confidences
        confidences = [s.confidence_score for s in source_data_list if s.confidence_score > 0]
        base_score = max(confidences) if confidences else 0
        
        # Bonus for multiple sources
        real_sources = sum(1 for s in source_data_list if s.is_real_data)
        source_bonus = min(20, real_sources * 10)  # Up to 20 points for multiple sources
        
        # Bonus for source diversity
        unique_sources = len(set(s.source_name for s in source_data_list))
        diversity_bonus = min(10, unique_sources * 5)  # Up to 10 points
        
        total = base_score + source_bonus + diversity_bonus
        
        return min(100, total)
    
    def canonical_to_dict(self, canonical: CanonicalProduct) -> Dict[str, Any]:
        """Convert CanonicalProduct to dictionary for database storage"""
        return {
            'canonical_id': canonical.canonical_id,
            'product_name': canonical.product_name,
            'category': canonical.category,
            'image_url': canonical.image_url,
            
            'supplier_cost': canonical.supplier_cost,
            'estimated_retail_price': canonical.estimated_retail_price,
            'estimated_margin': canonical.estimated_margin,
            'total_orders': canonical.total_orders,
            'total_reviews': canonical.total_reviews,
            'avg_rating': canonical.avg_rating,
            
            'trend_score': canonical.trend_score,
            'margin_score': canonical.margin_score,
            'competition_score': canonical.competition_score,
            'market_score': canonical.market_score,
            'win_score': canonical.win_score,
            'success_probability': canonical.success_probability,
            
            'contributing_sources': canonical.contributing_sources,
            'source_data': [
                {
                    'source_name': s.source_name,
                    'source_product_id': s.source_product_id,
                    'supplier_cost': s.supplier_cost,
                    'estimated_retail_price': s.estimated_retail_price,
                    'order_count': s.order_count,
                    'reviews_count': s.reviews_count,
                    'rating': s.rating,
                    'trend_score': s.trend_score,
                    'bsr_change': s.bsr_change,
                    'tiktok_views': s.tiktok_views,
                    'engagement_rate': s.engagement_rate,
                    'ad_count': s.ad_count,
                    'confidence_score': s.confidence_score,
                    'last_updated': s.last_updated,
                    'is_real_data': s.is_real_data
                }
                for s in canonical.source_data
            ],
            'primary_source': canonical.primary_source,
            'canonical_confidence': canonical.canonical_confidence,
            
            'is_canonical': canonical.is_canonical,
            'merged_product_ids': canonical.merged_product_ids,
            'created_at': canonical.created_at,
            'updated_at': canonical.updated_at
        }
