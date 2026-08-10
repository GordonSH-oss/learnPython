# 第三方库：AI

## PyTorch

- [ ] 我理解 Tensor、autograd、Module、optimizer、train/eval 和 device。
- [ ] 我会写最小训练循环、关闭梯度推理并保存/加载 state dict。

安装：仓库 `requirements/ai.txt` 声明 `torch>=2.2`；根据 CPU/CUDA 平台选择官方安装命令。

```python
import torch

x = torch.tensor([[1.0], [2.0]])
y = 2 * x
w = torch.nn.Parameter(torch.zeros(1, 1))
loss = ((x @ w - y) ** 2).mean()
loss.backward()
print(w.grad)
```

常见坑：训练和推理模式不同；推理时应使用 `torch.no_grad()`；设备和 dtype 必须一致；保存完整对象会带来版本耦合，通常保存 `state_dict`。

自查：`backward()` 后梯度存在哪里？为什么每个 batch 要清零梯度？

练习：将一个线性回归改成完整训练/验证循环，记录 loss 并保存最佳检查点。

仓库关联：[PyTorch 课程](../07-deep-learning/pytorch/plan.md)、[基础 notebook](../07-deep-learning/pytorch/notebooks/02-autograd.ipynb)。

## OpenAI Python SDK

- [ ] 我知道客户端、认证、请求、响应和错误边界。
- [ ] 我会从环境变量读取 API key，设置超时，检查响应并避免记录敏感内容。

安装：`python -m pip install openai`（仓库基线 `openai>=1.0`）。具体模型名和接口以当前服务文档为准。

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=30.0)
response = client.responses.create(model="<model>", input="Say hello")
print(response.output_text)
```

常见坑：不要硬编码密钥；模型响应可能包含拒答、工具调用或不稳定文本；生产代码要有超时、重试、限流、成本和审计边界。

自查：为什么 SDK 调用仍需要自己的错误映射？如何测试而不访问真实 API？

练习：给客户端包一层可注入的接口，使用 fake client 测试成功、超时和服务端错误。

仓库关联：[API 集成](../04-api-integration/openai_demo.py)、[韧性客户端](../04-api-integration/resilient_api_client.py)。

## LangGraph

- [ ] 我理解 state、node、edge、条件路由和 checkpoint 的关系。
- [ ] 我会先用确定性节点构建图，再加入模型或工具，并为每个状态转移写测试。

安装：`python -m pip install langgraph`（仓库基线 `langgraph>=0.2`）。本仓库已有示例依赖但未固定具体图结构。

```python
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    text: str

def normalize(state: State) -> State:
    return {"text": state["text"].strip().lower()}

graph = StateGraph(State)
graph.add_node("normalize", normalize)
graph.add_edge(START, "normalize")
graph.add_edge("normalize", END)
app = graph.compile()
print(app.invoke({"text": " Hello "}))
```

常见坑：节点应明确读写哪些状态；循环必须有终止条件；checkpoint、工具副作用和重试会影响幂等性；不要把所有逻辑塞进一个节点。

自查：条件边根据什么状态做决定？如何重放一次失败执行？

练习：增加一个条件节点，空文本进入错误分支，非空文本进入完成分支，并测试两条路径。

仓库关联：[Agent 示例](../14-ai-agents/examples/framework_langgraph.py)、[Agent 学习路线](../14-ai-agents/README.md)。

