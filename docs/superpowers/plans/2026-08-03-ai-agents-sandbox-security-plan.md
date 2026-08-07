# AI Agent Sandbox Security Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `14-ai-agents` 增加统一的 sandbox 执行接口、本机进程与可选 Docker 实现，并将安全课程扩展为覆盖应用、数据、供应链和事件响应的 12-18 教学路线。

**Architecture:** 新建 `agent_core/sandbox/` 作为独立执行边界，使用不可变请求/策略对象和结构化结果；`LocalProcessSandbox` 与 `DockerSandbox` 实现同一协议。Agent 工具仍负责 schema、授权、审批和审计，不能直接把模型文本交给 shell。文档和课程测试同步从 14 课迁移为 18 课，Docker 只作为可选集成测试依赖。

**Tech Stack:** Python 3.10+, standard library (`dataclasses`, `subprocess`, `tempfile`, `resource`, `os`, `signal`, `selectors`), pytest 8+, Docker CLI（可选）。

## Global Constraints

- 代码示例与测试继续支持 Python 3.10+。
- 不引入新的 LLM provider 或真实在线模型依赖。
- 不使用 shell 字符串拼接；所有外部命令使用参数列表和 `shell=False`。
- 本机进程 sandbox 明确不是强安全边界，不得把它描述为可安全承载任意不可信代码。
- Docker 集成测试检测 Docker 可用性后运行，不可用时显式 skip。
- 默认网络拒绝、最小环境变量、无宿主 secret、无 Docker socket、无未声明挂载。
- 不实现 microVM、gVisor、Firecracker 或生产级多租户隔离平台。
- 保留工作树中与本任务无关的 `playground.py`、`08-frameworks/django/`、`08-frameworks/fastapi/` 变更。

---

## File Map

- Create: `14-ai-agents/agent_core/sandbox/__init__.py` — 导出 sandbox 公共类型和执行器。
- Create: `14-ai-agents/agent_core/sandbox/types.py` — `PredefinedCommand`、`PythonCode`、`ExecutionRequest`、`SandboxPolicy`、`ExecutionResult`、停止原因。
- Create: `14-ai-agents/agent_core/sandbox/local.py` — 本机进程执行器与 Unix resource 限制。
- Create: `14-ai-agents/agent_core/sandbox/docker.py` — Docker 参数构造和容器执行器。
- Modify: `14-ai-agents/agent_core/__init__.py` — 暴露 sandbox API。
- Create: `14-ai-agents/tests/test_sandbox_policy.py` — 请求、策略、命令 allowlist 和结果契约测试。
- Create: `14-ai-agents/tests/test_sandbox_local.py` — 本机执行器行为与攻击性测试。
- Create: `14-ai-agents/tests/test_sandbox_docker.py` — Docker 可选集成测试与命令构造测试。
- Modify: `14-ai-agents/tests/test_rag_and_curriculum.py` — 课程数量从 14 更新为 18，并校验新链接。
- Modify/Create: `14-ai-agents/guides/12-security-and-guardrails.md` — 迁移为 12 课应用层安全。
- Create: `14-ai-agents/guides/13-sandbox-and-policies.md` — sandbox 威胁模型和策略。
- Create: `14-ai-agents/guides/14-local-process-sandbox.md` — 本机执行实验。
- Create: `14-ai-agents/guides/15-docker-sandbox.md` — Docker 执行实验。
- Create: `14-ai-agents/guides/16-identity-data-supply-chain.md` — 数据、身份、供应链。
- Rename/Modify: `14-ai-agents/guides/13-observability-and-production.md` -> `17-observability-and-production.md`。
- Rename/Modify: `14-ai-agents/guides/14-capstone-research-agent.md` -> `18-capstone-research-agent.md`。
- Modify: `14-ai-agents/README.md` — 课程表、路线、文件树、运行说明和安全边界。

---

### Task 1: Define Sandbox Contracts

