"""
Product Data Migration Script

Adds required fields to all existing products and recomputes scores
using the transparent scoring engine.
"""

import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_products():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    from services.scoring import ScoringEngine
    engine = ScoringEngine(db)
    
    cursor = db.products.find({}, {"_id": 0})
    products = await cursor.to_list(5000)
    
    logger.info(f"Migrating {len(products)} products")
    
    stats = {'updated': 0, 'failed': 0}
    
    for product in products:
        pid = product.get('id')
        if not pid:
            continue
        
        update = {}
        
        # Ensure required fields exist
        if not product.get('canonical_product_id'):
            update['canonical_product_id'] = product.get('canonical_id', pid)
        
        if not product.get('data_sources'):
            ds = product.get('data_source', 'unknown')
            update['data_sources'] = [ds] if ds else ['unknown']
        
        if not product.get('confidence_score'):
            # Calculate real confidence based on data availability
            confidence = 0
            if product.get('is_real_data'):
                confidence += 40
            if product.get('estimated_retail_price', 0) > 0:
                confidence += 15
            if product.get('supplier_cost', 0) > 0:
                confidence += 15
            if product.get('amazon_bsr_change', 0) > 0:
                confidence += 15
            if product.get('image_url'):
                confidence += 10
            if product.get('supplier_link'):
                confidence += 5
            update['confidence_score'] = confidence
        
        if not product.get('last_updated'):
            update['last_updated'] = product.get('updated_at', datetime.now(timezone.utc).isoformat())
        
        # Add missing fields with "unavailable" markers (never fabricate)
        field_defaults = {
            'estimated_shipping_cost': None,
            'recommended_price': product.get('estimated_retail_price'),
            'trend_velocity': None,
            'competitor_density': None,
            'supplier_stock': None,
            'video_urls': [],
        }
        
        for field, default in field_defaults.items():
            if field not in product:
                update[field] = default
        
        # Recompute all scores with new transparent engine
        try:
            scores = engine.calculate_all_scores(product)
            update.update(scores)
        except Exception as e:
            logger.error(f"Score calc failed for {pid}: {e}")
            stats['failed'] += 1
            continue
        
        if update:
            await db.products.update_one({"id": pid}, {"$set": update})
            stats['updated'] += 1
    
    logger.info(f"Migration complete: {stats}")
    return stats


if __name__ == '__main__':
    asyncio.run(migrate_products())
