import os

from daytona import Daytona, DaytonaConfig
from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_daytona import DaytonaSandbox
from langchain_ollama import ChatOllama


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    load_dotenv()

    daytona = Daytona(
        DaytonaConfig(api_key=require_env("DAYTONA_API_KEY"))
    )
    sandbox = daytona.create()

    try:
        backend = DaytonaSandbox(sandbox=sandbox)
        agent = create_deep_agent(
            model=ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "llama3.2:1b")
            ),
            system_prompt=(
                "You are a Python coding assistant with sandbox access."
            ),
            backend=backend,
        )

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Create a hello world Python script and run it"
                        ),
                    }
                ]
            }
        )
        print(result)
    finally:
        daytona.delete(sandbox)


if __name__ == "__main__":
    main()
