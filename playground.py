def func(x):
    x.append(99) # 修改外部原列表
    x = [1,2]    # 仅修改局部标签绑定，外部不变
    print(f"func 里面的 x = {x}")

a = [1]
res=func(a)