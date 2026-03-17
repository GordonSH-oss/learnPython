class Parent:
    def __final_method(self):  # 双下划线：触发名称改写
        print("父类核心方法，无法被重写")

    def call_final(self):
        # 内部调用改写后的方法
        self.__final_method()

class Child(Parent):
    # 子类试图重写 __final_method，但实际创建的是 _Child__final_method
    def __final_method(self):
        print("子类试图重写，无效")

# 测试：子类的重写不会生效
child = Child()
child.call_final()  # 输出：父类核心方法，无法被重写
# 子类的 __final_method 是独立方法，需手动调用才会执行
child._Child__final_method()  # 输出：子类试图重写，无效