**Files:**
- Create: `14-ai-agents/agent_core/sandbox/__init__.py`
- Create: `14-ai-agents/agent_core/sandbox/types.py`
- Modify: `14-ai-agents/agent_core/__init__.py`
- Test: `14-ai-agents/tests/test_sandbox_policy.py`

**Interfaces:**
- Produce `PredefinedCommand(name: str, arguments: tuple[str, ...] = ())`.
- Produce `PythonCode(source: str, files: Mapping[str, bytes] = {})`.
- Produce `ExecutionRequest = PredefinedCommand | PythonCode`.
- Produce frozen `SandboxPolicy(workspace: Path, timeout_seconds: float = 5, max_output_bytes: int = 65536, max_memory_bytes: int | None = 268435456, max_cpu_seconds: int | None = 2, max_processes: int | None = 16, network: Literal["deny", "allow"] = "deny", environment: Mapping[str, str] = {})`.
- Produce `ExecutionResult(stdout: str, stderr: str, returncode: int | None, reason: StopReason, duration_seconds: float, policy_summary: Mapping[str, object])`.
- Produce `Sandbox` protocol with `run(request, policy) -> ExecutionResult`.

- [ ] **Step 1: Write failing contract tests**

Test construction, frozen policy, request validation, supported stop reasons (`completed`, `failed`, `timeout`, `output_limit`, `resource_limit`, `policy_denied`), and stable public exports.

- [ ] **Step 2: Run the focused tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_policy.py -q`
Expected: FAIL because the sandbox package and types do not exist.

- [ ] **Step 3: Implement the minimal dataclasses and protocol**

Use `@dataclass(frozen=True)`, normalize command arguments to tuples, validate positive timeout/output limits, and keep policy summaries JSON-serializable. Do not execute anything in this task.

- [ ] **Step 4: Run focused tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_policy.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add 14-ai-agents/agent_core/sandbox 14-ai-agents/agent_core/__init__.py 14-ai-agents/tests/test_sandbox_policy.py
git commit -m "feat: define agent sandbox contracts"
```

### Task 2: Implement Local Process Sandbox

**Files:**
- Create: `14-ai-agents/agent_core/sandbox/local.py`
- Test: `14-ai-agents/tests/test_sandbox_local.py`

**Interfaces:**
- Consume the types from Task 1.
- Produce `LocalProcessSandbox(command_allowlist: Mapping[str, Sequence[str]] | None = None)` implementing `Sandbox.run`.
- `PredefinedCommand.name` resolves only through the allowlist; `PythonCode` runs the current Python executable with a temporary script.

- [ ] **Step 1: Write failing behavior tests**

Cover allowlisted command success, denied command, Python code success, explicit input files, no inherited secret environment variable, workspace-only file access, `../` and absolute path rejection, non-zero exit, timeout, output limit, and child-process cleanup. Add Unix-only tests for CPU/memory/process limits using `pytest.mark.skipif` when `resource` is unavailable.

- [ ] **Step 2: Run focused tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_local.py -q`
Expected: FAIL because `LocalProcessSandbox` is not implemented.

- [ ] **Step 3: Implement process setup**

Use `TemporaryDirectory` below the policy workspace or a dedicated child workspace, write Python source and declared files without following destination paths outside the workspace, build an explicit environment, and launch with `shell=False`, `cwd=workspace`, `start_new_session=True`, and pipes.

- [ ] **Step 4: Implement bounded collection and termination**

Use `communicate(timeout=...)`; if the deadline or output limit is exceeded, terminate the process group with `os.killpg`, wait, and return the corresponding reason. Decode with replacement and truncate captured output to the configured byte limit. Preserve return code for ordinary failures.

- [ ] **Step 5: Implement Unix pre-exec limits**

In a child-only `preexec_fn`, call `os.setsid` only if needed by the selected process setup and apply available `resource.setrlimit` values for CPU, address space, open files, and process count. Record unsupported limits in `policy_summary` rather than claiming enforcement.

- [ ] **Step 6: Run focused and full tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_policy.py 14-ai-agents/tests/test_sandbox_local.py -q`
Expected: PASS with platform-specific resource tests either passing or explicitly skipped.

