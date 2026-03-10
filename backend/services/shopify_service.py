"""
Shopify Integration Service

Complete implementation for Shopify OAuth and product publishing.
Requires SHOPIFY_API_KEY, SHOPIFY_API_SECRET, and store-specific access tokens.

OAuth Flow:
1. User initiates connection via /api/shopify/connect
2. Redirect to Shopify OAuth consent screen
3. Shopify redirects back with authorization code
4. Exchange code for permanent access token
5. Store token securely in user profile

Usage:
- EXPORT: Generate Shopify-compatible JSON for manual upload (works now)
- PUBLISH: Direct API publish (requires credentials)
"""

import os
import hmac
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from urllib.parse import urlencode
import aiohttp

# Configuration - set via environment variables
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_SCOPES = 'write_products,read_products,write_inventory,read_inventory'
SHOPIFY_API_VERSION = '2024-01'


def is_shopify_configured() -> bool:
    """Check if Shopify API credentials are configured"""
    return bool(SHOPIFY_API_KEY and SHOPIFY_API_SECRET)


def get_oauth_url(shop_domain: str, redirect_uri: str, state: str) -> str:
    """
    Generate Shopify OAuth authorization URL
    
    Args:
        shop_domain: The myshopify.com domain (e.g., 'mystore.myshopify.com')
        redirect_uri: URL to redirect after authorization
        state: Random state parameter for CSRF protection
        
    Returns:
        Full OAuth URL to redirect user to
    """
    if not is_shopify_configured():
        raise ValueError("Shopify API credentials not configured")
    
    params = {
        'client_id': SHOPIFY_API_KEY,
        'scope': SHOPIFY_SCOPES,
        'redirect_uri': redirect_uri,
        'state': state,
    }
    
    return f"https://{shop_domain}/admin/oauth/authorize?{urlencode(params)}"


async def exchange_code_for_token(shop_domain: str, code: str) -> Dict:
    """
    Exchange authorization code for permanent access token
    
    Args:
        shop_domain: The myshopify.com domain
        code: Authorization code from OAuth callback
        
    Returns:
        Dict with access_token and scope
    """
    if not is_shopify_configured():
        raise ValueError("Shopify API credentials not configured")
    
    url = f"https://{shop_domain}/admin/oauth/access_token"
    
    payload = {
        'client_id': SHOPIFY_API_KEY,
        'client_secret': SHOPIFY_API_SECRET,
        'code': code,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error = await response.text()
                raise Exception(f"Failed to exchange code: {error}")
            
            return await response.json()


def verify_webhook_signature(data: bytes, hmac_header: str) -> bool:
    """
    Verify Shopify webhook signature
    
    Args:
        data: Raw request body
        hmac_header: X-Shopify-Hmac-SHA256 header value
        
    Returns:
        True if signature is valid
    """
    if not SHOPIFY_API_SECRET:
        return False
    
    calculated = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated, hmac_header)


