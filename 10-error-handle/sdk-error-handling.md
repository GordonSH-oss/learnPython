结合**SDK 开发场景**，给你一套工业级完整方案：**自定义异常体系 + 错误码绑定 + 分层抛出 + 对外统一捕获 + 文档说明**，适配自研 SDK、工具库、MCP 服务客户端等场景。

# 一、整体设计思路
SDK 核心诉求：
1. 区分 **Python 原生异常** 和 **SDK 业务异常**
2. 每个错误对应**唯一错误码、错误描述、建议方案**
3. 异常分层（基础异常 → 细分业务异常），方便调用方精准捕获
4. 支持错误码查询、日志输出、结构化信息返回
5. 对内统一抛出，对外统一收口，不暴露底层原生异常细节

---

# 二、分步实现（可直接复制到项目）
## 1. 第一步：设计错误码枚举（规范管理）
用 `enum.Enum` 统一维护**错误码 + 文案**，集中管理，便于迭代、查文档、对接前端/服务端。

```python
from enum import Enum

class SdkErrorCode(Enum):
    """SDK 全局错误码枚举"""
    # 通用类 1000~1999
    UNKNOWN_ERROR = (1000, "未知错误")
    PARAM_TYPE_ERROR = (1001, "参数类型非法")
    PARAM_VALUE_ERROR = (1002, "参数值超出范围或格式错误")
    
    # 网络/请求类 2000~2999
    REQUEST_TIMEOUT = (2001, "接口请求超时")
    CONNECTION_FAILED = (2002, "网络连接失败")
    RESPONSE_PARSE_ERROR = (2003, "接口响应数据解析失败")
    
    # 权限/认证类 3000~3999
    AUTH_FAILED = (3001, "密钥/Token 认证失败")
    PERMISSION_DENIED = (3002, "权限不足")
    
    # 业务逻辑类 4000~4999
    RESOURCE_NOT_FOUND = (4001, "目标资源不存在")
    INVALID_KEY_NAME = (4002, "键名不符合命名规范")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
```

- 编码规则：按模块分段，方便归类
- 优势：所有错误码集中一处，不会散落在代码各处

### Enum 使用要点：类、成员和成员属性
上面的 `SdkErrorCode` 继承自 `Enum`。定义枚举时，容易混淆 **枚举类本身** 和 **枚举成员**：

```python
from enum import Enum

class ErrorCode(Enum):
    TYPE_ERR = (1001, "类型错误")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
```

这段代码创建了一个枚举类 `ErrorCode`，其中 `TYPE_ERR` 才是一个具体的枚举成员。`code` 和 `msg` 是在 `__init__` 里绑定到每个枚举成员上的属性，不是绑定到枚举类上的属性。

正确访问方式：

```python
import playground3

err = playground3.ErrorCode.TYPE_ERR

print(err.code)   # 1001
print(err.msg)    # 类型错误
print(err.name)   # TYPE_ERR
print(err.value)  # (1001, "类型错误")
```

如果写成下面这样：

```python
import playground3

e1 = playground3.ErrorCode
print(e1.code)
```

会得到：

```text
AttributeError: type object 'ErrorCode' has no attribute 'code'
```

原因是 `e1` 指向的是枚举类 `ErrorCode`，不是枚举成员。类上有 `TYPE_ERR`，但类本身没有 `code` 属性。应该改成：

```python
print(e1.TYPE_ERR.code)
```

再看另一个错误：

```python
print(e.code)
```

如果前面没有定义过变量 `e`，会得到：

```text
NameError: name 'e' is not defined
```

这个错误和 `Enum` 没有关系，只是普通变量名未定义。可以先赋值：

```python
e = playground3.ErrorCode.TYPE_ERR
print(e.code)
```

用一句话记住：

```python
playground3.ErrorCode              # 枚举类
playground3.ErrorCode.TYPE_ERR     # 枚举成员
playground3.ErrorCode.TYPE_ERR.code  # 枚举成员上的自定义属性
```

### Enum 功能速查和常见坑
`Enum` 适合表达一组固定选项，例如状态、错误码、消息类型、权限类型。用在 SDK 错误码里，最常用的是下面这些能力。

#### 1. 每个成员都有 `name` 和 `value`

```python
from enum import Enum

class Status(Enum):
    SUCCESS = 1
    FAILURE = 2
    PENDING = 3

print(Status.SUCCESS.name)   # SUCCESS
print(Status.SUCCESS.value)  # 1
```

- `name` 是成员名，来自左侧的 `SUCCESS`
- `value` 是成员值，来自右侧的 `1`

#### 2. 通过名字或值反查枚举成员

```python
print(Status["SUCCESS"])  # Status.SUCCESS
print(Status(1))          # Status.SUCCESS
```

