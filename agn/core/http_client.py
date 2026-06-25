"""
AGN-SDK HTTP 客户端

封装 httpx.AsyncClient，提供连接池、自动重试、统一错误处理等功能。
"""

import logging
from typing import Any

import httpx

from agn.core.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    map_http_status_to_error,
)
from agn.core.retry import retry_on_error

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    异步 HTTP 客户端

    基于 httpx.AsyncClient 封装，提供：
    - 连接池复用
    - 自动重试
    - 统一错误处理
    - 请求/响应日志
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        初始化 HTTP 客户端

        Args:
            base_url: API Base URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            headers: 默认请求头
        """
        self.base_url = base_url or ""
        self.timeout = httpx.Timeout(
            timeout=timeout,
            connect=30.0,
        )
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.default_headers = headers or {}
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """启动客户端（初始化连接池）"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers,
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
                http2=True,
            )

    async def close(self) -> None:
        """关闭客户端（释放连接池）"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncHttpClient":
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """异步上下文管理器出口"""
        await self.close()

    def _get_client(self) -> httpx.AsyncClient:
        """获取客户端实例"""
        if self._client is None:
            raise RuntimeError("HTTP client not started. Call start() first.")
        return self._client

    @retry_on_error(max_attempts=3, delay=2.0)
    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> httpx.Response:
        """
        发送 GET 请求

        Args:
            url: 请求 URL
            headers: 请求头
            params: 查询参数
            timeout: 超时时间

        Returns:
            响应对象

        Raises:
            各种 AGNError 子类
        """
        try:
            client = self._get_client()
            response = await client.get(
                url=url,
                headers=headers,
                params=params,
                timeout=timeout or self.timeout,
            )
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timeout: {url}",
                original_error=e,
            ) from e
        except httpx.ConnectError as e:
            raise NetworkError(
                message=f"Connection error: {url}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            raise NetworkError(
                message=f"HTTP error: {e}",
                original_error=e,
            ) from e

    @retry_on_error(max_attempts=3, delay=2.0)
    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> httpx.Response:
        """
        发送 POST 请求

        Args:
            url: 请求 URL
            headers: 请求头
            json: JSON 请求体
            data: 表单数据
            files: 文件上传
            timeout: 超时时间

        Returns:
            响应对象

        Raises:
            各种 AGNError 子类
        """
        try:
            client = self._get_client()
            response = await client.post(
                url=url,
                headers=headers,
                json=json,
                data=data,
                files=files,
                timeout=timeout or self.timeout,
            )
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timeout: {url}",
                original_error=e,
            ) from e
        except httpx.ConnectError as e:
            raise NetworkError(
                message=f"Connection error: {url}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            raise NetworkError(
                message=f"HTTP error: {e}",
                original_error=e,
            ) from e

    @retry_on_error(max_attempts=3, delay=2.0)
    async def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> httpx.Response:
        """
        发送 DELETE 请求

        Args:
            url: 请求 URL
            headers: 请求头
            timeout: 超时时间

        Returns:
            响应对象
        """
        try:
            client = self._get_client()
            response = await client.delete(
                url=url,
                headers=headers,
                timeout=timeout or self.timeout,
            )
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timeout: {url}",
                original_error=e,
            ) from e
        except httpx.HTTPError as e:
            raise NetworkError(
                message=f"HTTP error: {e}",
                original_error=e,
            ) from e

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """
        处理响应，检查错误状态码

        Args:
            response: 响应对象

        Returns:
            响应对象

        Raises:
            各种 AGNError 子类
        """
        # 尝试解析响应体
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text

        # 检查状态码
        if response.status_code >= 400:
            error = map_http_status_to_error(response.status_code, response_body)

            # 特殊处理认证错误
            if response.status_code == 401:
                raise AuthenticationError(
                    message="Authentication failed. Please check your API key.",
                    details={"status_code": response.status_code},
                )

            # 特殊处理限流
            if response.status_code == 429:
                raise RateLimitError(
                    message="Rate limit exceeded. Please slow down your requests.",
                    details={"status_code": response.status_code},
                )

            raise error

        return response
