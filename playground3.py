class ClientBuilder:
    def __init__(self):
        # 内部字段不能与链式方法同名，否则实例属性会遮蔽方法。
        self._app_id = None
        self._app_secret = None
        self._app_type = None

    def app_id(self, value):
        self._app_id = value
        return self   # 关键！返回自身

    def app_secret(self, value):
        self._app_secret = value
        return self

    def app_type(self, value):
        self._app_type = value
        return self

    def build(self):
        # 真正创建最终Client对象
        client = Client(self._app_id, self._app_secret, self._app_type)
        return client


class Client:
    def __init__(self, app_id, app_secret, app_type):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_type = app_type

# 对外暴露入口，模仿 lark.Client.builder()
class Lark:
    @staticmethod
    def builder():
        return ClientBuilder()

# 模拟模块
# lark = Lark()


def main():
    # 链式调用
    client = (
        Lark.builder()
        .app_id("APP_ID")
        .app_secret("APP_SECRET")
        .app_type("ISV")
        .build()
    )

    print(client.app_id)


if __name__ == "__main__":
    main()
