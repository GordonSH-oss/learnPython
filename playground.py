def make_aver():
    series=[]
    def aver(new_value):
        series.append(new_value)
        total=sum(series)
        return total/len(series)
    return aver

avger=make_aver()
print(avger(10))
print(avger(11))
print(avger(12))
