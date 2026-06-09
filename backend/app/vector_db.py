import logging
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    Wrapper around the ChromaDB HTTP client.
    Handles configuration, initial connection verification, and collection retrieval.
    """

    def __init__(self):
        self._client = None

    @property
    def client(self) -> chromadb.HttpClient:
        if self._client is None:
            self.connect()
        return self._client

    def connect(self) -> None:
        """
        Establishes connection to the ChromaDB server container.
        """
        try:
            logger.info(f"Connecting to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}...")
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            # Verify connectivity by fetching heartbeat
            heartbeat = self._client.heartbeat()
            logger.info(f"ChromaDB connection established. Heartbeat: {heartbeat}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            # We don't crash the server start, but we log the critical failure
            self._client = None

    def check_health(self) -> bool:
        """
        Checks if the ChromaDB server is reachable.
        """
        try:
            if self._client is None:
                self.connect()
            if self._client is not None:
                self._client.heartbeat()
                return True
            return False
        except Exception:
            return False


# Singleton client instance
chroma_client = ChromaDBClient()