- [ ] **Step 7: Commit**

```bash
git add 14-ai-agents/agent_core/sandbox/local.py 14-ai-agents/tests/test_sandbox_local.py
git commit -m "feat: add local process sandbox"
```

### Task 3: Implement Docker Sandbox

**Files:**
- Create: `14-ai-agents/agent_core/sandbox/docker.py`
- Test: `14-ai-agents/tests/test_sandbox_docker.py`

**Interfaces:**
- Produce `DockerSandbox(image: str, docker_binary: str = "docker", command_allowlist: Mapping[str, Sequence[str]] | None = None)` implementing `Sandbox.run`.
- Produce a private/public `build_docker_args(request, policy) -> list[str]` helper suitable for deterministic argument tests.

- [ ] **Step 1: Write command-construction tests**

Assert `docker run` uses argument lists, `--network=none`, `--read-only`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`, non-root user, resource flags, a temporary workspace mount only, and no host environment, source tree, Docker socket, or credential mounts. Assert denied commands never reach Docker.

- [ ] **Step 2: Run focused tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_docker.py -q`
Expected: FAIL because the Docker executor is absent.

- [ ] **Step 3: Implement safe Docker argument construction**

Translate `PredefinedCommand` through the allowlist and `PythonCode` to a script inside the temporary workspace. Use only list arguments; reject `network="allow"` unless the executor is explicitly configured to allow it; never copy `os.environ` wholesale.

- [ ] **Step 4: Implement subprocess execution and result normalization**

Invoke Docker with `shell=False`, use the same timeout and bounded output rules as the local executor, terminate the container on timeout, and return a policy summary including image reference and requested restrictions without recording secrets.

- [ ] **Step 5: Add optional integration tests**

Detect Docker with `shutil.which` and a short `docker version` probe. Skip with a clear reason when unavailable. When available, run tests for non-root, no network, read-only root, no host secret, workspace access, and resource/timeout termination.

- [ ] **Step 6: Run tests**

Run: `pytest 14-ai-agents/tests/test_sandbox_docker.py -q`
Expected: command tests PASS; integration tests PASS or show explicit skips when Docker is unavailable.

- [ ] **Step 7: Commit**

```bash
git add 14-ai-agents/agent_core/sandbox/docker.py 14-ai-agents/tests/test_sandbox_docker.py
git commit -m "feat: add optional docker sandbox"
```

### Task 4: Migrate and Expand Curriculum

**Files:**
- Modify: `14-ai-agents/guides/12-security-and-guardrails.md`
- Create: `14-ai-agents/guides/13-sandbox-and-policies.md`
- Create: `14-ai-agents/guides/14-local-process-sandbox.md`
- Create: `14-ai-agents/guides/15-docker-sandbox.md`
- Create: `14-ai-agents/guides/16-identity-data-supply-chain.md`
- Rename: `14-ai-agents/guides/13-observability-and-production.md` to `14-ai-agents/guides/17-observability-and-production.md`
- Rename: `14-ai-agents/guides/14-capstone-research-agent.md` to `14-ai-agents/guides/18-capstone-research-agent.md`
- Modify: `14-ai-agents/README.md`
- Test: `14-ai-agents/tests/test_rag_and_curriculum.py`

**Interfaces:**
- Consume the sandbox API from Tasks 1-3 in examples and exercises.
- Preserve every guide's required headings: `## 学习目标` and `## 常见错误` or `## 常见错误与生产注意`.

- [ ] **Step 1: Update the curriculum test first**

Change the expected lesson count to 18 and assert the new guide links exist, including the renamed observability and capstone files. Add assertions that the README mentions `Docker` as optional and that the sandbox docs state the local executor is not a strong security boundary.

- [ ] **Step 2: Run the curriculum test**

Run: `pytest 14-ai-agents/tests/test_rag_and_curriculum.py::test_curriculum_has_eighteen_linked_lessons -q`
Expected: FAIL until README and guides are migrated.

- [ ] **Step 3: Write the four new guides**

