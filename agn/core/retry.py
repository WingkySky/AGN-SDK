"""
AGN-SDK 重试机制

提供声明式的重试装饰器，支持指数退避策略。
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from agn.core.errors import (
    APIError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)

logger = logging.getLogger(__name__)

# 类型变量
F = TypeVar("F", bound=Callable[..., Any])


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 2.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    exceptions: tuple[type[Exception], ...] | None = None,
) -> Callable[[F], F]:
    """
    重试装饰器

    使用 tenacity 实现，支持指数退避策略。

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        max_delay: 最大延迟（秒）
        multiplier: 延迟倍数
        exceptions: 需要重试的异常类型

    Returns:
        装饰器函数

    Example:
        @retry_on_error(max_attempts=3, delay=2.0)
        async def fetch_data():
            ...
    """
    if exceptions is None:
        exceptions = (
            APIError,
            NetworkError,
            TimeoutError,
            RateLimitError,
        )

    return retry(
        retry=retry_if_exception_type(exceptions),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=multiplier,
            min=delay,
            max=max_delay,
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying after error: {retry_state.outcome.exception() if retry_state.outcome else 'unknown'}, "
            f"attempt {retry_state.attempt_number}/{max_attempts}"
        ),
    )


def retry_async(
    func: F | None = None,
    *,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 30.0,
    retriable_errors: tuple[type[Exception], ...] = (
        TimeoutError,
        NetworkError,
        RateLimitError,
    ),
) -> Callable[[F], F] | Callable[[F], Any]:
    """
    异步重试装饰器（不使用 tenacity）

    简单实现，支持指数退避。

    Args:
        func: 被装饰的函数
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避倍数
        max_delay: 最大延迟（秒）
        retriable_errors: 可重试的错误类型

    Returns:
        装饰后的函数
    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await f(*args, **kwargs)
                except retriable_errors as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {f.__name__}: {e}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {f.__name__}: {e}. "
                        f"Retrying in {current_delay}s..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay = min(current_delay * backoff, max_delay)

                except Exception as e:
                    # 非可重试错误，直接抛出
                    logger.error(f"Non-retriable error in {f.__name__}: {e}")
                    raise

        return wrapper  # type: ignore

    # 支持有参数和无参数调用
    if func is None:
        return decorator
    return decorator(func)
