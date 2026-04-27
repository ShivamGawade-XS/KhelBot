"""
KhelBot Database Client — Singleton Supabase connection.
"""

from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_KEY
from utils.logger import setup_logger

log = setup_logger("database")

# Singleton Supabase client
_client: Client = None


def get_client() -> Client:
    """
    Get or create the Supabase client singleton.
    
    Returns:
        Supabase Client instance
    """
    global _client
    
    if _client is None:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
            log.info("Supabase client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    return _client
