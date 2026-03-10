"""
Product Identity Service

Main service for product deduplication and canonical record management.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass

from .matcher import ProductMatcher, MatchResult
from .merger import ProductMerger, CanonicalProduct

logger = logging.getLogger(__name__)


@dataclass
class DeduplicationResult:
    """Result of a deduplication run"""
    started_at: str
    completed_at: str
    duration_seconds: float
    total_products_processed: int
    duplicate_groups_found: int
    products_merged: int
    canonical_products_created: int
    canonical_products_updated: int
    errors: List[str]
    success: bool


class ProductIdentityService:
    """
    Main service for product identity and deduplication.
    
    Features:
    - Find duplicate products across all sources
    - Merge duplicates into canonical records
    - Preserve source-level data provenance
    - Recompute scores after merging
    - Update reports to use canonical products
    """
    
    def __init__(self, db, match_threshold: float = 70):
        self.db = db
        self.matcher = ProductMatcher(match_threshold=match_threshold)
        self.merger = ProductMerger(db)
    
    async def run_deduplication(
        self,
        batch_size: int = 100,
        dry_run: bool = False
    ) -> DeduplicationResult:
        """
        Run full deduplication process on all products.
        
        Args:
            batch_size: Number of products to process per batch
            dry_run: If True, don't actually merge (just report)
            
        Returns:
            DeduplicationResult with statistics
        """
        started_at = datetime.now(timezone.utc)
        errors = []
        duplicate_groups = []
        
        logger.info(f"Starting deduplication (dry_run={dry_run})")
        
        # Get all products
        cursor = self.db.products.find(
            {"is_canonical": {"$ne": False}},  # Exclude already-merged
            {"_id": 0}
        )
        products = await cursor.to_list(5000)
        
        total_products = len(products)
        logger.info(f"Processing {total_products} products")
        
        # Find all duplicate groups
        try:
            duplicate_groups = await self._find_duplicate_groups(products)
            logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        except Exception as e:
            errors.append(f"Error finding duplicates: {e}")
            logger.error(f"Deduplication error: {e}")
        
        products_merged = 0
        canonical_created = 0
        canonical_updated = 0
        
        # Process each duplicate group
        if not dry_run and duplicate_groups:
            for group in duplicate_groups:
                try:
                    result = await self._merge_duplicate_group(group)
                    products_merged += result.get('merged', 0)
                    if result.get('created'):
                        canonical_created += 1
                    if result.get('updated'):
                        canonical_updated += 1
                except Exception as e:
                    errors.append(f"Error merging group: {e}")
                    logger.error(f"Merge error: {e}")
        
        # Update non-duplicate products to canonical format
        if not dry_run:
            try:
                non_duplicates = await self._mark_canonical_singles(products, duplicate_groups)
                canonical_updated += non_duplicates
            except Exception as e:
                errors.append(f"Error updating singles: {e}")
        
        # Recompute scores for all canonical products
        if not dry_run:
            try:
                await self._recompute_all_scores()
            except Exception as e:
                errors.append(f"Error recomputing scores: {e}")
        
        completed_at = datetime.now(timezone.utc)
        duration = (completed_at - started_at).total_seconds()
        
        result = DeduplicationResult(
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_seconds=duration,
            total_products_processed=total_products,
            duplicate_groups_found=len(duplicate_groups),
            products_merged=products_merged,
            canonical_products_created=canonical_created,
            canonical_products_updated=canonical_updated,
            errors=errors,
            success=len(errors) == 0
        )
        
        # Save deduplication run to history
        await self._save_dedup_run(result)
        
        return result
    
    async def _find_duplicate_groups(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Find groups of duplicate products.
        
        Uses Union-Find algorithm to group products.
        """
        # Build adjacency list of matches
        matches = self.matcher.find_duplicates(products)
        
        if not matches:
            return []
        
        # Union-Find to group matches
        parent = {p.get('id'): p.get('id') for p in products}
        product_map = {p.get('id'): p for p in products}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Union matched products
        for match in matches:
            union(match.product_a_id, match.product_b_id)
        
        # Group by root
        groups = {}
        for product_id in parent:
            root = find(product_id)
            if root not in groups:
                groups[root] = []
            groups[root].append(product_map.get(product_id))
        
        # Filter to groups with 2+ products
        duplicate_groups = [
            group for group in groups.values() 
            if len(group) >= 2
        ]
        
        return duplicate_groups
    
    async def _merge_duplicate_group(
        self, 
        group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge a group of duplicate products"""
        if len(group) < 2:
            return {'merged': 0, 'created': False, 'updated': False}
        
        # Create canonical product
        canonical = self.merger.merge_products(group)
        canonical_dict = self.merger.canonical_to_dict(canonical)
        
        # Check if we're updating an existing canonical
        existing = await self.db.products.find_one({
            "canonical_id": {"$in": [p.get('canonical_id') for p in group if p.get('canonical_id')]}
        })
        
        if existing:
            # Update existing canonical
            canonical_dict['canonical_id'] = existing.get('canonical_id')
            canonical_dict['id'] = existing.get('id')
            
            await self.db.products.update_one(
                {"id": existing['id']},
                {"$set": canonical_dict}
            )
            
            created = False
            updated = True
        else:
            # Create new canonical product
            canonical_dict['id'] = str(uuid.uuid4())
            await self.db.products.insert_one(canonical_dict)
            created = True
            updated = False
        
        # Mark merged products as non-canonical
        merged_ids = [p.get('id') for p in group]
        
        # Filter out the canonical product ID from the list to update
        ids_to_mark_merged = [mid for mid in merged_ids if mid != canonical_dict['id']]
        
        if ids_to_mark_merged:
            await self.db.products.update_many(
                {"id": {"$in": ids_to_mark_merged}},
                {
                    "$set": {
                        "is_canonical": False,
                        "canonical_id": canonical_dict['canonical_id'],
                        "merged_into": canonical_dict['id'],
                        "merged_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
        
        return {
            'merged': len(group),
            'created': created,
            'updated': updated,
            'canonical_id': canonical_dict['canonical_id']
        }
    
    async def _mark_canonical_singles(
        self, 
        products: List[Dict[str, Any]],
        duplicate_groups: List[List[Dict[str, Any]]]
    ) -> int:
        """Mark non-duplicate products as canonical singles"""
        # Get IDs of products in duplicate groups
        duplicate_ids = set()
        for group in duplicate_groups:
            for p in group:
                duplicate_ids.add(p.get('id'))
        
        # Find single products (not in any group)
        singles = [p for p in products if p.get('id') not in duplicate_ids]
        
        updated = 0
        for product in singles:
            # Check if already has canonical_id
            if not product.get('canonical_id'):
                canonical_id = str(uuid.uuid4())
                
                await self.db.products.update_one(
                    {"id": product.get('id')},
                    {
                        "$set": {
                            "canonical_id": canonical_id,
                            "is_canonical": True,
                            "contributing_sources": [product.get('data_source', 'unknown')],
                            "canonical_confidence": product.get('confidence_score', 0)
                        }
                    }
                )
                updated += 1
        
        return updated
    
    async def _recompute_all_scores(self):
        """Recompute scores for all canonical products"""
        logger.info("Recomputing scores for all canonical products")
        
        # Get all canonical products
        cursor = self.db.products.find(
            {"is_canonical": {"$ne": False}},
            {"_id": 0}
        )
        
        async for product in cursor:
            try:
                scores = self._compute_product_scores(product)
                
                await self.db.products.update_one(
                    {"id": product.get('id')},
                    {"$set": scores}
                )
            except Exception as e:
                logger.error(f"Error computing scores for {product.get('id')}: {e}")
    
    def _compute_product_scores(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute all product scores using merged data.
        
        Returns dict with all score fields.
        """
        # Get source data for additional signals
        source_data = product.get('source_data', [])
        
        # Trend Score (0-100)
        trend_score = self._compute_trend_score(product, source_data)
        
        # Margin Score (0-100)
        margin_score = self._compute_margin_score(product)
        
        # Competition Score (0-100, lower is better for opportunities)
        competition_score = self._compute_competition_score(product, source_data)
        
        # Market Score (0-100)
        market_score = self._compute_market_score(product, source_data)
        
        # Win Score (0-100) - Overall opportunity score
        win_score = (
            trend_score * 0.30 +
            margin_score * 0.25 +
            (100 - competition_score) * 0.25 +
            market_score * 0.20
        )
        
        # Success Probability (0-100)
        success_probability = self._compute_success_probability(
            trend_score, margin_score, competition_score, market_score, product
        )
        
        # Determine trend stage
        trend_stage = self._determine_trend_stage(trend_score, source_data)
        
        # Determine competition level
        competition_level = self._determine_competition_level(competition_score)
        
        return {
            'trend_score': round(trend_score, 1),
            'margin_score': round(margin_score, 1),
            'competition_score': round(competition_score, 1),
            'market_score': round(market_score, 1),
            'win_score': round(win_score, 1),
            'success_probability': round(success_probability, 1),
            'trend_stage': trend_stage,
            'competition_level': competition_level,
            'scores_updated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def _compute_trend_score(
        self, 
        product: Dict[str, Any], 
        source_data: List[Dict[str, Any]]
    ) -> float:
        """Compute trend score using all available signals"""
        signals = []
        
        # TikTok signals
        tiktok_data = next((s for s in source_data if s.get('source_name') == 'tiktok_trends'), None)
        if tiktok_data:
            views = tiktok_data.get('tiktok_views', 0)
            if views > 1000000:
                signals.append(90)
            elif views > 100000:
                signals.append(75)
            elif views > 10000:
                signals.append(60)
            elif views > 0:
                signals.append(40)
        
        # Amazon BSR change
        amazon_data = next((s for s in source_data if 'amazon' in s.get('source_name', '')), None)
        if amazon_data:
            bsr_change = amazon_data.get('bsr_change', 0)
            if bsr_change > 500:
                signals.append(95)
            elif bsr_change > 100:
                signals.append(80)
            elif bsr_change > 50:
                signals.append(65)
            elif bsr_change > 0:
                signals.append(50)
        
        # Order velocity
        orders = product.get('total_orders', 0)
        if orders > 10000:
            signals.append(90)
        elif orders > 1000:
            signals.append(75)
        elif orders > 100:
            signals.append(55)
        elif orders > 0:
            signals.append(35)
        
        # Existing trend score if available
        if product.get('trend_score', 0) > 0:
            signals.append(product['trend_score'])
        
        if signals:
            return sum(signals) / len(signals)
        return 50  # Neutral default
    
    def _compute_margin_score(self, product: Dict[str, Any]) -> float:
        """Compute margin score"""
        supplier_cost = product.get('supplier_cost', 0)
        retail_price = product.get('estimated_retail_price', 0)
        
        if supplier_cost > 0 and retail_price > 0:
            margin = retail_price - supplier_cost
            margin_percent = (margin / retail_price) * 100
            
            if margin_percent >= 70:
                return 95
            elif margin_percent >= 60:
                return 85
            elif margin_percent >= 50:
                return 75
            elif margin_percent >= 40:
                return 65
            elif margin_percent >= 30:
                return 55
            elif margin_percent >= 20:
                return 45
            else:
                return 30
        
        # Use existing if available
        return product.get('margin_score', 50)
    
    def _compute_competition_score(
        self, 
        product: Dict[str, Any], 
        source_data: List[Dict[str, Any]]
    ) -> float:
        """Compute competition score (higher = more competitive)"""
        signals = []
        
        # Review count as competition proxy
        reviews = product.get('total_reviews', 0)
        if reviews > 10000:
            signals.append(90)  # Very competitive
        elif reviews > 1000:
            signals.append(70)
        elif reviews > 100:
            signals.append(50)
        elif reviews > 0:
            signals.append(30)
        else:
            signals.append(20)  # Low competition
        
        # Ad activity
        for source in source_data:
            ad_count = source.get('ad_count', 0)
            if ad_count > 100:
                signals.append(85)
            elif ad_count > 20:
                signals.append(65)
            elif ad_count > 5:
                signals.append(45)
        
        # Existing score
        if product.get('competition_score', 0) > 0:
            signals.append(product['competition_score'])
        
        if signals:
            return sum(signals) / len(signals)
        return 50
    
    def _compute_market_score(
        self, 
        product: Dict[str, Any], 
        source_data: List[Dict[str, Any]]
    ) -> float:
        """Compute market opportunity score"""
        signals = []
        
        # Multi-source validation bonus
        num_sources = len(product.get('contributing_sources', []))
        if num_sources >= 3:
            signals.append(90)
        elif num_sources >= 2:
            signals.append(75)
        else:
            signals.append(50)
        
        # Data confidence
        confidence = product.get('canonical_confidence', 0)
        signals.append(confidence)
        
        # Orders indicate market demand
        orders = product.get('total_orders', 0)
        if orders > 5000:
            signals.append(85)
        elif orders > 500:
            signals.append(70)
        elif orders > 50:
            signals.append(55)
        
        if signals:
            return sum(signals) / len(signals)
        return 50
    
    def _compute_success_probability(
        self,
        trend_score: float,
        margin_score: float,
        competition_score: float,
        market_score: float,
        product: Dict[str, Any]
    ) -> float:
        """Compute overall success probability"""
        # Weighted factors
        base_prob = (
            trend_score * 0.30 +
            margin_score * 0.25 +
            (100 - competition_score) * 0.25 +  # Lower competition = better
            market_score * 0.20
        )
        
        # Confidence adjustment
        confidence = product.get('canonical_confidence', 0)
        confidence_factor = 0.8 + (confidence / 500)  # 0.8 to 1.0
        
        # Multi-source bonus
        num_sources = len(product.get('contributing_sources', []))
        source_bonus = min(10, num_sources * 3)
        
        return min(100, base_prob * confidence_factor + source_bonus)
    
    def _determine_trend_stage(
        self, 
        trend_score: float, 
        source_data: List[Dict[str, Any]]
    ) -> str:
        """Determine the trend lifecycle stage"""
        # Check for TikTok viral signals
        tiktok_data = next((s for s in source_data if s.get('source_name') == 'tiktok_trends'), None)
        if tiktok_data and tiktok_data.get('tiktok_views', 0) > 1000000:
            if trend_score > 85:
                return 'exploding'
        
        # Check for Amazon BSR spike
        amazon_data = next((s for s in source_data if 'amazon' in s.get('source_name', '')), None)
        if amazon_data and amazon_data.get('bsr_change', 0) > 200:
            if trend_score > 80:
                return 'exploding'
        
        if trend_score >= 80:
            return 'rising'
        elif trend_score >= 60:
            return 'stable'
        elif trend_score >= 40:
            return 'early'
        else:
            return 'declining'
    
    def _determine_competition_level(self, competition_score: float) -> str:
        """Determine competition level category"""
        if competition_score >= 75:
            return 'high'
        elif competition_score >= 45:
            return 'medium'
        else:
            return 'low'
    
    async def _save_dedup_run(self, result: DeduplicationResult):
        """Save deduplication run to history"""
        await self.db.dedup_runs.insert_one({
            'started_at': result.started_at,
            'completed_at': result.completed_at,
            'duration_seconds': result.duration_seconds,
            'total_products_processed': result.total_products_processed,
            'duplicate_groups_found': result.duplicate_groups_found,
            'products_merged': result.products_merged,
            'canonical_products_created': result.canonical_products_created,
            'canonical_products_updated': result.canonical_products_updated,
            'errors': result.errors,
            'success': result.success
        })
    
    async def get_dedup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get deduplication run history"""
        cursor = self.db.dedup_runs.find(
            {},
            {"_id": 0}
        ).sort("started_at", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_canonical_stats(self) -> Dict[str, Any]:
        """Get statistics about canonical products"""
        total_products = await self.db.products.count_documents({})
        canonical_products = await self.db.products.count_documents({"is_canonical": {"$ne": False}})
        merged_products = await self.db.products.count_documents({"is_canonical": False})
        
        # Multi-source products
        multi_source = await self.db.products.count_documents({
            "contributing_sources.1": {"$exists": True}  # Has at least 2 sources
        })
        
        # Average confidence
        pipeline = [
            {"$match": {"is_canonical": {"$ne": False}}},
            {"$group": {"_id": None, "avg_confidence": {"$avg": "$canonical_confidence"}}}
        ]
        confidence_result = await self.db.products.aggregate(pipeline).to_list(1)
        avg_confidence = confidence_result[0]['avg_confidence'] if confidence_result else 0
        
        return {
            "total_products": total_products,
            "canonical_products": canonical_products,
            "merged_products": merged_products,
            "multi_source_products": multi_source,
            "avg_canonical_confidence": round(avg_confidence, 1)
        }
    
    async def find_duplicates_for_product(
        self, 
        product_id: str
    ) -> List[Dict[str, Any]]:
        """Find potential duplicates for a specific product"""
        # Get the target product
        product = await self.db.products.find_one(
            {"id": product_id},
            {"_id": 0}
        )
        
        if not product:
            return []
        
        # Get candidates (same category or similar keywords)
        candidates_cursor = self.db.products.find(
            {
                "id": {"$ne": product_id},
                "$or": [
                    {"category": product.get('category')},
                    {"product_name": {"$regex": product.get('product_name', '')[:20], "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).limit(100)
        
        candidates = await candidates_cursor.to_list(100)
        
        # Find matches
        matches = self.matcher.find_duplicates(candidates, target_product=product)
        
        # Return matched products with scores
        return [
            {
                "product_id": m.product_b_id,
                "match_score": m.overall_score,
                "title_score": m.title_score,
                "keyword_score": m.keyword_score,
                "match_reasons": m.match_reasons
            }
            for m in matches
        ]
