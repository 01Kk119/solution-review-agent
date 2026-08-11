import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from siliconflow import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DeepSeekClient,
    DeepSeekError,
)


class FakeResponse:
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(
            {
                "model": "test-model",
                "choices": [
                    {
                        "message": {"content": "评审完成"},
                        "finish_reason": "stop",
                    }
                ],
            }
        ).encode("utf-8")


class DeepSeekRetryTests(unittest.TestCase):
    def test_official_deepseek_defaults(self):
        self.assertEqual("https://api.deepseek.com", DEFAULT_BASE_URL)
        self.assertEqual("deepseek-v4-flash", DEFAULT_MODEL)

    def test_request_uses_official_thinking_schema(self):
        client = DeepSeekClient(api_key="test-api-key-123")

        with patch(
            "siliconflow.urllib.request.urlopen",
            return_value=FakeResponse(),
        ) as urlopen:
            client.chat(
                [{"role": "user", "content": "test"}],
                enable_thinking=False,
            )

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(
            "https://api.deepseek.com/chat/completions",
            request.full_url,
        )
        self.assertEqual({"type": "disabled"}, payload["thinking"])
        self.assertNotIn("enable_thinking", payload)

    def test_request_can_override_timeout_retry_and_callback(self):
        default_retries = []
        request_retries = []
        client = DeepSeekClient(
            api_key="test-api-key-123",
            timeout=180,
            max_retries=2,
            retry_callback=lambda number, maximum, reason: default_retries.append(
                (number, maximum, reason)
            ),
        )

        with (
            patch(
                "siliconflow.urllib.request.urlopen",
                side_effect=[TimeoutError(), FakeResponse()],
            ) as urlopen,
            patch("siliconflow.time.sleep"),
        ):
            client.chat(
                [{"role": "user", "content": "test"}],
                timeout=7,
                max_retries=1,
                retry_callback=lambda number, maximum, reason: request_retries.append(
                    (number, maximum, reason)
                ),
            )

        self.assertEqual(2, urlopen.call_count)
        self.assertTrue(all(call.kwargs["timeout"] == 7 for call in urlopen.call_args_list))
        self.assertEqual([1], [item[0] for item in request_retries])
        self.assertTrue(all(item[1] == 1 for item in request_retries))
        self.assertEqual([], default_retries)

    def test_timeout_retries_at_most_twice_then_succeeds(self):
        retries = []
        client = DeepSeekClient(
            api_key="test-api-key-123",
            timeout=1,
            max_retries=2,
            retry_callback=lambda number, maximum, reason: retries.append(
                (number, maximum, reason)
            ),
        )

        with (
            patch(
                "siliconflow.urllib.request.urlopen",
                side_effect=[TimeoutError(), TimeoutError(), FakeResponse()],
            ) as urlopen,
            patch("siliconflow.time.sleep"),
        ):
            result = client.chat([{"role": "user", "content": "test"}])

        self.assertEqual("评审完成", result.content)
        self.assertEqual(3, urlopen.call_count)
        self.assertEqual([1, 2], [item[0] for item in retries])
        self.assertTrue(all(item[1] == 2 for item in retries))

    def test_three_timeouts_return_clear_failure(self):
        client = DeepSeekClient(
            api_key="test-api-key-123",
            timeout=1,
            max_retries=2,
        )

        with (
            patch(
                "siliconflow.urllib.request.urlopen",
                side_effect=[TimeoutError(), TimeoutError(), TimeoutError()],
            ) as urlopen,
            patch("siliconflow.time.sleep"),
        ):
            with self.assertRaisesRegex(
                DeepSeekError, "连续 3 次未在 1 秒内回复"
            ) as raised:
                client.chat([{"role": "user", "content": "test"}])

        self.assertEqual(3, urlopen.call_count)
        self.assertTrue(raised.exception.retry_exhausted)

    def test_billing_failure_stops_without_retry(self):
        client = DeepSeekClient(
            api_key="test-api-key-123",
            timeout=1,
            max_retries=2,
        )
        error = HTTPError(
            "https://api.deepseek.com/chat/completions",
            402,
            "Payment Required",
            {},
            BytesIO(b'{"message":"insufficient balance"}'),
        )
        with (
            patch("siliconflow.urllib.request.urlopen", side_effect=error) as urlopen,
            patch("siliconflow.time.sleep") as sleep,
        ):
            with self.assertRaisesRegex(DeepSeekError, "立即停止") as raised:
                client.chat([{"role": "user", "content": "test"}])

        self.assertEqual(1, urlopen.call_count)
        sleep.assert_not_called()
        self.assertEqual(402, raised.exception.status)


if __name__ == "__main__":
    unittest.main()
