class Demo:
    def __init__(self, name):
        self.name = name

    def ___setattr__(self, name, value):
        print(f"Setting attribute {name} to {value}")
        super().__setattr__(name, value)
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    demo = Demo("Alice")
    demo.name = "Bob"  # This will trigger the ___setattr__ method
    print(demo.greet())
