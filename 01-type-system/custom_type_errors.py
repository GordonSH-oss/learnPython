"""供 mypy 检查的反例；这个文件故意包含类型错误。"""

import custom_types as _t
from custom_type_demo import build_request, find_user


bad_method: _t.HttpMethod = "PATCH"
bad_params: _t.QueryParams = {"tags": ["python", "typing"]}

build_request(bad_method, "example.com", bad_params)
find_user(42)

