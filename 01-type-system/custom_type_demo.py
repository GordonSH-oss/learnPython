"""使用自定义类型的可运行示例。"""

import custom_types as _t


def build_request(
    method: _t.HttpMethod,
    url: _t.Url,
    params: _t.QueryParams | None = None,
    options: _t.RequestOptions | None = None,
) -> str:
    timeout = options.get("timeout", 5.0) if options else 5.0
    return f"{method} {url}, params={params}, timeout={timeout}"


def find_user(user_id: _t.UserId) -> str:
    return f"user-{user_id}"


request_text = build_request(
    "GET",
    "https://example.com",
    params={"page": 1, "active": True},
    options={"timeout": 3.0, "follow_redirects": True},
)
user_name = find_user(_t.UserId(42))

print(request_text)
print(user_name)

