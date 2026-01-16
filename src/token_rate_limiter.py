from __future__ import annotations

from langchain.rate_limiters import BaseRateLimiter

import abc
import asyncio
import threading
import time


class InMemoryTokenAndRequestRateLimiter(BaseRateLimiter):
    """Dual token-bucket limiter: requests/time + tokens/time.

    - Request bucket:
        * Refill at requests_per_second
        * Consume 1 per admitted request
        * Cap at max_request_bucket_size
    - Token bucket (optional):
        * Enabled when tokens_per_second is not None
        * Refill at tokens_per_second
        * Consume token_cost per request (caller-provided)
        * Cap at max_token_bucket_size

    Behavior matches LangChain InMemoryRateLimiter style:
      - thread-safe
      - polling loop with check_every_n_seconds for blocking calls
      - monotonic time base
      - initialize on first call to avoid burst (bucket starts empty)
    """

    def __init__(
        self,
        *,
        # ----- request limiting -----
        requests_per_second: float = 1.0,
        check_every_n_seconds: float = 0.1,
        max_request_bucket_size: float = 1.0,
        # ----- token limiting (optional) -----
        tokens_per_second: float | None = None,
        max_token_bucket_size: float | None = None,
        default_token_cost: float = 0.0,
    ) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0.")
        if check_every_n_seconds <= 0:
            raise ValueError("check_every_n_seconds must be > 0.")
        if max_request_bucket_size < 1:
            raise ValueError("max_request_bucket_size must be >= 1.")
        if default_token_cost < 0:
            raise ValueError("default_token_cost must be >= 0.")

        self.requests_per_second = float(requests_per_second)
        self.check_every_n_seconds = float(check_every_n_seconds)
        self.max_request_bucket_size = float(max_request_bucket_size)

        self.tokens_per_second = None if tokens_per_second is None else float(tokens_per_second)
        self.max_token_bucket_size = (
            None if max_token_bucket_size is None else float(max_token_bucket_size)
        )
        self.default_token_cost = float(default_token_cost)

        if self.tokens_per_second is not None:
            if self.tokens_per_second <= 0:
                raise ValueError("tokens_per_second must be > 0 when enabled.")
            if self.max_token_bucket_size is None or self.max_token_bucket_size <= 0:
                raise ValueError("max_token_bucket_size must be > 0 when token limiting is enabled.")

        # state (stored)
        self.available_requests = 0.0
        self.available_tokens = 0.0
        self.last: float | None = None

        self._lock = threading.Lock()

    def _refill_locked(self, now: float) -> None:
        """Refill both buckets based on elapsed time.

        Called with self._lock held.
        """
        if self.last is None:
            # init on first call to avoid burst
            self.last = now
            return

        elapsed = now - self.last
        if elapsed <= 0:
            return

        # Refill request credits
        self.available_requests += elapsed * self.requests_per_second
        self.available_requests = min(self.available_requests, self.max_request_bucket_size)

        # Refill token credits (if enabled)
        if self.tokens_per_second is not None and self.max_token_bucket_size is not None:
            self.available_tokens += elapsed * self.tokens_per_second
            self.available_tokens = min(self.available_tokens, self.max_token_bucket_size)

        self.last = now

    def _consume_locked(self, *, token_cost: float) -> bool:
        """Try to consume 1 request credit and token_cost token credits.

        Called with self._lock held.
        """
        # Check request budget
        if self.available_requests < 1.0:
            return False

        # Check token budget if enabled and token_cost > 0
        if self.tokens_per_second is not None and self.max_token_bucket_size is not None:
            if token_cost > 0 and self.available_tokens < token_cost:
                return False

        # Commit
        self.available_requests -= 1.0
        if self.tokens_per_second is not None and self.max_token_bucket_size is not None:
            if token_cost > 0:
                self.available_tokens -= token_cost

        return True

    def _try_acquire(self, *, token_cost: float) -> bool:
        """Non-blocking attempt."""
        if token_cost < 0:
            raise ValueError("token_cost must be >= 0.")

        # Impossible case: single request asks more tokens than bucket capacity.
        if (
            self.tokens_per_second is not None
            and self.max_token_bucket_size is not None
            and token_cost > self.max_token_bucket_size
        ):
            return False

        with self._lock:
            now = time.monotonic()
            self._refill_locked(now)
            return self._consume_locked(token_cost=token_cost)

    def acquire(self, *, blocking: bool = True, token_cost: float | None = None) -> bool:
        """Sync acquire.

        If you want token limiting, pass token_cost (estimated).
        If omitted, uses default_token_cost (default 0 => only request limiting).
        """
        cost = self.default_token_cost if token_cost is None else float(token_cost)

        if not blocking:
            return self._try_acquire(token_cost=cost)

        # Deterministic fail-fast if impossible under token bucket.
        if (
            self.tokens_per_second is not None
            and self.max_token_bucket_size is not None
            and cost > self.max_token_bucket_size
        ):
            raise ValueError(
                f"token_cost ({cost}) > max_token_bucket_size ({self.max_token_bucket_size}). "
                "This request can never be admitted."
            )

        while not self._try_acquire(token_cost=cost):
            time.sleep(self.check_every_n_seconds)
        return True

    async def aacquire(self, *, blocking: bool = True, token_cost: float | None = None) -> bool:
        """Async acquire."""
        cost = self.default_token_cost if token_cost is None else float(token_cost)

        if not blocking:
            return self._try_acquire(token_cost=cost)

        if (
            self.tokens_per_second is not None
            and self.max_token_bucket_size is not None
            and cost > self.max_token_bucket_size
        ):
            raise ValueError(
                f"token_cost ({cost}) > max_token_bucket_size ({self.max_token_bucket_size}). "
                "This request can never be admitted."
            )

        while not self._try_acquire(token_cost=cost):
            await asyncio.sleep(self.check_every_n_seconds)
        return True


__all__ = ["InMemoryTokenAndRequestRateLimiter"]