注意：如果错误码枚举使用 tuple 作为原始值：

```python
class ErrCode(Enum):
    TYPE_ERR = (1001, "参数类型错误")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
```

此时 `ErrCode.TYPE_ERR.value` 是整个 tuple：

```python
print(ErrCode.TYPE_ERR.value)  # (1001, "参数类型错误")
```

所以不能直接写：

```python
ErrCode(1001)  # 错误：1001 不是完整 value
```

可以自己提供按错误码查找的方法：

```python
class ErrCode(Enum):
    TYPE_ERR = (1001, "参数类型错误")
    TIME_OUT = (2001, "请求超时")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    @classmethod
    def from_code(cls, code):
        for item in cls:
            if item.code == code:
                return item
        raise ValueError(f"未知错误码：{code}")

print(ErrCode.from_code(1001))  # ErrCode.TYPE_ERR
```

#### 3. 遍历枚举成员

```python
for item in ErrCode:
    print(item.name, item.code, item.msg)
```

这适合生成错误码表、文档、日志映射：

```python
error_docs = [
    {"name": item.name, "code": item.code, "message": item.msg}
    for item in ErrCode
]
```

#### 4. tuple 会拆给 `__init__`，list 不会

这是 `Enum` 的特殊规则，不是普通类的规则。

```python
class ErrCode(Enum):
    TYPE_ERR = (1001, "参数类型错误")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
```

tuple 写法会被拆成多个参数：

```python
ErrCode.__init__(self, 1001, "参数类型错误")
```

如果写成 list：

```python
class ErrCode(Enum):
    TYPE_ERR = [1001, "参数类型错误"]

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
```

list 会被当作一个整体参数：

```python
ErrCode.__init__(self, [1001, "参数类型错误"])
```

于是 `code` 收到整个 list，`msg` 缺失，就会报：

```text
TypeError: ErrCode.__init__() missing 1 required positional argument: 'msg'
```

错误码是常量，推荐使用不可变的 tuple，不推荐使用可变的 list。

#### 5. 重复值会变成别名

```python
class HttpStatus(Enum):
    OK = 200
    SUCCESS = 200

print(HttpStatus.SUCCESS is HttpStatus.OK)  # True
print(list(HttpStatus))                     # [<HttpStatus.OK: 200>]
print(HttpStatus.__members__)               # 包含 OK 和 SUCCESS
```

`SUCCESS` 是 `OK` 的别名。遍历 `HttpStatus` 时，只会遍历主成员。

错误码通常要求全局唯一，可以用 `@unique` 强制检查：

```python
from enum import Enum, unique

@unique
class ErrCode(Enum):
    TYPE_ERR = 1001
    TIME_OUT = 2001
```

如果两个成员使用同一个值，类创建时会直接报错。

#### 6. `auto()` 自动生成值

```python
from enum import Enum, auto

class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    PENDING = auto()
```

`auto()` 适合内部状态，不适合对外错误码。错误码是 SDK 对外契约，应该显式写出稳定的数字。

#### 7. `IntEnum` 和 `StrEnum`

如果枚举成员需要像整数一样参与比较，可以用 `IntEnum`：

```python
from enum import IntEnum

class HttpCode(IntEnum):
    OK = 200
    NOT_FOUND = 404

print(HttpCode.OK == 200)  # True
```

如果枚举成员需要像字符串一样使用，可以用 `StrEnum`：

```python
from enum import StrEnum

class MessageType(StrEnum):
    TEXT = "text"
    IMAGE = "image"

print(MessageType.TEXT == "text")  # True
```

普通 `Enum` 更强调类型边界，`IntEnum` 和 `StrEnum` 更方便和外部协议、JSON 字段、HTTP 状态码对接。

#### 8. 用 `__new__` 控制 `.value`

前面的 tuple 写法中，`.value` 是整个 tuple：

```python
ErrCode.TYPE_ERR.value  # (1001, "参数类型错误")
```

如果你希望 `.value` 就是错误码数字，同时又保留 `msg`，可以使用 `__new__`：

```python
class ErrCode(Enum):
    TYPE_ERR = (1001, "参数类型错误")
    TIME_OUT = (2001, "请求超时")

    def __new__(cls, code, msg):
        obj = object.__new__(cls)
        obj._value_ = code
        return obj

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

print(ErrCode.TYPE_ERR.value)  # 1001
print(ErrCode.TYPE_ERR.code)   # 1001
print(ErrCode.TYPE_ERR.msg)    # 参数类型错误
print(ErrCode(1001))           # ErrCode.TYPE_ERR
```

普通错误码枚举可以先用 `__init__` 版本；当你明确需要 `ErrCode(1001)` 这种按错误码反查能力时，再考虑 `__new__` 版本。

