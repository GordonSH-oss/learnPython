import unittest
from pathlib import Path

from playground import hybrid_score, lexical_overlap_score, load_docs


ROOT = Path(__file__).resolve().parents[1]


class PlaygroundChunkingTests(unittest.TestCase):
    def test_message_listener_section_stays_together(self) -> None:
        docs = load_docs(ROOT / "quickstart.md")

        listening_section = next(doc for doc in docs if "### 监听消息" in doc)

        self.assertIn("通过设置消息接收监听器", listening_section)
        self.assertIn("RongCoreClient.addOnReceiveMessageListener", listening_section)
        self.assertNotIn("### 连接融云 IM 服务器", listening_section)

    def test_heading_only_chunks_are_not_indexed(self) -> None:
        docs = load_docs(ROOT / "quickstart.md")

        self.assertNotIn("## 环境要求", docs)
        self.assertNotIn("### 监听消息", docs)

    def test_exact_phrase_match_gets_a_lexical_boost(self) -> None:
        listening_doc = "# 快速上手\n## 操作步骤\n### 监听消息\n通过设置消息接收监听器，用户可接收所有类型的实时消息和离线消息。"
        prep_doc = "# 快速上手\n## 准备工作\n获取 App Key 并完成 SDK 初始化。"

        listening_lexical = lexical_overlap_score("如何监听消息？", listening_doc)
        prep_lexical = lexical_overlap_score("如何监听消息？", prep_doc)

        self.assertGreater(listening_lexical, prep_lexical)
        self.assertGreater(
            hybrid_score(0.63, listening_lexical),
            hybrid_score(0.68, prep_lexical),
        )


if __name__ == "__main__":
    unittest.main()
