"""
Fix broken product images by replacing Amazon placeholder GIFs with curated Unsplash images per category.
Run: cd /app/backend && python fix_images.py
"""
import asyncio
import os
import sys
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import motor.motor_asyncio

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
BROKEN_IMAGE = "01jrA-8DXYL"

# Curated Unsplash images per category (reliable, high-quality)
CATEGORY_IMAGES = {
    "Garden & Outdoors": [
        "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1558171813-4c088753af8f?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=600&h=600&fit=crop",
    ],
    "Automotive": [
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1542362567-b07e54358753?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0afe?w=600&h=600&fit=crop",
    ],
    "Health & Personal Care": [
        "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1505576399279-0b6f3e7b8c2e?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=600&fit=crop",
    ],
    "DIY & Tools": [
        "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581783898377-1c85bf937427?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600&h=600&fit=crop",
    ],
    "Home & Kitchen": [
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1583845112239-97ef1341b271?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?w=600&h=600&fit=crop",
    ],
    "Beauty": [
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=600&h=600&fit=crop",
    ],
    "Toys & Games": [
        "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=600&h=600&fit=crop",
    ],
    "Sports & Outdoors": [
        "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1461896836934-bd45ba3e44e1?w=600&h=600&fit=crop",
    ],
    "Pet Supplies": [
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&h=600&fit=crop",
    ],
    "Fashion": [
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=600&h=600&fit=crop",
    ],
    "Baby Products": [
        "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&h=600&fit=crop",
    ],
    "Electronics": [
        "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&h=600&fit=crop",
        "https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=600&h=600&fit=crop",
    ],
}

DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop",
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=600&fit=crop",
    "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&h=600&fit=crop",
]


async def fix_images():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    broken = await db.products.find(
        {"image_url": {"$regex": BROKEN_IMAGE}},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1}
    ).to_list(200)

    print(f"Found {len(broken)} products with broken images")

    cat_counters = {}
    fixed = 0

    for product in broken:
        pid = product["id"]
        category = product.get("category", "Other")
        images = CATEGORY_IMAGES.get(category, DEFAULT_IMAGES)

        idx = cat_counters.get(category, 0)
        new_url = images[idx % len(images)]
        cat_counters[category] = idx + 1

        result = await db.products.update_one(
            {"id": pid},
            {"$set": {"image_url": new_url}}
        )
        if result.modified_count > 0:
            fixed += 1
            print(f"  Fixed: {product['product_name'][:40]:40s} ({category}) -> ...{new_url[-30:]}")

    print(f"\nDone! Fixed {fixed}/{len(broken)} images")
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_images())
