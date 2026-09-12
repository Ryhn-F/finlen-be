import logging
from typing import Any

from supabase import Client, create_client

from finlen_be.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase_client() -> Client | None:
    """Get the Supabase client singleton, used for generating storage public URLs.

    Returns None if SUPABASE_URL / SUPABASE_KEY are not configured, so callers
    must handle the disabled case gracefully.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.warning(
            "SUPABASE_URL/SUPABASE_KEY not configured. Supabase storage features are disabled."
        )
        return None

    try:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", e)
        return None
