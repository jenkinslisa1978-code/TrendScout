"""
Product Identity & Deduplication System

Merges duplicate products from multiple sources into canonical records while
preserving source-level signals and data provenance.
"""

from .matcher import ProductMatcher
from .merger import ProductMerger
from .identity_service import ProductIdentityService

__all__ = [
    'ProductMatcher',
    'ProductMerger',
    'ProductIdentityService'
]
