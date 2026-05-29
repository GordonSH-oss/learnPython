"""
SDK 异常体系完整示例 - 对应 sdk-error-handling.md
运行：python sdk_example.py
"""

from enum import Enum
from urllib import request
from urllib.error import URLError


# ── 1. 错误码枚举 ─────────────────────────────────────────────────────────────

class SdkErrorCode(Enum):
    UNKNOWN_ERROR        = (1000, "未知错误")
    PARAM_TYPE_ERROR     = (1001, "参数类型非法")
    PARAM_VALUE_ERROR    = (1002, "参数值超出范围或格式错误")
    REQUEST_TIMEOUT      = (2001, "接口请求超时")
    CONNECTION_FAILED    = (2002, "网络连接失败")
    RESPONSE_PARSE_ERROR = (2003, "接口响应数据解析失败")
    AUTH_FAILED          = (3001, "密钥/Token 认证失败")
    PERMISSION_DENIED    = (3002, "权限不足")
    RESOURCE_NOT_FOUND   = (4001, "目标资源不存在")
    INVALID_KEY_NAME     = (4002, "键名不符合命名规范")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# ── 2. 异常体系 ───────────────────────────────────────────────────────────────

class SdkBaseError(Exception):
    def __init__(self, error_code: SdkErrorCode, detail: str = None, origin_exc: Exception = None):
        self.code = error_code.code
        self.msg = error_code.message
        self.detail = detail or ""
        self.origin_exc = origin_exc
        super().__init__(f"[{self.code}] {self.msg} | 详情：{self.detail}")

class SdkParamError(SdkBaseError):
    pass

class SdkNetworkError(SdkBaseError):
    pass

class SdkAuthError(SdkBaseError):
    pass

class SdkBusinessError(SdkBaseError):
    pass


# ── 3. SDK 内部：封装请求，转换原生异常 ───────────────────────────────────────

def sdk_request(url: str, timeout: int = 10) -> str:
    if not isinstance(url, str):
        raise SdkParamError(
            SdkErrorCode.PARAM_TYPE_ERROR,
            detail=f"url 必须是字符串，当前类型：{type(url).__name__}"
        )
    if timeout <= 0:
        raise SdkParamError(
            SdkErrorCode.PARAM_VALUE_ERROR,
            detail=f"超时时间必须大于0，当前值：{timeout}"
        )

    resp = None
    try:
        resp = request.urlopen(url, timeout=timeout)
        return resp.read().decode("utf-8")
    except TimeoutError as e:
        raise SdkNetworkError(SdkErrorCode.REQUEST_TIMEOUT, detail=f"请求地址：{url}", origin_exc=e) from e
    except URLError as e:
        raise SdkNetworkError(SdkErrorCode.CONNECTION_FAILED, detail=f"请求地址：{url}", origin_exc=e) from e
    except Exception as e:
        raise SdkBaseError(SdkErrorCode.UNKNOWN_ERROR, detail=str(e), origin_exc=e) from e
    finally:
        if resp:
            resp.close()


# ── 4. 调用方使用 ─────────────────────────────────────────────────────────────

def call_sdk(url, timeout=5):
    try:
        res = sdk_request(url, timeout=timeout)
        print(f"  成功：{res[:80]}...")
    except SdkParamError as e:
        print(f"  [参数错误] {e.code}: {e.msg} — {e.detail}")
    except SdkNetworkError as e:
        print(f"  [网络错误] {e.code}: {e.msg} — {e.detail}")
    except SdkAuthError as e:
        print(f"  [认证失败] 请检查密钥配置")
    except SdkBaseError as e:
        print(f"  [SDK异常]  {e.code}: {e.msg}")
    except Exception as e:
        print(f"  [系统异常] {e}")


print("=== 参数类型错误 ===")
call_sdk(url=12345)

print("\n=== 参数值错误 ===")
call_sdk(url="https://example.com", timeout=-1)

print("\n=== 网络连接失败 ===")
call_sdk(url="http://localhost:19999/nonexistent")

print("\n=== 正常请求 ===")
call_sdk(url="https://httpbin.org/get", timeout=10)
