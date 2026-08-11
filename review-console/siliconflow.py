from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


class SiliconFlowError(RuntimeError):
    def __init__(
        self,
        message: str,
        status: int | None = None,
        *,
        retry_exhausted: bool = False,
    ):
        super().__init__(message)
        self.status = status
        self.retry_exhausted = retry_exhausted


@dataclass
class ChatResult:
    content: str
    model: str
    trace_id: str
    usage: dict[str, Any]
    finish_reason: str


class SiliconFlowClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 180,
        max_retries: int = 2,
        retry_callback: Callable[[int, int, str], None] | None = None,
    ):
        self.api_key = (
            api_key
            or os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("SILICONFLOW_API_KEY", "")
        ).strip()
        self.base_url = (
            base_url or os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.model = (
            model or os.environ.get("DEEPSEEK_MODEL") or DEFAULT_MODEL
        ).strip()
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self.retry_callback = retry_callback

    def _notify_retry(self, retry_number: int, reason: str) -> None:
        if self.retry_callback is not None:
            self.retry_callback(retry_number, self.max_retries, reason)

    @property
    def configured(self) -> bool:
        return len(self.api_key) >= 12 and not any(ord(char) < 32 for char in self.api_key)

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 4000,
        temperature: float = 0.2,
        enable_thinking: bool = False,
        timeout: int | None = None,
        max_retries: int | None = None,
        retry_callback: Callable[[int, int, str], None] | None = None,
    ) -> ChatResult:
        if not self.configured:
            raise SiliconFlowError("DeepSeek API 未配置，请先运行“设置智谱API.cmd”。")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "thinking": {
                "type": "enabled" if enable_thinking else "disabled",
            },
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        request_timeout = self.timeout if timeout is None else max(1, timeout)
        request_max_retries = self.max_retries if max_retries is None else max(0, max_retries)
        request_retry_callback = retry_callback or self.retry_callback

        def notify_retry(retry_number: int, reason: str) -> None:
            if request_retry_callback is not None:
                request_retry_callback(retry_number, request_max_retries, reason)

        total_attempts = request_max_retries + 1
        for attempt in range(total_attempts):
            try:
                with urllib.request.urlopen(request, timeout=request_timeout) as response:
                    raw = response.read().decode("utf-8")
                    body = json.loads(raw)
                    choices = body.get("choices") or []
                    if not choices:
                        raise SiliconFlowError("API 返回中没有 choices。")
                    message = choices[0].get("message") or {}
                    content = message.get("content")
                    if not isinstance(content, str) or not content.strip():
                        raise SiliconFlowError("API 返回内容为空。")
                    return ChatResult(
                        content=content.strip(),
                        model=body.get("model") or self.model,
                        trace_id=(
                            response.headers.get("x-request-id", "")
                            or response.headers.get("x-ds-request-id", "")
                            or body.get("id", "")
                        ),
                        usage=body.get("usage") or {},
                        finish_reason=choices[0].get("finish_reason") or "",
                    )
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:800]
                if exc.code in {429, 503, 504} and attempt < request_max_retries:
                    notify_retry(
                        attempt + 1,
                        f"模型服务返回 HTTP {exc.code}",
                    )
                    time.sleep(1.5 * (attempt + 1))
                    continue
                messages_by_status = {
                    401: "API Key 无效或已失效。",
                    402: "API 账户余额不足或计费被拒绝；已立即停止，不会自动重试。",
                    403: "当前 API Key 无权访问所选模型。",
                    404: "API 地址或模型不存在。",
                    429: "API 请求达到限流，请稍后重试。",
                    503: "模型服务暂时过载。",
                    504: "模型服务响应超时。",
                }
                raise SiliconFlowError(
                    f"{messages_by_status.get(exc.code, 'DeepSeek API 请求失败')} HTTP {exc.code}：{detail}",
                    exc.code,
                    retry_exhausted=exc.code in {429, 503, 504},
                ) from exc
            except urllib.error.URLError as exc:
                if attempt < request_max_retries:
                    notify_retry(
                        attempt + 1,
                        f"模型服务连接异常：{exc.reason}",
                    )
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise SiliconFlowError(
                    f"无法连接 DeepSeek API：{exc.reason}",
                    retry_exhausted=True,
                ) from exc
            except (TimeoutError, ConnectionError, OSError) as exc:
                if attempt < request_max_retries:
                    notify_retry(
                        attempt + 1,
                        f"{request_timeout} 秒内未收到模型回复",
                    )
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise SiliconFlowError(
                    f"模型连续 {total_attempts} 次未在 {request_timeout} 秒内回复。",
                    retry_exhausted=True,
                ) from exc
            except json.JSONDecodeError as exc:
                raise SiliconFlowError("DeepSeek API 返回了无法解析的 JSON。") from exc

        raise SiliconFlowError("DeepSeek API 调用失败。")


# 兼容既有导入路径；新代码使用 DeepSeek 命名。
DeepSeekClient = SiliconFlowClient
DeepSeekError = SiliconFlowError
