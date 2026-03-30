"""
Fix TikTok product images — uses name-matching to pick the right CJ product image.
Falls back to curated Unsplash images when CJ returns no good match.
Run with: python fix_tiktok_images.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from services.cj_dropshipping import search_products

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "trendscout")

# Curated fallback images — used when CJ search doesn't return a good match.
# Each URL is a specific Unsplash photo chosen to match the product.
CURATED_IMAGES = {
    # Original 15 TikTok products
    "LED Sunset Lamp":              "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&h=600&fit=crop",
    "LED Sunset Projection Lamp":   "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&h=600&fit=crop",
    "Sunset Projection Lamp":       "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&h=600&fit=crop",
    "Cloud Slides":                 "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=600&h=600&fit=crop",
    "Cloud Pillow Slides":          "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=600&h=600&fit=crop",
    "Portable Neck Fan":            "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&h=600&fit=crop",
    "Portable Bladeless Neck Fan":  "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&h=600&fit=crop",
    "Ice Roller Face Massager":     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=600&fit=crop",
    "Star Projector Galaxy Light":  "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&h=600&fit=crop",
    "Smart Galaxy Star Projector":  "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&h=600&fit=crop",
    "Scalp Massager Shampoo Brush": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&h=600&fit=crop",
    "Mini Portable Projector":      "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&h=600&fit=crop",
    "Mini Pocket Projector 1080P":  "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&h=600&fit=crop",
    "Magnetic Phone Mount":         "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=600&h=600&fit=crop",
    "MagSafe Car Phone Mount":      "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=600&h=600&fit=crop",
    "Acrylic Desk Organizer":       "https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=600&h=600&fit=crop",
    "Clear Acrylic Desk Organizer": "https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=600&h=600&fit=crop",
    "Wireless Earbuds Pro":         "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=600&fit=crop",
    "Premium ANC Wireless Earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=600&fit=crop",
    "Posture Corrector Belt":       "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop",
    "Adjustable Posture Corrector": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop",
    "Pet Hair Remover Roller":      "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop",
    "Reusable Pet Hair Remover":    "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop",
    "Portable Blender Cup":         "https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=600&h=600&fit=crop",
    "USB Rechargeable Blender Cup": "https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=600&h=600&fit=crop",
    "LED Strip Lights 50ft":        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    "RGB LED Strip Lights 50ft":    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop",
    "Electric Lunch Box":           "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop",
    "Electric Heated Lunch Box":    "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop",
    # Extra products added by Emergent
    "Wireless Charging Desk Pad":   "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&h=600&fit=crop",
    "Smart Water Bottle Reminder":  "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&h=600&fit=crop",
    "Mini Thermal Printer":         "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=600&h=600&fit=crop",
    "Weighted Sleep Eye Mask":      "https://images.unsplash.com/photo-1531353826977-0941b4779a1c?w=600&h=600&fit=crop",
    "Ergonomic Laptop Stand":       "https://images.unsplash.com/photo-1593642634315-48f5414c3ad9?w=600&h=600&fit=crop",
    "Electric Milk Frother":        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&h=600&fit=crop",
    "Collapsible Storage Bins Set": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&h=600&fit=crop",
    "Ceramic Coating Spray":        "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=600&h=600&fit=crop",
    "Yoga Wheel Set":               "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&h=600&fit=crop",
    "Magnetic Spice Jars Set":      "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&h=600&fit=crop",
    "Self-Watering Plant Pots":     "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600&h=600&fit=crop",
}

STOPWORDS = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'set', 'of', 'to', 'in', 'is'}


def score_match(query_name: str, cj_name: str) -> float:
    """
    Score how well a CJ product name matches our product name.
    Returns a fraction: 1.0 = perfect match, 0.0 = no overlap.
    """
    q_words = set(w.lower() for w in query_name.split() if w.lower() not in STOPWORDS and len(w) > 2)
    c_words = set(w.lower() for w in cj_name.split() if w.lower() not in STOPWORDS and len(w) > 2)
    if not q_words:
        return 0.0
    return len(q_words & c_words) / len(q_words)


async def fix_tiktok_images():
    if not MONGO_URL:
        print("ERROR: MONGO_URL not set")
        sys.exit(1)

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    col = db["products"]

    print("Fetching TikTok products from database...")
    products = await col.find(
        {"$or": [
            {"source": "tiktok"},
            {"data_source": "tiktok"},
            {"tiktok_views": {"$gt": 0}},
        ]},
        {"_id": 1, "product_name": 1, "image_url": 1}
    ).to_list(length=200)

    print(f"Found {len(products)} TikTok products\n")

    updated = 0
    used_curated = 0
    failed = 0

    for product in products:
        name = product.get("product_name", "")
        current_image = product.get("image_url", "")

        # --- Step 1: Try curated image first (most reliable) ---
        if name in CURATED_IMAGES:
            new_image = CURATED_IMAGES[name]
            if new_image != current_image:
                await col.update_one({"_id": product["_id"]}, {"$set": {"image_url": new_image}})
                print(f"  ✓ [curated] {name}")
                used_curated += 1
                updated += 1
            else:
                print(f"  = [curated] {name} (already set)")
                updated += 1
            continue

        # --- Step 2: Search CJ with name matching ---
        print(f"  Searching CJ for: {name}")
        try:
            result = await search_products(name, page=1, page_size=10)
            await asyncio.sleep(1.2)

            cj_products = result.get("products", []) if isinstance(result, dict) else []

            best_image = None
            best_score = 0.0

            for r in cj_products:
                cj_name = r.get("product_name", r.get("name", ""))
                score = score_match(name, cj_name)
                img = r.get("image_url") or r.get("image") or r.get("productImage") or ""
                if score > best_score and img and isinstance(img, str) and img.startswith("http"):
                    best_score = score
                    best_image = img

            if best_image and best_score >= 0.4:
                if best_image != current_image:
                    await col.update_one({"_id": product["_id"]}, {"$set": {"image_url": best_image}})
                    print(f"  ✓ [CJ score={best_score:.1f}] {name}")
                    updated += 1
                else:
                    print(f"  = [CJ] {name} (already correct)")
                    updated += 1
            else:
                print(f"  ✗ No good CJ match (best score={best_score:.1f}) for: {name}")
                failed += 1

        except Exception as e:
            print(f"  ERROR for {name}: {e}")
            failed += 1
            await asyncio.sleep(2)

    print(f"\n{'='*50}")
    print(f"DONE! Updated: {updated} ({used_curated} curated, {updated-used_curated} CJ), Failed: {failed}")
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_tiktok_images())
