class MiniFlask:
    def __init__(self):
        self.routes = {}
    
    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def handle(self, path):
        """模拟收到请求"""
        handler = self.routes.get(path)
        return handler() if handler else "404"

app = MiniFlask()

@app.route("/users")
def users():
    return "user list"

@app.route("/posts")
def posts():
    return "post list"

print(app.handle("/users"))   # user list
print(app.handle("/posts"))   # post list
print(app.handle("/xxx"))     # 404