Use the existing concise structure: learning goals, code to inspect, concept model, execution path, underlying mechanism, exercises, and production mistakes. Include concrete commands and safety warnings for local and Docker modes, but do not present shell snippets that bypass the allowlist.

- [ ] **Step 4: Renumber existing security, observability, and capstone guides**

Make 12 focus on application-layer security. Rename 13/14 files and update headings, internal references, exercise paths, and all README links to 17/18.

- [ ] **Step 5: Update README**

Update course table to 18 lessons, recommended sequence, tree comments, commands, optional Docker verification instructions, and the statement that generated code must pass through sandbox and that local process isolation is limited.

- [ ] **Step 6: Run curriculum and complete test suite**

Run: `pytest 14-ai-agents/tests -q`
Expected: all tests PASS, with only Docker integration tests skipped when Docker is unavailable.

- [ ] **Step 7: Commit**

```bash
git add 14-ai-agents/README.md 14-ai-agents/guides 14-ai-agents/tests/test_rag_and_curriculum.py
git commit -m "docs: expand agent security curriculum"
```

### Task 5: Add Security and Capstone Integration Coverage

**Files:**
- Modify: `14-ai-agents/examples/research_agent.py`
- Modify: `14-ai-agents/guides/18-capstone-research-agent.md`
- Modify: `14-ai-agents/tests/test_agent_core.py`
- Create: `14-ai-agents/tests/test_security_integration.py`

**Interfaces:**
- Consume `Sandbox`, `SandboxPolicy`, `PythonCode`, and `LocalProcessSandbox` from Tasks 1-2.
- Produce a capstone tool that sends generated code through sandbox only and keeps tenant/session workspace and memory scopes distinct.

- [ ] **Step 1: Write integration tests first**

Assert a generated Python tool call cannot read an injected host secret, cannot escape through `../` or a symlink, cannot execute a non-allowlisted command, and returns deterministic timeout/output-limit reasons. Add two tenant runs and assert their workspace and memory evidence do not cross.

- [ ] **Step 2: Run the focused integration tests**

Run: `pytest 14-ai-agents/tests/test_security_integration.py -q`
Expected: FAIL because the capstone has no sandbox execution path.

- [ ] **Step 3: Wire the capstone through a sandbox tool**

Register one narrowly described tool for code execution, require approval for any write-capable mode, construct the request from typed arguments, pass a tenant-scoped workspace policy, and return only structured execution results to the Agent loop.

- [ ] **Step 4: Add trace-safe security metadata**

Record tenant/session/task identifiers, tool name, policy version, executor type, stop reason and image reference where applicable. Exclude prompt contents, full code, environment dumps and credentials.

- [ ] **Step 5: Update capstone exercises and incident exercise**

Document the new acceptance checks, explain why tool authorization and sandbox isolation are separate, and add a short offline incident exercise that identifies the affected policy and task from trace metadata.

- [ ] **Step 6: Run all tests and examples**

Run: `pytest 14-ai-agents/tests -q`; `python 14-ai-agents/examples/offline_agent.py`; `python 14-ai-agents/examples/research_agent.py`.
Expected: tests PASS (Docker tests may skip), offline examples complete without network or API keys.

- [ ] **Step 7: Commit**

```bash
git add 14-ai-agents/examples/research_agent.py 14-ai-agents/guides/18-capstone-research-agent.md 14-ai-agents/tests/test_agent_core.py 14-ai-agents/tests/test_security_integration.py
git commit -m "test: integrate sandbox security boundaries"
```

## Final Verification

- [ ] Run `pytest 14-ai-agents/tests -q` and record the exact pass/skip summary.
- [ ] Run all three offline examples from README.
- [ ] Run `git diff --check`.
- [ ] Search for stale `guides/13-` and `guides/14-` references with `rg -n 'guides/(13|14)-|第 13|第 14|十四' 14-ai-agents` and update any links that refer to the renamed lessons.
- [ ] Confirm `git status --short` contains only intended implementation changes plus the user's pre-existing unrelated files.
