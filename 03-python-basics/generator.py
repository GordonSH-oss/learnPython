def generator():
    x=1
    while x<11:
        yield x
        x +=1
        

gen=generator()
for i in gen:
    print(i)