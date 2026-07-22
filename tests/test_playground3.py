import unittest

from playground3 import lark


class ClientBuilderTests(unittest.TestCase):
    def test_builds_client_with_chained_configuration(self) -> None:
        client = (
            lark.builder()
            .app_id("APP_ID")
            .app_secret("APP_SECRET")
            .app_type("ISV")
            .build()
        )

        self.assertEqual(client.app_id, "APP_ID")
        self.assertEqual(client.app_secret, "APP_SECRET")
        self.assertEqual(client.app_type, "ISV")


if __name__ == "__main__":
    unittest.main()
