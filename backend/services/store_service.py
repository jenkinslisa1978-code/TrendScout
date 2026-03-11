"""
Store Service - AI Store Builder and Management
Handles store creation, product-to-store workflow, and AI generation
"""

import uuid
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

# Plan-based store limits
STORE_LIMITS = {
    "starter": 1,
    "pro": 5,
    "elite": float('inf'),  # Unlimited
    "admin": float('inf'),  # Admin always unlimited
}

# Branding style options
BRANDING_STYLES = [
    {"name": "Modern Minimal", "primary": "#0f172a", "secondary": "#3b82f6", "accent": "#10b981", "font": "Inter"},
    {"name": "Bold & Vibrant", "primary": "#7c3aed", "secondary": "#f59e0b", "accent": "#ec4899", "font": "Poppins"},
    {"name": "Clean Professional", "primary": "#1e3a5f", "secondary": "#0ea5e9", "accent": "#14b8a6", "font": "Source Sans Pro"},
    {"name": "Warm & Friendly", "primary": "#92400e", "secondary": "#f97316", "accent": "#84cc16", "font": "Nunito"},
    {"name": "Elegant Luxury", "primary": "#1f2937", "secondary": "#d4af37", "accent": "#a78bfa", "font": "Playfair Display"},
    {"name": "Fresh & Energetic", "primary": "#059669", "secondary": "#06b6d4", "accent": "#fbbf24", "font": "Rubik"},
]

# Store name templates by category
STORE_NAME_TEMPLATES = {
    "Electronics": ["{adj} Tech", "{adj} Gadgets", "Tech{suffix}", "{adj} Electronics", "Gadget{suffix}"],
    "Home Decor": ["{adj} Home", "{adj} Living", "Home{suffix}", "{adj} Decor", "Cozy{suffix}"],
    "Fashion": ["{adj} Style", "{adj} Wear", "Style{suffix}", "{adj} Fashion", "Trend{suffix}"],
    "Health & Fitness": ["{adj} Fit", "{adj} Wellness", "Fit{suffix}", "{adj} Health", "Active{suffix}"],
    "Beauty": ["{adj} Beauty", "{adj} Glow", "Beauty{suffix}", "{adj} Cosmetics", "Glow{suffix}"],
    "Pet Supplies": ["{adj} Pets", "{adj} Paws", "Pet{suffix}", "{adj} Furry", "Paw{suffix}"],
    "Kitchen": ["{adj} Kitchen", "{adj} Cook", "Kitchen{suffix}", "{adj} Chef", "Cook{suffix}"],
    "default": ["{adj} Shop", "{adj} Store", "Shop{suffix}", "{adj} Market", "Store{suffix}"],
}

ADJECTIVES = ["Swift", "Prime", "Urban", "Nova", "Luxe", "Elite", "Apex", "Zen", "Pure", "Smart", "Bright", "Fresh", "Bold", "Sleek", "Vibe"]
SUFFIXES = ["Hub", "Zone", "Spot", "Lab", "Box", "Den", "Nest", "Haven", "Base", "Co"]


def get_store_limit(plan: str) -> int:
    """Get the store limit for a given plan"""
    return STORE_LIMITS.get(plan, 1)


def can_create_store(current_count: int, plan: str) -> bool:
    """Check if user can create another store based on their plan"""
    limit = get_store_limit(plan)
    return current_count < limit


