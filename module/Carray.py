class Circular_Array():
    def __init__(self,size):
        self._list = [None] * size
        self._size = size
        self._front = -1
        
    def push(self,val):
        self._front= (self._front + 1) % self._size
        self._list[self._front]=val
     
    @property
    def top(self):
        if self._front == -1 :
            return None
        else:
            return self._list[self._front]
    
    @property
    def size(self):
        return self._size
    
    
    @property
    def length(self) :
        l=  (self._front + 1 ) % self._size
        if self._list[l] == None :
            return l
        return self.size
            
    def val(self,i) :
        j = self._front - i
        if (j < 0) :
            if self.length < self._size:
                return None
            j = self._size +  j
        return self._list[j]
        
            
        
