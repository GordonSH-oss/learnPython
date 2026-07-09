try:
    num = int(input("输入数字："))
except ValueError:
    print("输入不是数字")
else:
    # 只有转数字成功才执行
    print("转换成功，数字：", num)
finally:
    print("我一定会执行")