from enum import Enum

class ErrCode(Enum):
    # 右侧是列表
    TYPE_ERR = (1001, "参数类型错误")
    TIME_OUT = (2001, "请求超时")

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

