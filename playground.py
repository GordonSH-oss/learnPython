class iterator:
    def __init__(self):
        self.index = 1
        self.data= []

    def __iter__(self):
        return self

    def __next__(self):
        if self.index > 10:
            raise StopIteration
        self.data.append(self.index)
        result = self.data[-1]
        self.index += 1
        return result
        
iter = iterator()
print(list(iter))
