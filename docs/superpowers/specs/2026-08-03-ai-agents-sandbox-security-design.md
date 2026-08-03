# 14-ai-agents 安全专题与 Sandbox 设计

## 背景与目标

`14-ai-agents` 已覆盖 Agent loop、工具、记忆、RAG、持久执行、Multi-agent、评测和可观测性。当前 `controlled_read()` 只解决允许目录之外的路径逃逸，不构成可执行代码的进程隔离，也没有统一说明 CPU、内存、进程数、输出、网络、环境变量和宿主凭据边界。

本次补充把安全内容扩展为一个连续的小单元，并实现一个统一的 Sandbox 教学接口。学习者应能区分模型安全提示、工具授权、数据隔离和执行隔离，理解本机进程 sandbox 与 Docker sandbox 的能力边界，并用攻击性测试验证约束确实生效。

## 课程结构

现有 01-11 保持不变，后续章节整体重新编号为：

- 12：威胁建模、Prompt Injection 与纵深防御
- 13：Sandbox 原理与策略
- 14：本机进程 Sandbox 实验
- 15：Docker Sandbox 实验
- 16：身份、数据与供应链安全
- 17：可观测性与生产工程
- 18：综合项目：可恢复的研究助手

README 的课程目录、建议学习顺序、文件树和链接必须同步更新。代码示例与测试仍使用 Python 3.10+；Docker 集成测试为可选项。

## Sandbox 设计

### 统一接口

新增独立的 `agent_core/sandbox/` 模块，不把隔离执行逻辑塞进 `ToolRegistry`。工具层只负责 schema、授权、审批和审计，sandbox 负责执行边界。

核心类型：

```python
@dataclass(frozen=True)
class SandboxPolicy:
    workspace: Path
    timeout_seconds: float = 5
    max_output_bytes: int = 64 * 1024
    max_memory_bytes: int | None = 256 * 1024 * 1024
    max_cpu_seconds: int | None = 2
    max_processes: int | None = 16
    network: Literal["deny", "allow"] = "deny"
    environment: Mapping[str, str] = field(default_factory=dict)

class Sandbox:
    def run(self, request: ExecutionRequest, policy: SandboxPolicy) -> ExecutionResult: ...
```

`ExecutionRequest` 至少包含两种受控模式：

- `PredefinedCommand`：命令名来自 allowlist，参数经过 schema 校验，使用参数列表执行，不拼接 shell 字符串。
- `PythonCode`：代码写入临时工作目录后执行，默认不继承宿主环境变量，只暴露显式传入的输入文件。

`ExecutionResult` 记录 stdout、stderr、退出码、停止原因、耗时和策略摘要。停止原因至少区分正常退出、非零退出、超时、输出超限和资源限制。结果与审计字段不得包含完整宿主环境、密钥或不必要的敏感代码内容。

### LocalProcessSandbox

本机执行器使用 `subprocess.Popen(..., shell=False)`，工作目录固定在临时 workspace。执行前清空继承环境，仅加入明确 allowlist 的变量；输入文件只读复制或显式挂载。stdout/stderr 必须受上限约束，超限后终止任务。超时后终止整个进程组，不能只杀顶层进程。

Unix 平台使用 `resource.setrlimit` 限制 CPU 时间、地址空间、打开文件数和进程数。平台不支持的限制必须显式记录为未启用，不能声称已经提供保护。

文档明确说明：本机进程版不是强安全边界。它不能可靠阻止网络访问、同一用户权限下的资源访问、内核漏洞利用或解释器/系统调用层面的逃逸，适合教学和低风险受信代码，不适合直接执行不可信代码。

### DockerSandbox

Docker 执行器使用参数列表调用 `docker run`，不经过 shell。默认参数包括：

- `--network=none`
- `--read-only`
- 独立的临时 writable workspace
- 非 root 用户
- `--cap-drop=ALL`
- `--security-opt=no-new-privileges`
- `--memory`、`--cpus`、`--pids-limit`

不得传入宿主环境变量、Docker socket、credential、源码目录或未声明的挂载。镜像应支持 digest 固定，并在审计摘要中记录镜像标识。超时和输出上限由宿主执行器兜底。

Docker 也不是所有威胁的绝对保证；镜像、Docker daemon、宿主内核和挂载配置仍属于信任边界。文档必须把“容器隔离”与身份授权、租户过滤、数据最小化分别说明。

### Agent 接入边界

模型不能直接执行任意 shell。Agent 只能调用经过 `ToolDefinition` 注册的工具；工具负责 allowlist、参数校验、用户/租户/任务授权和高风险审批，再把安全的 `ExecutionRequest` 交给 sandbox。高风险动作使用 preview/commit 两阶段，审批界面显示最终参数、目标对象和影响范围。

## 安全专题内容

### 应用层安全

覆盖信任边界、直接和间接 Prompt Injection、上下文中的数据/指令标记、工具 allowlist、最小权限、输出校验、审批、审计脱敏和高风险操作的 preview/commit。案例对比任意 shell、预定义命令和 sandbox 三种边界。

### 数据与身份

覆盖用户、租户、session、memory 和 RAG 文档隔离；数据分类、最小化传递、保留/删除；短期凭据和环境变量 allowlist。密钥不得进入 prompt、checkpoint 或日志。无网络不能代替授权，容器隔离不能代替租户级数据过滤。

### 供应链安全

覆盖 Python 依赖锁定与扫描、Docker 镜像 digest 和更新、MCP server 来源/版本/capability allowlist、认证、超时、结果过滤及第三方工具描述的不可信性。

### 事件响应

覆盖最小化记录 trace、策略版本、工具版本和镜像版本；针对注入、越权、密钥泄露、sandbox 异常和副作用重复定义暂停任务、撤销凭据、隔离任务、回滚和人工升级流程。加入一次离线 incident exercise，从 trace 反推出攻击路径。

## 测试与验收

### 策略单元测试

覆盖命令 allowlist、参数 schema、环境变量清理、绝对路径、`../` 和符号链接逃逸、输出截断、超时、返回码、停止原因和审计摘要脱敏。

### 本机执行器测试

覆盖短脚本、非零退出、子进程、无限输出、无限循环、CPU/内存限制。平台不支持的资源限制显式 skip 或标记，不得静默通过。

### Docker 集成测试

检测 Docker 可用性后运行。验证无网络、非 root、无宿主文件/密钥、只读根文件系统、资源限制和容器终止。Docker 不可用时测试套件显式 skip，README 说明安装和验证方式。

### 综合项目验收

- 预定义命令无法执行 allowlist 外的程序。
- 生成 Python 代码只能通过 sandbox，不能继承宿主 secret。
- `../`、绝对路径和符号链接不能访问 workspace 外部。
- 超时、输出爆炸和资源耗尽都有确定停止原因。
- Docker 模式默认无网络、非 root、无额外挂载。
- trace 能定位任务、工具、策略和镜像版本。
- 两个租户不能通过 memory、RAG、workspace 或日志互相读取。

## 不在本次范围

- 不实现操作系统级微 VM、gVisor、Firecracker 或生产级多租户隔离平台。
- 不允许通过 shell 字符串拼接来“简化”命令执行。
- 不把本机进程执行器描述为可承载任意不可信代码。
- 不在本次任务中引入新的 LLM provider 或真实在线模型依赖。
