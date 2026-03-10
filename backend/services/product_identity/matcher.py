"""
Product Matcher

Identifies potential duplicate products using multiple matching signals:
- Normalized title similarity
- Keyword matching
- Category similarity
- Supplier URL matching
- Image similarity (placeholder for future)
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of a product match comparison"""
    product_a_id: str
    product_b_id: str
    overall_score: float  # 0-100
    title_score: float
    keyword_score: float
    category_score: float
    url_score: float
    is_match: bool  # True if overall_score >= threshold
    match_reasons: List[str]


class ProductMatcher:
    """
    Identifies duplicate products using multiple matching signals.
    
    Match Signals:
    - Title similarity (normalized, fuzzy matching)
    - Keyword extraction and overlap
    - Category matching
    - Supplier URL comparison
    - Price range similarity
    """
    
    # Minimum score to consider a match (0-100)
    MATCH_THRESHOLD = 70
    
    # Signal weights for overall score
    WEIGHTS = {
        'title': 0.40,      # 40% - Most important
        'keywords': 0.25,   # 25% - Product keywords
        'category': 0.15,   # 15% - Category match
        'url': 0.15,        # 15% - URL match
        'price': 0.05,      # 5% - Price similarity
    }
    
    # Common words to remove during normalization
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'for', 'with', 'new', 'hot',
        'sale', 'free', 'shipping', 'fast', 'best', 'quality', 'high',
        'product', 'item', 'piece', 'pcs', 'set', 'kit', 'pack', 'lot',
        'style', 'fashion', 'portable', 'mini', 'small', 'large', 'big',
        '2024', '2025', '2026', 'newest', 'latest', 'original', 'brand'
    }
    
    def __init__(self, match_threshold: float = None):
        self.match_threshold = match_threshold or self.MATCH_THRESHOLD
    
    def find_duplicates(
        self, 
        products: List[Dict[str, Any]],
        target_product: Optional[Dict[str, Any]] = None
    ) -> List[MatchResult]:
        """
        Find duplicate products in a list.
        
        Args:
            products: List of products to check
            target_product: If provided, find duplicates of this product only
            
        Returns:
            List of MatchResult for products that match
        """
        matches = []
        
        if target_product:
            # Find duplicates of a specific product
            for product in products:
                if product.get('id') == target_product.get('id'):
                    continue
                
                result = self.compare_products(target_product, product)
                if result.is_match:
                    matches.append(result)
        else:
            # Find all duplicates (pairwise comparison)
            seen_pairs = set()
            
            for i, product_a in enumerate(products):
                for product_b in products[i + 1:]:
                    pair_key = tuple(sorted([product_a.get('id', ''), product_b.get('id', '')]))
                    if pair_key in seen_pairs:
                        continue
                    
                    seen_pairs.add(pair_key)
                    result = self.compare_products(product_a, product_b)
                    
                    if result.is_match:
                        matches.append(result)
        
        # Sort by match score descending
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches
    
    def compare_products(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> MatchResult:
        """
        Compare two products and calculate match scores.
        
        Returns:
            MatchResult with detailed scores
        """
        match_reasons = []
        
        # Calculate individual scores
        title_score = self._calculate_title_score(product_a, product_b)
        if title_score >= 80:
            match_reasons.append(f"Title match: {title_score:.0f}%")
        
        keyword_score = self._calculate_keyword_score(product_a, product_b)
        if keyword_score >= 70:
            match_reasons.append(f"Keyword match: {keyword_score:.0f}%")
        
        category_score = self._calculate_category_score(product_a, product_b)
        if category_score >= 80:
            match_reasons.append(f"Category match: {category_score:.0f}%")
        
        url_score = self._calculate_url_score(product_a, product_b)
        if url_score >= 90:
            match_reasons.append(f"URL match: {url_score:.0f}%")
        
        price_score = self._calculate_price_score(product_a, product_b)
        
        # Calculate weighted overall score
        overall_score = (
            title_score * self.WEIGHTS['title'] +
            keyword_score * self.WEIGHTS['keywords'] +
            category_score * self.WEIGHTS['category'] +
            url_score * self.WEIGHTS['url'] +
            price_score * self.WEIGHTS['price']
        )
        
        is_match = overall_score >= self.match_threshold
        
        return MatchResult(
            product_a_id=product_a.get('id', ''),
            product_b_id=product_b.get('id', ''),
            overall_score=round(overall_score, 1),
            title_score=round(title_score, 1),
            keyword_score=round(keyword_score, 1),
            category_score=round(category_score, 1),
            url_score=round(url_score, 1),
            is_match=is_match,
            match_reasons=match_reasons
        )
    
    def _calculate_title_score(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> float:
        """Calculate title similarity score"""
        title_a = self._normalize_title(product_a.get('product_name', ''))
        title_b = self._normalize_title(product_b.get('product_name', ''))
        
        if not title_a or not title_b:
            return 0
        
        # Use sequence matcher for fuzzy matching
        ratio = SequenceMatcher(None, title_a, title_b).ratio()
        
        # Also check if one contains the other (substring match)
        if title_a in title_b or title_b in title_a:
            ratio = max(ratio, 0.85)
        
        return ratio * 100
    
    def _calculate_keyword_score(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> float:
        """Calculate keyword overlap score"""
        keywords_a = self._extract_keywords(product_a)
        keywords_b = self._extract_keywords(product_b)
        
        if not keywords_a or not keywords_b:
            return 0
        
        # Calculate Jaccard similarity
        intersection = keywords_a & keywords_b
        union = keywords_a | keywords_b
        
        if not union:
            return 0
        
        jaccard = len(intersection) / len(union)
        
        return jaccard * 100
    
    def _calculate_category_score(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> float:
        """Calculate category match score"""
        cat_a = self._normalize_category(product_a.get('category', ''))
        cat_b = self._normalize_category(product_b.get('category', ''))
        
        if not cat_a or not cat_b:
            return 50  # Neutral if missing
        
        if cat_a == cat_b:
            return 100
        
        # Check for partial match or related categories
        if cat_a in cat_b or cat_b in cat_a:
            return 80
        
        # Check for word overlap
        words_a = set(cat_a.split())
        words_b = set(cat_b.split())
        overlap = words_a & words_b
        
        if overlap:
            return 60
        
        return 0
    
    def _calculate_url_score(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> float:
        """Calculate URL match score"""
        # Check various URL fields
        url_fields = ['product_url', 'supplier_url', 'aliexpress_id', 'amazon_asin', 'cj_product_id']
        
        for field in url_fields:
            val_a = product_a.get(field)
            val_b = product_b.get(field)
            
            if val_a and val_b and val_a == val_b:
                return 100
        
        # Check if URLs contain same product ID
        url_a = product_a.get('product_url', '')
        url_b = product_b.get('product_url', '')
        
        if url_a and url_b:
            # Extract product IDs from URLs
            id_pattern = r'/(\d{8,})'
            match_a = re.search(id_pattern, url_a)
            match_b = re.search(id_pattern, url_b)
            
            if match_a and match_b and match_a.group(1) == match_b.group(1):
                return 100
        
        return 0
    
    def _calculate_price_score(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> float:
        """Calculate price similarity score"""
        price_a = product_a.get('supplier_cost') or product_a.get('estimated_retail_price', 0)
        price_b = product_b.get('supplier_cost') or product_b.get('estimated_retail_price', 0)
        
        if not price_a or not price_b:
            return 50  # Neutral if missing
        
        # Calculate percentage difference
        avg_price = (price_a + price_b) / 2
        diff = abs(price_a - price_b)
        
        if avg_price == 0:
            return 50
        
        diff_percent = (diff / avg_price) * 100
        
        # Score based on difference
        if diff_percent <= 5:
            return 100
        elif diff_percent <= 15:
            return 80
        elif diff_percent <= 30:
            return 60
        elif diff_percent <= 50:
            return 40
        else:
            return 20
    
    def _normalize_title(self, title: str) -> str:
        """Normalize product title for comparison"""
        if not title:
            return ''
        
        # Convert to lowercase
        title = title.lower()
        
        # Remove special characters except spaces
        title = re.sub(r'[^\w\s]', ' ', title)
        
        # Split into words
        words = title.split()
        
        # Remove stop words
        words = [w for w in words if w not in self.STOP_WORDS and len(w) > 1]
        
        # Remove numbers-only words
        words = [w for w in words if not w.isdigit()]
        
        # Sort for order-independent comparison
        words.sort()
        
        return ' '.join(words)
    
    def _extract_keywords(self, product: Dict[str, Any]) -> Set[str]:
        """Extract keywords from product data"""
        keywords = set()
        
        # From title
        title = product.get('product_name', '')
        if title:
            normalized = self._normalize_title(title)
            keywords.update(normalized.split())
        
        # From category
        category = product.get('category', '')
        if category:
            cat_words = self._normalize_title(category).split()
            keywords.update(cat_words)
        
        # From description if available
        desc = product.get('description', '')
        if desc:
            desc_normalized = self._normalize_title(desc[:500])  # Limit description
            keywords.update(desc_normalized.split()[:20])  # Limit words
        
        return keywords
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category name"""
        if not category:
            return ''
        
        return category.lower().strip()
    
    def quick_match_check(
        self, 
        product_a: Dict[str, Any], 
        product_b: Dict[str, Any]
    ) -> bool:
        """
        Quick check if products might be duplicates (for filtering).
        
        Uses fast heuristics before full comparison.
        """
        # Same source ID
        for field in ['aliexpress_id', 'amazon_asin', 'cj_product_id']:
            val_a = product_a.get(field)
            val_b = product_b.get(field)
            if val_a and val_b and val_a == val_b:
                return True
        
        # First few words of title match
        title_a = product_a.get('product_name', '').lower()[:50]
        title_b = product_b.get('product_name', '').lower()[:50]
        
        if title_a and title_b:
            # Check first 3 significant words
            words_a = [w for w in title_a.split()[:5] if len(w) > 2]
            words_b = [w for w in title_b.split()[:5] if len(w) > 2]
            
            if words_a and words_b:
                common = set(words_a[:3]) & set(words_b[:3])
                if len(common) >= 2:
                    return True
        
        return False
