import time
import logging
from collections import OrderedDict
from typing import Optional, Tuple
from threading import Lock

logger = logging.getLogger(__name__)


class DNSCache:
    def __init__(
        self, max_size: Optional[int] = None, enable_logging: bool = False
    ) -> None:
        self._store: "OrderedDict[Tuple[str, str, str], Tuple[bytes, float]]" = (
            OrderedDict()
        )
        self.max_size = max_size
        self.enable_logging = enable_logging
        self._lock = Lock()

    def get(self, key: Tuple[str, str, str]) -> Optional[bytes]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            response, expiry = entry
            if time.time() > expiry:
                del self._store[key]
                if self.enable_logging:
                    logger.debug(f'msg="Cache expired" key={key}')
                return None
            if self.max_size is not None:
                self._store.move_to_end(key)  # LRU update
            if self.enable_logging:
                logger.debug(f'msg="Cache hit" key={key}')
            return response

    def set(self, key: Tuple[str, str, str], response: bytes, ttl: int) -> None:
        expiry = time.time() + ttl
        with self._lock:
            if key in self._store:
                del self._store[key]
            elif self.max_size is not None and len(self._store) >= self.max_size:
                evicted_key, _ = self._store.popitem(last=False)
                if self.enable_logging:
                    logger.debug(f'msg="Cache evicted" key={evicted_key}')
            self._store[key] = (response, expiry)
            if self.enable_logging:
                logger.debug(f'msg="Cache set" key={key} ttl={ttl}s')

    def __contains__(self, key: Tuple[str, str, str]) -> bool:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            _, expiry = entry
            if time.time() > expiry:
                del self._store[key]
                return False
            return True

    def cleanup(self) -> None:
        now = time.time()
        with self._lock:
            expired_keys = [k for k, (_, expiry) in self._store.items() if expiry < now]
            for k in expired_keys:
                del self._store[k]
                if self.enable_logging:
                    logger.debug(f'msg="Cache cleaned" key={k}')
