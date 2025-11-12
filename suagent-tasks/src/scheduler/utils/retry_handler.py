"""
Retry Handler - 重试处理器
"""

import time
import logging
import functools
from typing import Callable, Any, Optional
from enum import Enum

class RetryStrategy(Enum):
    """重试策略枚举"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"

class RetryHandler:
    """重试处理器"""

    def __init__(self, max_retries: int = 3, default_delay: int = 60):
        self.max_retries = max_retries
        self.default_delay = default_delay
        self.logger = logging.getLogger(__name__)

    def retry(
        self,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries: Optional[int] = None,
        delay: Optional[int] = None,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        """
        重试装饰器

        Args:
            strategy: 重试策略
            max_retries: 最大重试次数
            delay: 延迟时间（秒）
            exceptions: 需要重试的异常类型
            on_retry: 重试时的回调函数
            on_failure: 最终失败时的回调函数
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                _max_retries = max_retries if max_retries is not None else self.max_retries
                _delay = delay if delay is not None else self.default_delay

                last_exception = None

                for attempt in range(_max_retries + 1):  # 包括初始尝试
                    try:
                        return func(*args, **kwargs)

                    except exceptions as exc:
                        last_exception = exc

                        if attempt == _max_retries:
                            # 最后一次尝试失败
                            self.logger.error(
                                f"Function {func.__name__} failed after {_max_retries + 1} attempts. "
                                f"Final error: {exc}"
                            )

                            if on_failure:
                                on_failure(exc, attempt, *args, **kwargs)

                            raise

                        # 计算延迟时间
                        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                            sleep_time = _delay * (2 ** attempt)
                        elif strategy == RetryStrategy.LINEAR_BACKOFF:
                            sleep_time = _delay * (attempt + 1)
                        else:  # FIXED_DELAY
                            sleep_time = _delay

                        self.logger.warning(
                            f"Function {func.__name__} failed on attempt {attempt + 1}/{_max_retries + 1}. "
                            f"Error: {exc}. Retrying in {sleep_time} seconds..."
                        )

                        if on_retry:
                            on_retry(exc, attempt, sleep_time, *args, **kwargs)

                        time.sleep(sleep_time)

                # 这里不应该到达，但为了类型安全
                raise last_exception

            return wrapper
        return decorator

    @staticmethod
    def circuit_breaker(
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        熔断器装饰器

        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间
            expected_exception: 预期的异常类型
        """
        def decorator(func: Callable) -> Callable:
            # 熔断器状态
            state = {
                'failure_count': 0,
                'last_failure_time': None,
                'is_open': False
            }

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                current_time = time.time()

                # 检查熔断器是否应该半开/关闭
                if (state['is_open'] and
                    state['last_failure_time'] and
                    current_time - state['last_failure_time'] > recovery_timeout):
                    state['is_open'] = False
                    state['failure_count'] = 0
                    logging.info(f"Circuit breaker for {func.__name__} is now half-open")

                # 如果熔断器打开，直接抛出异常
                if state['is_open']:
                    raise Exception(f"Circuit breaker is open for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    # 成功时重置失败计数
                    state['failure_count'] = 0
                    return result

                except expected_exception as exc:
                    state['failure_count'] += 1
                    state['last_failure_time'] = current_time

                    # 如果失败次数达到阈值，打开熔断器
                    if state['failure_count'] >= failure_threshold:
                        state['is_open'] = True
                        logging.warning(
                            f"Circuit breaker opened for {func.__name__} after "
                            f"{state['failure_count']} failures"
                        )

                    raise

            return wrapper
        return decorator

# 全局重试处理器实例
retry_handler = RetryHandler()

# 常用重试装饰器
database_retry = retry_handler.retry(
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    max_retries=3,
    delay=2,
    exceptions=(ConnectionError, TimeoutError)
)

network_retry = retry_handler.retry(
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    max_retries=5,
    delay=5,
    exceptions=(ConnectionError, TimeoutError, OSError)
)

storage_retry = retry_handler.retry(
    strategy=RetryStrategy.LINEAR_BACKOFF,
    max_retries=3,
    delay=10,
    exceptions=(ConnectionError, TimeoutError, OSError)
)