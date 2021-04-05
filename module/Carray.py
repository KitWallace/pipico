class Circular_Array():
    def __init__(self,size):
        self._list = [None] * size
        self._size = size
        self._front = -1
        
    def push(self,val):
        self._front= (self._front + 1) % self._size
        self._list[self._front]=val
     
    def top(self):
        if self._front == -1 :
            return None
        else:
            return self._list[self._front]
    
    @property
    def size(self):
        return self._size
    
    @property
    def _back(self) :
        if (self._front == -1):
            return -1
        else:
            next = (self._front + 1) % self._size
            if self._list[next] != None:
                return next
            else :
                return 0
    @property
    def length(self) :
        if self._back > self._front :
            return self._size
        else :
            return self._front + 1
            
    def val(self,i) :
        start = self._back
        if (start == -1) :
            return None
        else :
            j = (start + i) % self._size
            return self._list[j]
            
        
