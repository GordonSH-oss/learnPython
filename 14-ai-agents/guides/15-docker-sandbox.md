# 15 Docker Sandbox

## 学习目标

能够构造最小 Docker 执行参数，理解无网络、只读根文件系统、降权用户、资源限制和临时工作区挂载的组合防护。

## 要看的代码

- `agent_core/sandbox/docker.py`
- `tests/test_sandbox_docker.py`

## 概念模型

Docker 执行器仍只接受结构化请求。`PredefinedCommand` 先经过应用 allowlist，`PythonCode` 写入临时工作区后作为容器内脚本运行。容器不是授权层，镜像也不是自动可信；两者都需要版本固定、扫描和运行时策略。

默认参数应包括 `--network=none`、`--read-only`、`--cap-drop=ALL`、`--security-opt=no-new-privileges`、非 root 用户和明确的资源上限。只挂载临时工作区，不挂载源码树、宿主 secret 或 Docker socket。

## 执行路径

1. 校验策略和请求，拒绝未 allowlist 的命令。
2. 创建临时目录并写入脚本与声明输入。
3. 构造确定性的 Docker 参数列表。
4. 以 `shell=False` 调用 Docker，设置超时和输出上限。
5. 超时取消容器并等待清理。
6. 返回包含镜像引用和限制摘要的结构化结果。

Docker 是可选依赖。没有 Docker 时，命令构造测试仍应运行，集成测试应检测 CLI 和短时 `docker version` 探针后明确 skip。

## 底层机制

`--read-only` 保护容器根文件系统，但可写挂载仍决定实际写入范围；`--network=none` 限制默认出口，却不解决数据授权；丢弃 capabilities 和禁止提权减少内核接口，但不能代替镜像供应链审查。生产部署还应使用固定 digest、资源配额、日志脱敏和宿主节点隔离。

## 检查点与练习

审查一次 `build_docker_args` 的输出：确认没有 `-v` 指向源码树、没有 `--env-file`、没有 socket 挂载，并验证脚本无法联网、不能以 root 运行、不能写入根目录。再比较本机模式和 Docker 模式的威胁模型。

## 常见错误与生产注意

- 以为 Docker 默认等于强隔离，忽略 daemon、内核和节点权限。
- 使用浮动镜像标签，无法重现或回滚执行环境。
- 为方便调试开启网络、特权模式或 Docker socket。
- 将 `network="allow"` 当成普通配置而不经过明确审批。
- 集成测试不可用时静默通过，导致安全能力无人知晓。