class StoreGenerator:
    """
    AI Store Builder - Generates store content from product data
    Currently uses rules-based generation, structured for future LLM integration
    """
    
    def __init__(self, use_ai: bool = False, ai_client: Any = None):
        """
        Initialize the store generator
        
        Args:
            use_ai: Whether to use real AI for generation (future)
            ai_client: AI client instance (e.g., OpenAI) for future use
        """
        self.use_ai = use_ai
        self.ai_client = ai_client
    
    def generate_store_names(self, product: Dict, count: int = 5) -> List[str]:
        """Generate store name suggestions based on product category"""
        category = product.get('category', 'default')
        templates = STORE_NAME_TEMPLATES.get(category, STORE_NAME_TEMPLATES['default'])
        
        names = []
        used_combos = set()
        
        while len(names) < count:
            template = random.choice(templates)
            adj = random.choice(ADJECTIVES)
            suffix = random.choice(SUFFIXES)
            
            name = template.format(adj=adj, suffix=suffix)
            
            if name not in used_combos:
                names.append(name)
                used_combos.add(name)
        
        return names
    
    def generate_tagline(self, product: Dict, store_name: str) -> str:
        """Generate a store tagline"""
        category = product.get('category', 'General')
        product_name = product.get('product_name', 'products')
        
        tagline_templates = [
            f"Your destination for premium {category.lower()}",
            f"Discover the best in {category.lower()}",
            f"Quality {category.lower()} for modern living",
            f"Elevate your lifestyle with {store_name}",
            "Where quality meets style",
            "Premium products, exceptional value",
            f"Your {category.lower()} experts",
            f"Curated {category.lower()} for you",
        ]
        
        return random.choice(tagline_templates)
    
    def generate_headline(self, product: Dict, store_name: str) -> str:
        """Generate a homepage headline"""
        product_name = product.get('product_name', 'Amazing Products')
        category = product.get('category', 'products')
        
        headline_templates = [
            f"Discover the {product_name}",
            f"Meet Your New Favorite {category} Product",
            f"Transform Your Life with {product_name}",
            f"The {product_name} Everyone's Talking About",
            "Premium Quality, Unbeatable Value",
            "Experience the Difference",
            f"Upgrade Your {category} Game",
            f"Trending Now: {product_name}",
        ]
        
        return random.choice(headline_templates)
    
    def generate_product_title(self, product: Dict) -> str:
        """Generate an optimized product title"""
        original_name = product.get('product_name', 'Product')
        category = product.get('category', '')
        
        # Clean and enhance the title
        title_enhancements = [
            f"Premium {original_name}",
            f"{original_name} - Professional Grade",
            f"{original_name} | Top Rated",
            f"Deluxe {original_name}",
            original_name,  # Keep original as option
        ]
        
        return random.choice(title_enhancements)
    
    def generate_product_description(self, product: Dict) -> str:
        """Generate a compelling product description"""
        product_name = product.get('product_name', 'This product')
        category = product.get('category', 'product')
        short_desc = product.get('short_description', '')
        
        if short_desc:
            base_desc = short_desc
        else:
            base_desc = f"A premium {category.lower()} designed for modern lifestyles"
        
        description = f"""Introducing the {product_name} - {base_desc}.

Designed with quality and functionality in mind, this {category.lower()} product delivers exceptional performance that exceeds expectations. Whether you're looking to upgrade your daily routine or searching for the perfect gift, this is the solution you've been waiting for.

Crafted with premium materials and attention to detail, this product combines style with substance. Join thousands of satisfied customers who have discovered the difference quality makes.

Order now and experience why this is quickly becoming one of the most sought-after {category.lower()} products on the market."""
        
        return description
    
    def generate_bullet_points(self, product: Dict) -> List[str]:
        """Generate product feature bullet points"""
        product_name = product.get('product_name', 'Product')
        category = product.get('category', 'product')
        
        # Category-specific bullet points
        category_bullets = {
            "Electronics": [
                "Advanced technology for superior performance",
                "Energy-efficient design saves power",
                "Compact and portable for on-the-go use",
                "Easy setup in minutes",
                "Durable construction built to last",
            ],
            "Home Decor": [
                "Elevates any room's aesthetic instantly",
                "Premium materials for lasting beauty",
                "Versatile design fits any style",
                "Easy to maintain and clean",
                "Creates the perfect ambiance",
            ],
            "Fashion": [
                "Comfortable fit for all-day wear",
                "Trendy design that turns heads",
                "High-quality materials that last",
                "Versatile for any occasion",
                "Easy care and maintenance",
            ],
            "Health & Fitness": [
                "Supports your wellness goals",
                "Ergonomic design for comfort",
                "Durable for everyday use",
                "Easy to incorporate into your routine",
                "Trusted by fitness enthusiasts",
            ],
            "default": [
                "Premium quality craftsmanship",
                "Designed for everyday convenience",
                "Exceptional value for the price",
                "Loved by thousands of customers",
                "Fast and reliable shipping",
            ],
        }
        
        bullets = category_bullets.get(category, category_bullets['default'])
        
        # Add product-specific bullets
        if product.get('tiktok_views', 0) > 1000000:
            bullets.insert(0, "Trending on social media with millions of views")
        
        return bullets[:5]  # Return top 5
    
    def generate_pricing_suggestion(self, product: Dict) -> Dict:
        """Generate pricing suggestions"""
        supplier_cost = product.get('supplier_cost', 0)
        estimated_retail = product.get('estimated_retail_price', 0)
        
        if estimated_retail > 0:
            suggested_price = estimated_retail
        elif supplier_cost > 0:
            # Apply 3x markup for suggested retail
            suggested_price = round(supplier_cost * 3, 2)
        else:
            suggested_price = 29.99
        
        # Generate compare-at price (original/crossed out price)
        compare_at = round(suggested_price * 1.4, 2)
        
        return {
            "suggested_price": suggested_price,
            "compare_at_price": compare_at,
            "currency": "GBP",
            "supplier_cost": supplier_cost,
            "estimated_margin": round(suggested_price - supplier_cost, 2),
        }
    
    def generate_branding(self, product: Dict) -> Dict:
        """Generate branding style suggestion"""
        category = product.get('category', 'General')
        
        # Select appropriate branding based on category
        if category in ['Electronics', 'Mobile Accessories']:
            style = BRANDING_STYLES[0]  # Modern Minimal
        elif category in ['Fashion', 'Beauty']:
            style = BRANDING_STYLES[4]  # Elegant Luxury
        elif category in ['Health & Fitness']:
            style = BRANDING_STYLES[5]  # Fresh & Energetic
        elif category in ['Home Decor']:
            style = BRANDING_STYLES[2]  # Clean Professional
        else:
            style = random.choice(BRANDING_STYLES)
        
        return {
            "style_name": style["name"],
            "primary_color": style["primary"],
            "secondary_color": style["secondary"],
            "accent_color": style["accent"],
            "font_family": style["font"],
        }
    
    def generate_faq(self, product: Dict) -> List[Dict]:
        """Generate FAQ placeholder content"""
        product_name = product.get('product_name', 'this product')
        
        faqs = [
            {
                "question": f"What is the {product_name}?",
                "answer": f"The {product_name} is a premium product designed to enhance your daily life with quality and convenience."
            },
            {
                "question": "How long does shipping take?",
                "answer": "Standard shipping typically takes 5-10 business days. Express shipping options are available at checkout."
            },
            {
                "question": "What is your return policy?",
                "answer": "We offer a 30-day satisfaction guarantee. If you're not completely happy, contact us for a full refund."
            },
            {
                "question": "Is this product high quality?",
                "answer": "Absolutely! We source only premium materials and each product undergoes rigorous quality control."
            },
            {
                "question": "Do you offer customer support?",
                "answer": "Yes! Our friendly customer support team is available 7 days a week to assist with any questions."
            },
        ]
        
        return faqs
    
    def generate_policies(self, store_name: str) -> Dict:
        """Generate shipping and policy placeholder text"""
        return {
            "shipping_policy": f"""Shipping Policy

{store_name} is committed to delivering your order quickly and safely.

Standard Shipping (5-10 business days): FREE on orders over £40
Express Shipping (2-3 business days): £7.99
Priority Shipping (1-2 business days): £12.99

All orders are processed within 1-2 business days. You will receive a tracking number via email once your order ships.

International shipping is available to select countries. Delivery times and rates vary by destination.""",
            
            "return_policy": f"""Return & Refund Policy

At {store_name}, your satisfaction is our priority.

30-Day Money-Back Guarantee
If you're not completely satisfied with your purchase, you may return it within 30 days for a full refund.

To initiate a return:
1. Contact our customer support team
2. Receive your return authorization
3. Ship the item back in original condition
4. Refund processed within 5-7 business days

Items must be unused and in original packaging. Return shipping costs are the responsibility of the customer unless the item is defective.""",
            
            "privacy_policy": f"""Privacy Policy

{store_name} respects your privacy and is committed to protecting your personal information.

We collect only the information necessary to process your orders and improve your shopping experience. Your data is never sold to third parties.

For questions about our privacy practices, please contact our support team.""",
        }
    
    def generate_shipping_rules(self, product: Dict, supplier: Optional[Dict] = None) -> Dict:
        """Generate shipping rules from supplier data."""
        if supplier:
            ship_min = supplier.get('shipping_days_min', 7)
            ship_max = supplier.get('shipping_days_max', 20)
            ship_cost = supplier.get('estimated_shipping_cost', 0)
            origin = supplier.get('shipping_origin', 'China')
        else:
            ship_min, ship_max, ship_cost, origin = 7, 20, 0, 'Unknown'
        
        retail = product.get('estimated_retail_price', 0)
        free_threshold = round(retail * 1.5, 2) if retail > 20 else 40
        
        return {
            "standard": {
                "name": "Standard Shipping",
                "price": round(max(ship_cost, 3.99), 2),
                "estimated_days": f"{ship_min}-{ship_max}",
                "origin": origin,
            },
            "express": {
                "name": "Express Shipping",
                "price": round(max(ship_cost * 2, 7.99), 2),
                "estimated_days": f"{max(3, ship_min - 4)}-{max(7, ship_max - 7)}",
                "origin": origin,
            },
            "free_shipping_threshold": free_threshold,
            "note": f"Free standard shipping on orders over £{free_threshold:.2f}",
        }
    
    def generate_product_variants(self, product: Dict) -> list:
        """Generate common product variants."""
        category = product.get('category', '').lower()
        retail = product.get('estimated_retail_price', 0)
        
        if 'fashion' in category or 'clothing' in category:
            return [
                {"option": "Size", "values": ["S", "M", "L", "XL"]},
                {"option": "Color", "values": ["Black", "White", "Navy"]},
            ]
        elif 'electronics' in category:
            return [
                {"option": "Color", "values": ["Black", "White"]},
            ]
        elif 'beauty' in category or 'health' in category:
            return [
                {"option": "Size", "values": ["Regular", "Large"]},
            ]
        else:
            return [
                {"option": "Style", "values": ["Standard"]},
            ]
    
    def generate_full_store(self, product: Dict, store_name: Optional[str] = None, supplier: Optional[Dict] = None) -> Dict:
        """
        Generate a complete store draft from a product
        
        Args:
            product: Product data dictionary
            store_name: Optional pre-selected store name
        
        Returns:
            Complete store generation result
        """
        # Generate store names if not provided
        name_suggestions = self.generate_store_names(product)
        selected_name = store_name or name_suggestions[0]
        
        # Generate all content
        tagline = self.generate_tagline(product, selected_name)
        headline = self.generate_headline(product, selected_name)
        product_title = self.generate_product_title(product)
        product_description = self.generate_product_description(product)
        bullet_points = self.generate_bullet_points(product)
        pricing = self.generate_pricing_suggestion(product)
        branding = self.generate_branding(product)
        faqs = self.generate_faq(product)
        policies = self.generate_policies(selected_name)
        shipping_rules = self.generate_shipping_rules(product, supplier)
        variants = self.generate_product_variants(product)
        
        return {
            "store_name_suggestions": name_suggestions,
            "selected_name": selected_name,
            "tagline": tagline,
            "headline": headline,
            "product": {
                "title": product_title,
                "description": product_description,
                "bullet_points": bullet_points,
                "pricing": pricing,
                "variants": variants,
                "original_product_id": product.get('id'),
                "original_product_name": product.get('product_name'),
                "category": product.get('category'),
                "image_url": product.get('image_url'),
                "supplier_link": product.get('supplier_link'),
            },
            "branding": branding,
            "faqs": faqs,
            "policies": policies,
            "shipping_rules": shipping_rules,
            "supplier": {
                "id": supplier.get('id') if supplier else None,
                "source": supplier.get('source') if supplier else None,
                "name": supplier.get('supplier_name') if supplier else None,
                "cost": supplier.get('supplier_cost') if supplier else product.get('supplier_cost', 0),
                "shipping_origin": supplier.get('shipping_origin') if supplier else None,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def create_store_document(
    user_id: str,
    store_name: str,
    generation_result: Dict,
    product: Dict
) -> Dict:
    """Create a store document for MongoDB"""
    store_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    return {
        "id": store_id,
        "owner_id": user_id,
        "name": store_name,
        "tagline": generation_result.get("tagline", ""),
        "headline": generation_result.get("headline", ""),
        "category": product.get("category", "General"),
        "status": "draft",
        "branding": generation_result.get("branding", {}),
        "faqs": generation_result.get("faqs", []),
        "policies": generation_result.get("policies", {}),
        "shipping_rules": generation_result.get("shipping_rules", {}),
        "supplier_info": generation_result.get("supplier", {}),
        "shopify_connected": False,
        "shopify_store_id": None,
        "created_at": now,
        "updated_at": now,
    }


def create_store_product_document(
    store_id: str,
    product: Dict,
    generation_result: Dict
) -> Dict:
    """Create a store product document for MongoDB"""
    product_data = generation_result.get("product", {})
    pricing = product_data.get("pricing", {})
    supplier = generation_result.get("supplier", {})
    
    return {
        "id": str(uuid.uuid4()),
        "store_id": store_id,
        "original_product_id": product.get("id"),
        "title": product_data.get("title", product.get("product_name")),
        "description": product_data.get("description", ""),
        "bullet_points": product_data.get("bullet_points", []),
        "variants": product_data.get("variants", []),
        "price": pricing.get("suggested_price", 0),
        "compare_at_price": pricing.get("compare_at_price", 0),
        "cost": pricing.get("supplier_cost", 0),
        "currency": "GBP",
        "category": product.get("category", "General"),
        "image_url": product.get("image_url"),
        "supplier_link": product.get("supplier_link"),
        "supplier_id": supplier.get("id"),
        "supplier_source": supplier.get("source"),
        "supplier_cost": supplier.get("cost", 0),
        "shipping_origin": supplier.get("shipping_origin"),
        "is_featured": True,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def export_store_for_shopify(store: Dict, products: List[Dict]) -> Dict:
    """
    Export store data in Shopify-compatible format
    Ready for future Shopify API integration
    """
    shopify_products = []
    
    for product in products:
        shopify_product = {
            "title": product.get("title", ""),
            "body_html": product.get("description", "").replace("\n", "<br>"),
            "vendor": store.get("name", ""),
            "product_type": product.get("category", ""),
            "tags": [product.get("category", ""), "trending", "viralscout"],
            "variants": [
                {
                    "price": str(product.get("price", 0)),
                    "compare_at_price": str(product.get("compare_at_price", 0)),
                    "inventory_management": "shopify",
                    "inventory_quantity": 100,
                }
            ],
            "images": [{"src": product.get("image_url")}] if product.get("image_url") else [],
            "status": "draft",
        }
        shopify_products.append(shopify_product)
    
    return {
        "store": {
            "name": store.get("name", ""),
            "description": store.get("tagline", ""),
        },
        "products": shopify_products,
        "export_format": "shopify_api_v2024_01",
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


def export_store_as_shopify_csv(store: Dict, products: List[Dict]) -> str:
    """
    Export store data as Shopify CSV format for import.
    Returns CSV string ready for download.
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Shopify CSV header
    writer.writerow([
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
        'Tags', 'Published', 'Option1 Name', 'Option1 Value',
        'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
        'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service',
        'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping',
        'Variant Taxable', 'Image Src', 'Image Position', 'Image Alt Text',
        'SEO Title', 'SEO Description', 'Cost per item', 'Status'
    ])
    
    for product in products:
        handle = product.get('title', '').lower().replace(' ', '-').replace(',', '').replace('.', '')[:80]
        body_html = product.get('description', '').replace('\n', '<br>')
        bullets = product.get('bullet_points', [])
        if bullets:
            body_html += '<br><ul>' + ''.join(f'<li>{b}</li>' for b in bullets) + '</ul>'
        
        # Get variants
        variants = product.get('variants', [])
        if not variants or len(variants) == 0:
            variants = [{"option": "Title", "values": ["Default"]}]
        
        first_variant = True
        for var in variants:
            for val in var.get('values', ['Default']):
                row = [
                    handle if first_variant else '',
                    product.get('title', '') if first_variant else '',
                    body_html if first_variant else '',
                    store.get('name', '') if first_variant else '',
                    product.get('category', '') if first_variant else '',
                    product.get('category', '') if first_variant else '',
                    f"{product.get('category', '')},trending,trendscout" if first_variant else '',
                    'TRUE' if first_variant else '',
                    var.get('option', 'Title'),
                    val,
                    f'{handle}-{val.lower()}',
                    '0',
                    'shopify',
                    '100',
                    'continue',
                    'manual',
                    str(product.get('price', 0)),
                    str(product.get('compare_at_price', 0)),
                    'TRUE',
                    'TRUE',
                    product.get('image_url', '') if first_variant else '',
                    '1' if first_variant else '',
                    product.get('title', '') if first_variant else '',
                    product.get('title', '')[:70] if first_variant else '',
                    (product.get('description', '')[:160]) if first_variant else '',
                    str(product.get('cost', 0)),
                    'draft',
                ]
                writer.writerow(row)
                first_variant = False
    
    return output.getvalue()


def export_store_for_woocommerce(store: Dict, products: List[Dict]) -> Dict:
    """
    Export store data in WooCommerce-compatible format.
    """
    woo_products = []
    
    for product in products:
        woo_product = {
            "name": product.get("title", ""),
            "type": "simple",
            "regular_price": str(product.get("price", 0)),
            "sale_price": "",
            "description": product.get("description", "").replace("\n", "<br>"),
            "short_description": product.get("bullet_points", [""])[0] if product.get("bullet_points") else "",
            "categories": [{"name": product.get("category", "Uncategorized")}],
            "tags": [{"name": "trending"}, {"name": "trendscout"}],
            "images": [{"src": product.get("image_url")}] if product.get("image_url") else [],
            "manage_stock": True,
            "stock_quantity": 100,
            "status": "draft",
            "meta_data": [
                {"key": "_supplier_link", "value": product.get("supplier_link", "")},
                {"key": "_supplier_cost", "value": str(product.get("cost", 0))},
                {"key": "_compare_at_price", "value": str(product.get("compare_at_price", 0))},
            ],
        }
        
        # Add attributes/variants
        variants = product.get("variants", [])
        if variants and len(variants) > 0 and variants[0].get("values", ["Default"]) != ["Default"]:
            woo_product["type"] = "variable"
            woo_product["attributes"] = []
            for var in variants:
                woo_product["attributes"].append({
                    "name": var.get("option", "Size"),
                    "visible": True,
                    "variation": True,
                    "options": var.get("values", []),
                })
        
        woo_products.append(woo_product)
    
    return {
        "store": {
            "name": store.get("name", ""),
            "description": store.get("tagline", ""),
        },
        "products": woo_products,
        "export_format": "woocommerce_rest_api_v3",
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
