"""
Supplier Service

Manages supplier listings for products. Supports AliExpress and CJ Dropshipping.
Provides supplier discovery, selection, and attachment to store products.
"""

import re
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for managing product suppliers."""
    
    SHIPPING_ORIGINS = {
        'aliexpress': 'China',
        'cj_dropshipping': 'China/US Warehouse',
    }
    
    SHIPPING_ESTIMATES = {
        'aliexpress': {'min_days': 7, 'max_days': 20, 'standard': 14},
        'cj_dropshipping': {'min_days': 5, 'max_days': 15, 'standard': 10},
    }
    
    def __init__(self, db):
        self.db = db
    
    async def get_suppliers_for_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all supplier listings for a product."""
        cursor = self.db.product_suppliers.find(
            {"product_id": product_id},
            {"_id": 0}
        ).sort("is_selected", -1)
        return await cursor.to_list(50)
    
    async def find_suppliers(self, product_id: str) -> Dict[str, Any]:
        """
        Find suppliers for a product.
        Creates supplier listings based on product data and AliExpress search.
        """
        product = await self.db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            return {"error": "Product not found", "suppliers_found": 0}
        
        # Check existing suppliers
        existing = await self.db.product_suppliers.count_documents({"product_id": product_id})
        if existing > 0:
            suppliers = await self.get_suppliers_for_product(product_id)
            return {"suppliers_found": existing, "suppliers": suppliers, "cached": True}
        
        suppliers = []
        
        # Generate AliExpress supplier listing
        ali_supplier = self._create_aliexpress_listing(product)
        if ali_supplier:
            suppliers.append(ali_supplier)
        
        # Generate CJ Dropshipping listing
        cj_supplier = self._create_cj_listing(product)
        if cj_supplier:
            suppliers.append(cj_supplier)
        
        # Save to database
        if suppliers:
            await self.db.product_suppliers.insert_many(suppliers)
        
        # Clean _id from response
        for s in suppliers:
            s.pop('_id', None)
        
        return {
            "suppliers_found": len(suppliers),
            "suppliers": suppliers,
            "cached": False,
        }
    
    def _create_aliexpress_listing(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an AliExpress supplier listing from product data."""
        product_name = product.get('product_name', '')
        if not product_name:
            return None
        
        retail_price = product.get('estimated_retail_price', 0)
        existing_cost = product.get('supplier_cost', 0)
        
        # Use existing cost or estimate at ~35% of retail
        supplier_cost = existing_cost if existing_cost > 0 else round(retail_price * 0.35, 2) if retail_price > 0 else 0
        
        # Build search URL
        search_term = re.sub(r'[^\w\s]', '', product_name[:60]).strip()
        supplier_url = product.get('supplier_link') or f"https://www.aliexpress.com/wholesale?SearchText={search_term.replace(' ', '+')}"
        
        shipping_est = self.SHIPPING_ESTIMATES['aliexpress']
        
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get('id'),
            "source": "aliexpress",
            "supplier_name": "AliExpress Marketplace",
            "supplier_url": supplier_url,
            "supplier_cost": supplier_cost,
            "currency": "USD",
            "estimated_shipping_cost": round(supplier_cost * 0.1, 2) if supplier_cost > 0 else 0,
            "shipping_origin": self.SHIPPING_ORIGINS['aliexpress'],
            "shipping_days_min": shipping_est['min_days'],
            "shipping_days_max": shipping_est['max_days'],
            "shipping_days_estimate": shipping_est['standard'],
            "stock_status": "in_stock",
            "stock_quantity": None,
            "supplier_rating": None,
            "supplier_orders": None,
            "confidence": "estimated" if existing_cost <= 0 else "verified",
            "confidence_note": "Cost estimated from retail price" if existing_cost <= 0 else "Cost from Amazon listing data",
            "is_selected": False,
            "image_urls": [product.get('image_url', '')] if product.get('image_url') else [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def _create_cj_listing(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a CJ Dropshipping supplier listing."""
        product_name = product.get('product_name', '')
        if not product_name:
            return None
        
        retail_price = product.get('estimated_retail_price', 0)
        # CJ typically slightly cheaper than AliExpress
        supplier_cost = round(retail_price * 0.30, 2) if retail_price > 0 else 0
        
        search_term = re.sub(r'[^\w\s]', '', product_name[:60]).strip()
        supplier_url = f"https://cjdropshipping.com/search.html?keyword={search_term.replace(' ', '%20')}"
        
        shipping_est = self.SHIPPING_ESTIMATES['cj_dropshipping']
        
        return {
            "id": str(uuid.uuid4()),
            "product_id": product.get('id'),
            "source": "cj_dropshipping",
            "supplier_name": "CJ Dropshipping",
            "supplier_url": supplier_url,
            "supplier_cost": supplier_cost,
            "currency": "USD",
            "estimated_shipping_cost": round(supplier_cost * 0.08, 2) if supplier_cost > 0 else 0,
            "shipping_origin": self.SHIPPING_ORIGINS['cj_dropshipping'],
            "shipping_days_min": shipping_est['min_days'],
            "shipping_days_max": shipping_est['max_days'],
            "shipping_days_estimate": shipping_est['standard'],
            "stock_status": "unknown",
            "stock_quantity": None,
            "supplier_rating": None,
            "supplier_orders": None,
            "confidence": "estimated",
            "confidence_note": "Cost estimated from retail price. Verify on CJ Dropshipping.",
            "is_selected": False,
            "image_urls": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    
    async def select_supplier(self, product_id: str, supplier_id: str, user_id: str) -> Dict[str, Any]:
        """Select a supplier for a product (deselects others)."""
        # Deselect all for this product
        await self.db.product_suppliers.update_many(
            {"product_id": product_id},
            {"$set": {"is_selected": False}}
        )
        
        # Select the chosen one
        result = await self.db.product_suppliers.update_one(
            {"id": supplier_id, "product_id": product_id},
            {"$set": {
                "is_selected": True,
                "selected_by": user_id,
                "selected_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        
        if result.modified_count == 0:
            return {"error": "Supplier not found"}
        
        # Get the selected supplier
        supplier = await self.db.product_suppliers.find_one(
            {"id": supplier_id}, {"_id": 0}
        )
        
        # Update product with selected supplier info
        if supplier:
            await self.db.products.update_one(
                {"id": product_id},
                {"$set": {
                    "selected_supplier_id": supplier_id,
                    "selected_supplier_source": supplier.get('source'),
                    "selected_supplier_cost": supplier.get('supplier_cost'),
                    "selected_supplier_shipping": supplier.get('shipping_days_estimate'),
                }}
            )
        
        return {"success": True, "supplier": supplier}
    
    async def enrich_from_crawl_data(self, product_id: str, crawl_text: str) -> Dict[str, Any]:
        """
        Parse crawl_tool output to extract real AliExpress supplier data.
        This is called during development to populate real supplier data.
        """
        suppliers = self._parse_aliexpress_crawl(crawl_text, product_id)
        
        if suppliers:
            # Remove old listings for this product from aliexpress
            await self.db.product_suppliers.delete_many({
                "product_id": product_id,
                "source": "aliexpress"
            })
            await self.db.product_suppliers.insert_many(suppliers)
            for s in suppliers:
                s.pop('_id', None)
        
        return {"enriched": len(suppliers), "suppliers": suppliers}
    
    def _parse_aliexpress_crawl(self, text: str, product_id: str) -> List[Dict[str, Any]]:
        """Parse AliExpress crawl_tool markdown output to extract supplier listings."""
        suppliers = []
        
        # Pattern: **Product Name**\n$price\n...\nX.X rating\nN sold
        # Split by product blocks (each starts with bold product name)
        blocks = re.split(r'\*\*([^*]{20,})\*\*', text)
        
        for i in range(1, len(blocks), 2):
            if i + 1 >= len(blocks):
                break
            
            name = blocks[i].strip()
            detail = blocks[i + 1]
            
            # Extract price
            price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', detail)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0
            
            # Extract rating
            rating_match = re.search(r'(\d+\.?\d*)\s*\n\s*\n\s*(\d[\d,]*)\+?\s*sold', detail)
            rating = float(rating_match.group(1)) if rating_match else None
            orders = int(rating_match.group(2).replace(',', '')) if rating_match else None
            
            # Extract delivery
            delivery_match = re.search(r'Delivery:\s*(\w+ \d+ - \d+)', detail)
            delivery = delivery_match.group(1) if delivery_match else None
            
            # Extract product URL
            url_match = re.search(r'\(https://www\.aliexpress\.us/item/(\d+)\.html', detail)
            product_url = f"https://www.aliexpress.us/item/{url_match.group(1)}.html" if url_match else None
            
            if price > 0 and product_url:
                suppliers.append({
                    "id": str(uuid.uuid4()),
                    "product_id": product_id,
                    "source": "aliexpress",
                    "supplier_name": name[:120],
                    "supplier_url": product_url,
                    "supplier_cost": price,
                    "currency": "USD",
                    "estimated_shipping_cost": 0 if 'Free shipping' in detail else round(price * 0.05, 2),
                    "shipping_origin": "China",
                    "shipping_days_min": 7,
                    "shipping_days_max": 20,
                    "shipping_days_estimate": 14,
                    "stock_status": "in_stock" if orders and orders > 0 else "unknown",
                    "stock_quantity": None,
                    "supplier_rating": rating,
                    "supplier_orders": orders,
                    "confidence": "scraped",
                    "confidence_note": "Real data from AliExpress search results",
                    "is_selected": False,
                    "image_urls": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
        
        return suppliers[:10]  # Limit to top 10
