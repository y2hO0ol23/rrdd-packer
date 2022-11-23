class Node():
    def __init__(self, *argv):
        if type(argv[0]) == int:
            self.val = argv[0]
            self.freq = argv[1]
            self.left = None
        else:
            self.left = argv[0]
            self.right = argv[1]
            print
            self.freq = self.frequency()
    

    def frequency(self, depth = 1):
        if self.left == None:
            return self.freq * depth
        else:
            return self.left.frequency(depth+1) + self.right.frequency(depth+1) 


    def result(self, value = ""):
        if self.left == None:
            return {self.val : value}
        else:
            left = self.left.result(value + "0")
            right = self.right.result(value + "1")
            return {**left, **right}

    
    __lt__ = lambda self, other: True