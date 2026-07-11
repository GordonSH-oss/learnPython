func_list = []
for i in range(3):
    def func():
        print(i)
    func_list.append(func)

# 循环结束 i = 2
for f in func_list:
    f()
# 输出全部是 2，而不是 0 1 2