class ShopifyPublisher:
    """
    Handles publishing products to Shopify stores
    """
    
    def __init__(self, shop_domain: str, access_token: str):
        """
        Initialize publisher with store credentials
        
        Args:
            shop_domain: The myshopify.com domain
            access_token: Store's permanent access token
        """
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = SHOPIFY_API_VERSION
        self.base_url = f"https://{shop_domain}/admin/api/{self.api_version}"
    
    async def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Shopify API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                result = await response.json()
                
                if response.status >= 400:
                    raise Exception(f"Shopify API error: {result}")
                
                return result
    
    async def create_product(self, product_data: Dict) -> Dict:
        """
        Create a product in Shopify
        
        Args:
            product_data: Shopify-format product data
            
        Returns:
            Created product data from Shopify
        """
        return await self._request('POST', 'products.json', {'product': product_data})
    
    async def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """Update an existing Shopify product"""
        return await self._request('PUT', f'products/{product_id}.json', {'product': product_data})
    
    async def get_product(self, product_id: str) -> Dict:
        """Get a product by ID"""
        return await self._request('GET', f'products/{product_id}.json')
    
    async def list_products(self, limit: int = 50) -> Dict:
        """List products from the store"""
        return await self._request('GET', f'products.json?limit={limit}')
    
    async def delete_product(self, product_id: str) -> None:
        """Delete a product"""
        await self._request('DELETE', f'products/{product_id}.json')
    
    async def publish_store_products(self, store_products: List[Dict]) -> Dict:
        """
        Publish multiple products from a ViralScout store to Shopify
        
        Args:
            store_products: List of store_product documents
            
        Returns:
            Summary of publish results
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(store_products),
        }
        
        for product in store_products:
            shopify_product = format_product_for_shopify(product)
            
            try:
                created = await self.create_product(shopify_product)
                results['success'].append({
                    'viralscout_id': product.get('id'),
                    'shopify_id': created.get('product', {}).get('id'),
                    'title': product.get('title'),
                })
            except Exception as e:
                results['failed'].append({
                    'viralscout_id': product.get('id'),
                    'title': product.get('title'),
                    'error': str(e),
                })
        
        return results


def format_product_for_shopify(store_product: Dict, vendor: str = "ViralScout Store") -> Dict:
    """
    Convert ViralScout store product to Shopify product format
    
    Args:
        store_product: Store product document from MongoDB
        vendor: Store name to use as vendor
        
    Returns:
        Shopify-compatible product dict
    """
    # Format description as HTML
    description = store_product.get('description', '')
    bullet_points = store_product.get('bullet_points', [])
    
    body_html = f"<p>{description}</p>"
    if bullet_points:
        body_html += "<ul>"
        for point in bullet_points:
            body_html += f"<li>{point}</li>"
        body_html += "</ul>"
    
    # Build product structure
    product = {
        'title': store_product.get('title', 'Product'),
        'body_html': body_html,
        'vendor': vendor,
        'product_type': store_product.get('category', 'General'),
        'tags': [
            store_product.get('category', ''),
            'trending',
            'viralscout',
        ],
        'status': 'draft',  # Always start as draft for safety
        'variants': [
            {
                'price': str(store_product.get('price', 0)),
                'compare_at_price': str(store_product.get('compare_at_price', 0)) if store_product.get('compare_at_price') else None,
                'inventory_management': 'shopify',
                'inventory_quantity': 100,
                'requires_shipping': True,
                'taxable': True,
            }
        ],
    }
    
    # Add images if available
    image_url = store_product.get('image_url')
    if image_url:
        product['images'] = [{'src': image_url}]
    
    return product


def format_store_for_export(store: Dict, products: List[Dict]) -> Dict:
    """
    Format complete store for Shopify-compatible export
    
    Args:
        store: Store document
        products: List of store_product documents
        
    Returns:
        Complete export dict ready for Shopify import
    """
    shopify_products = []
    
    for product in products:
        shopify_product = format_product_for_shopify(product, store.get('name', 'ViralScout Store'))
        shopify_products.append(shopify_product)
    
    return {
        'store': {
            'name': store.get('name', ''),
            'description': store.get('tagline', ''),
        },
        'products': shopify_products,
        'export_format': 'shopify_api_v2024_01',
        'export_version': '1.0',
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'instructions': {
            'manual_import': [
                '1. Log in to your Shopify admin',
                '2. Go to Products > Import',
                '3. Upload this file or copy product data',
                '4. Review and publish products',
            ],
            'api_import': [
                '1. Configure Shopify credentials in ViralScout',
                '2. Use Direct Publish feature',
                '3. Products will be created as drafts',
                '4. Review and activate in Shopify admin',
            ],
        },
    }


# Shopify connection status helpers
def get_connection_status(user_profile: Dict) -> Dict:
    """
    Get Shopify connection status for a user
    
    Args:
        user_profile: User profile document
        
    Returns:
        Connection status dict
    """
    shopify_data = user_profile.get('shopify', {})
    
    if not shopify_data:
        return {
            'connected': False,
            'shop_domain': None,
            'can_publish': False,
            'message': 'Shopify not connected. Connect your store to enable direct publishing.',
        }
    
    return {
        'connected': True,
        'shop_domain': shopify_data.get('shop_domain'),
        'connected_at': shopify_data.get('connected_at'),
        'can_publish': bool(shopify_data.get('access_token')),
        'message': f"Connected to {shopify_data.get('shop_domain')}",
    }


async def test_connection(shop_domain: str, access_token: str) -> Dict:
    """
    Test if Shopify connection is working
    
    Args:
        shop_domain: The myshopify.com domain
        access_token: Store's access token
        
    Returns:
        Test result dict
    """
    try:
        publisher = ShopifyPublisher(shop_domain, access_token)
        result = await publisher._request('GET', 'shop.json')
        
        return {
            'success': True,
            'shop_name': result.get('shop', {}).get('name'),
            'shop_email': result.get('shop', {}).get('email'),
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }
