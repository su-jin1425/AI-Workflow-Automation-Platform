import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetryExhaustedError(RuntimeError):
    pass


async def execute_with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    backoff_seconds: int = 2,
    timeout_seconds: int = 60,
) -> T:
    last_exception: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await asyncio.wait_for(
                operation(),
                timeout=timeout_seconds,
            )

        except Exception as exc:
            last_exception = exc

            if attempt >= max_attempts:
                break

            await asyncio.sleep(
                backoff_seconds * (2 ** (attempt - 1))
            )

    raise RetryExhaustedError(
        f"Execution failed after {max_attempts} attempts"
    ) from last_exception