# 错误处理

错误处理不是“把异常抓住”。真正目标是让程序在失败时仍然可理解、可恢复、可排查。

## 本目录文件

- `exception-basics.md` / `basics.py`：基础异常语法、异常层次、`raise` 和异常链。
- `context-managers.md` / `context_manager.py`：上下文管理器、资源释放和异常传播。
- `sdk-error-handling.md` / `sdk_example.py`：SDK 风格的错误码、自定义异常和对外错误边界。

## 学习顺序

1. 先读 `exception-basics.md`，运行 `python 10-error-handle/basics.py`。
2. 再读 `context-managers.md`，运行 `python 10-error-handle/context_manager.py`。
3. 最后读 `sdk-error-handling.md`，运行 `python 10-error-handle/sdk_example.py`。

## 关键原则

- 只捕获你能处理的异常。
- 不要裸 `except:`，避免吞掉 `KeyboardInterrupt` 和 `SystemExit`。
- 转换异常时使用 `raise NewError(...) from exc` 保留原因链。
- 库和 SDK 对外应该抛稳定的自定义异常，而不是泄露底层实现细节。
- 日志里记录错误原因，但不要记录完整密钥、token 或敏感请求体。

## 练习

1. 给 `sdk_example.py` 增加 `SdkRateLimitError`。
2. 给每个异常增加 `to_dict()`，方便 API 层返回 JSON。
3. 用 `contextmanager` 包装一次 SDK 调用，统一记录开始、成功、失败和耗时。
