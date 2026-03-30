"""
Fix TikTok product images by searching CJ Dropshipping for real product images.
Run with: python fix_tiktok_images.py
"""
import asyncio
import os
import sys
import time

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from services.cj_dropshipping import search_products

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "trendscout")

# Map TikTok product names -> better CJ search queries
TIKTOK_SEARCH_MAP = {
    "LED Sunset Lamp": "sunset projection lamp",
    "Cloud Slides": "cloud slides EVA pillow sandals",
    "Portable Neck Fan": "bladeless wearable neck fan",
    "Ice Roller Face Massager": "ice roller face massager stainless",
    "Star Projector Galaxy Light": "star projector galaxy light LED",
    "Scalp Massager Shampoo Brush": "silicone scalp massager brush",
    "Mini Portable Projector": "mini portable projector pocket",
    "Magnetic Phone Mount": "magnetic phone car mount 360",
    "Acrylic Desk Organizer": "acrylic clear desk organizer",
    "Wireless Earbuds Pro": "ANC wireless earbuds bluetooth",
    "Posture Corrector Belt": "posture corrector back support brace",
    "Pet Hair Remover Roller": "pet hair remover lint roller reusable",
    "Portable Blender Cup": "USB portable blender smoothie cup",
    "LED Strip Lights 50ft": "RGB LED strip lights app control",
    "Electric Lunch Box": "portable electric food warmer lunch box",
}


async def fix_tiktok_images():
    if not MONGO_URL:
        print("ERROR: MONGO_URL environment variable not set")
        sys.exit(1)

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    products_col = db["products"]

    print("Fetching TikTok products from database...")
    # Try both field names (source and data_source) and also catch Unsplash-image products
    tiktok_products = await products_col.find(
        {"$or": [
            {"source": "tiktok"},
            {"data_source": "tiktok"},
            {"tiktok_views": {"$gt": 0}, "image_url": {"$regex": "unsplash.com"}},
        ]},
        {"_id": 1, "product_name": 1, "image_url": 1}
    ).to_list(length=100)

    print(f"Found {len(tiktok_products)} TikTok products")

    updated = 0
    failed = 0

    for product in tiktok_products:
        name = product.get("product_name", "")
        current_image = product.get("image_url", "")

        # Get CJ search query for this product
        search_query = TIKTOK_SEARCH_MAP.get(name, name)

        print(f"\nSearching CJ for: '{search_query}' (product: {name})")

        try:
            result = await search_products(search_query, page=1, page_size=3)
            await asyncio.sleep(1.2)  # Respect CJ rate limit

            # search_products returns {"success": bool, "products": [...]}
            product_list = result.get("products", []) if isinstance(result, dict) else []

            if product_list:
                # Pick first result with a valid image
                new_image = None
                for r in product_list:
                    img = r.get("image_url") or r.get("image") or r.get("productImage") or r.get("thumbnail")
                    if img and isinstance(img, str) and img.startswith("http"):
                        new_image = img
                        break

                if new_image and new_image != current_image:
                    await products_col.update_one(
                        {"_id": product["_id"]},
                        {"$set": {"image_url": new_image}}
                    )
                    print(f"  ✓ {name[:40]} -> {new_image[:70]}...")
                    updated += 1
                elif new_image == current_image:
                    print(f"  = {name[:40]} (image already correct)")
                    updated += 1
                else:
                    print(f"  ✗ No valid image in CJ results for: {name}")
                    failed += 1
            else:
                print(f"  ✗ No CJ results for: {name}")
                failed += 1

        except Exception as e:
            print(f"  ERROR for {name}: {e}")
            failed += 1
            await asyncio.sleep(2)

    print(f"\n{'='*50}")
    print(f"DONE! Updated: {updated}, Failed: {failed}")
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_tiktok_images())