#### 9. import 和热更新调试注意

枚举成员属于枚举类，不属于模块顶层：

```python
import playground3

playground3.ErrCode.TYPE_ERR  # 正确
playground3.TYPE_ERR          # 错误
```

如果在交互式 Python 里已经导入过模块，修改文件后再次 `import playground3` 不会重新执行文件。需要重启解释器，或者手动 reload：

```python
import importlib
import playground3

playground3 = importlib.reload(playground3)
```

## 2. 第二步：构建 SDK 异常继承体系
遵循 **「基类统一 + 子类细分」** 原则：
1. 顶层基类：`SdkBaseError`（所有 SDK 异常的父类，调用方捕获这个可兜底所有 SDK 错误）
2. 细分子类：按场景拆分（参数异常、网络异常、认证异常、业务异常）
3. 每个异常内置：**错误码、错误信息、原始异常、附加详情**

```python
class SdkBaseError(Exception):
    """SDK 所有异常的基类（对外统一入口）"""
    def __init__(self, error_code: SdkErrorCode, detail: str = None, origin_exc: Exception = None):
        self.code = error_code.code
        self.msg = error_code.message
        self.detail = detail or ""
        self.origin_exc = origin_exc  # 保存底层原始异常，用于排查问题
        super().__init__(f"[{self.code}] {self.msg} | 详情：{self.detail}")


# ========== 细分业务异常（按需拆分） ==========
class SdkParamError(SdkBaseError):
    """参数相关异常"""
    pass

class SdkNetworkError(SdkBaseError):
    """网络/请求相关异常"""
    pass

class SdkAuthError(SdkBaseError):
    """认证/权限异常"""
    pass

class SdkBusinessError(SdkBaseError):
    """业务逻辑异常"""
    pass
```

### 结构说明
- 所有 SDK 异常都继承 `SdkBaseError`，调用方可以：
  - 精准捕获：`except SdkNetworkError`
  - 兜底捕获：`except SdkBaseError`
- 保留 `origin_exc`：记录底层原生异常（如 `TimeoutError`、`ValueError`），方便日志排障

## 3. 第三步：SDK 内部：原生异常 → 转换为 SDK 自定义异常
SDK 原则：**对内捕获原生异常，对外只抛出 SDK 自定义异常**，屏蔽底层实现。

示例：封装一个 SDK 请求函数 + 参数校验函数
```python
from urllib import request
from urllib.error import URLError

# 模拟 SDK 内部接口调用
def sdk_request(url: str, timeout: int = 10):
    # 1. 参数校验：类型、值校验，抛参数异常
    if not isinstance(url, str):
        raise SdkParamError(
            SdkErrorCode.PARAM_TYPE_ERROR,
            detail=f"url 必须是字符串，当前类型：{type(url)}"
        )
    if timeout <= 0:
        raise SdkParamError(
            SdkErrorCode.PARAM_VALUE_ERROR,
            detail=f"超时时间必须大于0，当前值：{timeout}"
        )

    resp = None
    try:
        resp = request.urlopen(url, timeout=timeout)
        body = resp.read().decode("utf-8")
        return body
    except TimeoutError as e:
        # 原生超时异常 → 转为 SDK 网络异常
        raise SdkNetworkError(
            SdkErrorCode.REQUEST_TIMEOUT,
            detail=f"请求地址：{url}",
            origin_exc=e
        ) from e
    except URLError as e:
        # 原生连接异常 → 转为 SDK 网络异常
        raise SdkNetworkError(
            SdkErrorCode.CONNECTION_FAILED,
            detail=f"请求地址：{url}",
            origin_exc=e
        ) from e
    except Exception as e:
        # 其他未知原生异常 → 统一转为 SDK 未知错误
        raise SdkBaseError(
            SdkErrorCode.UNKNOWN_ERROR,
            detail=f"请求异常：{str(e)}",
            origin_exc=e
        ) from e
    finally:
        if resp:
            resp.close()
```

关键点：
- `from e`：**异常链保留**，追踪完整调用栈，排障必备
- 不对外暴露 `urllib`、`TimeoutError` 等底层细节，调用方只感知 SDK 异常

## 4. 第四步：调用方使用（外部使用者视角）
外部项目引入你的 SDK 后，只需要捕获你定义的异常，按错误码做分支处理。

