"""A testable API client skeleton with timeout, retry, and error boundaries.

The default transport is fake, so this file runs without network access.

Run:
    python 04-api-integration/resilient_api_client.py
"""

from __future__ import annotations

from dataclasses import dataclass
import time


class ApiClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    body: dict[str, object]


class FakeTransport:
    def __init__(self) -> None:
        self.calls = 0

    def post_json(self, url: str, payload: dict[str, object], timeout: float) -> ApiResponse:
        self.calls += 1
        if self.calls == 1:
            return ApiResponse(503, {"error": "temporary_unavailable"})
        return ApiResponse(200, {"message": payload["message"]})


class ResilientApiClient:
    def __init__(self, base_url: str, transport: FakeTransport, retries: int = 2) -> None:
        self.base_url = base_url.rstrip("/")
        self.transport = transport
        self.retries = retries

    def send_message(self, message: str) -> dict[str, object]:
        payload = {"message": message}
        last_status = 0
        for attempt in range(1, self.retries + 2):
            response = self.transport.post_json(f"{self.base_url}/messages", payload, timeout=10)
            last_status = response.status_code
            if response.status_code < 500:
                if response.status_code >= 400:
                    raise ApiClientError(f"request failed: HTTP {response.status_code} {response.body}")
                return response.body
            time.sleep(0.1 * attempt)
        raise ApiClientError(f"request failed after retries: HTTP {last_status}")


def main() -> None:
    client = ResilientApiClient("https://api.example.com/v1", FakeTransport())
    print(client.send_message("hello"))


if __name__ == "__main__":
    main()
