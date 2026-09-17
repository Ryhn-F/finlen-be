import logging

from finlen_be.core.config import settings
from finlen_be.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class StorageService:
    """Resolves Supabase Storage file paths into publicly accessible URLs."""

    def get_public_url(self, file_path: str | None) -> str | None:
        """Return the public URL for a file stored in the configured Supabase bucket.

        Returns None if the file_path is empty or the Supabase client is unavailable,
        so callers can fail soft rather than raising on missing configuration.
        """
        if not file_path:
            return None

        client = get_supabase_client()
        if client is None:
            return None

        try:
            return client.storage.from_("materials").get_public_url(file_path)
        except Exception as e:
            logger.error("Failed to build public URL for file '%s': %s", file_path, e)
            return None


storage_service = StorageService()