```python
def main():
    try:
        res = sdk_request("https://example.com", timeout=5)
        print("请求成功：", res[:100])
    except SdkParamError as e:
        # 单独处理参数错误
        print(f"【参数错误】码：{e.code}，信息：{e.msg}，详情：{e.detail}")
    except SdkNetworkError as e:
        # 单独处理网络错误（重试、提示用户）
        print(f"【网络错误】码：{e.code}，信息：{e.msg}")
    except SdkAuthError as e:
        # 单独处理认证错误（重新登录、刷新 Token）
        print(f"【认证失败】请检查密钥配置")
    except SdkBaseError as e:
        # SDK 所有异常兜底
        print(f"【SDK 业务异常】{e.code} | {e.msg}")
    except Exception as e:
        # 非 SDK 原生异常兜底
        print(f"【系统未知异常】{e}")

if __name__ == "__main__":
    main()
```

---

# 三、结合你之前的 FrozenJSON 改造（落地练习）
把这套方案用到你现有的 `FrozenJSON`，做成一个标准 SDK 风格：

```python
from collections import abc
from enum import Enum

# 1. 错误码枚举
class JsonErrorCode(Enum):
    UNKNOWN = (1000, "未知错误")
    INVALID_KEY = (1001, "键名非法，无法使用点语法访问")
    KEY_NOT_FOUND = (1002, "指定键/属性不存在")

    def __init__(self, code, msg):
        self.code = code
        self.message = msg

# 2. 异常体系
class FrozenJsonBaseError(Exception):
    def __init__(self, err_code: JsonErrorCode, detail="", origin=None):
        self.code = err_code.code
        self.msg = err_code.message
        self.detail = detail
        self.origin = origin
        super().__init__(f"[{self.code}] {self.msg} {detail}")

class JsonKeyError(FrozenJsonBaseError):
    pass

# 3. 业务类
class FrozenJSON:
    def __init__(self, mapping):
        self.__data = dict(mapping)
        # 初始化校验键名
        for k in self.__data:
            if not k.isidentifier():
                raise JsonKeyError(
                    JsonErrorCode.INVALID_KEY,
                    detail=f"非法键：{k}，请使用 [] 取值"
                )

    def __getattr__(self, name):
        try:
            return FrozenJSON.build(self.__data[name])
        except KeyError as e:
            raise JsonKeyError(
                JsonErrorCode.KEY_NOT_FOUND,
                detail=f"属性 {name} 不存在",
                origin=e
            ) from e

    def __getitem__(self, key):
        try:
            return FrozenJSON.build(self.__data[key])
        except KeyError as e:
            raise JsonKeyError(
                JsonErrorCode.KEY_NOT_FOUND,
                detail=f"键 {key} 不存在",
                origin=e
            ) from e

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj

# 4. 调用测试
if __name__ == "__main__":
    try:
        fj = FrozenJSON({"2be": "test"})
    except FrozenJsonBaseError as e:
        print(f"错误码：{e.code}，描述：{e.msg}，详情：{e.detail}")
```

---

# 四、SDK 异常进阶规范（生产必用）
## 1. 异常链 `from` 用法
- `raise NewError(...) from old_exc`：保留原始异常栈，日志能看到完整报错链路
- 不要省略，线上排查问题至关重要

## 2. 日志联动
在 SDK 内部统一打日志，输出：错误码、信息、详情、原始异常堆栈：
```python
import logging
logger = logging.getLogger("my_sdk")

# 抛出异常前记录日志
logger.error(
    f"SDK 异常 code={e.code}, msg={e.msg}, detail={e.detail}",
    exc_info=e.origin
)
```

## 3. 错误码设计规范（团队协作）
1. 按**模块/功能**分段编码
   - 通用：1xxx
   - 参数：2xxx
   - 网络：3xxx
   - 认证：4xxx
   - 业务：5xxx
2. 错误码**全局唯一**，不重复
3. 每个错误码必须配套：中文描述 + 触发场景 + 解决方案（写在注释/文档里）

## 4. 对外文档要求
SDK 文档必须列出：
- 所有自定义异常类
- 全部错误码、含义、触发条件、处理建议

## 5. 兼容处理（可选）
如果需要兼容老版本，可以：
- 保留部分原生异常透传
- 增加开关控制异常模式

---

# 五、总结 & 选型口诀
### 什么时候用这套方案？
- 开发 **独立 SDK、类库、客户端、服务组件**（对外提供调用）
- 需要**统一错误码、标准化报错、区分业务/系统错误**
- 多人协作、线上服务、需要日志/监控告警

### 核心流程一句话
1. 枚举管理**错误码 + 文案**
2. 搭建**分层自定义异常**（基类 + 子类）
3. SDK 内部捕获 Python 原生异常，**转换为自有异常**
4. 调用方按「细分异常/基类异常」分层捕获、按错误码分支处理

### 和原生异常的边界
- **SDK 内部**：自由使用 `TypeError`/`ValueError` 做校验，最后统一转成自定义异常
- **SDK 对外**：只抛出自己的异常体系，屏蔽底层细节
