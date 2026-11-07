class MinHeap: 
    
    def __init__(self):
        self._data = []

    def is_empty(self):
        return len(self._data) == 0
    
    def _heapify_up(self, index):
            parent_index = (index - 1) // 2
            while index > 0 and self._data[index] < self._data[parent_index]:
                self._data[index], self._data[parent_index] = self._data[parent_index], self._data[index]
                index = parent_index
                parent_index = (index - 1) // 2
                
    def insert(self, value):
        self._data.append(value)
        self._heapify_up(len(self._data) - 1)

    def _heapify_down(self, index):
            size = len(self._data)
            while True:
                smallest = index
                left = 2 * index + 1
                right = 2 * index + 2

                if left < size and self._data[left] < self._data[smallest]:
                    smallest = left
                if right < size and self._data[right] < self._data[smallest]:
                    smallest = right

                if smallest != index:
                    self._data[index], self._data[smallest] = self._data[smallest], self._data[index]
                    index = smallest
                else:
                    break
                
    def extract_min(self):
        if self.is_empty():
            raise IndexError("extract_min from empty heap")
        min_value = self._data[0]
        last_value = self._data.pop()
        if not self.is_empty():
            self._data[0] = last_value
            self._heapify_down(0)
        return min_value

    def contains(self, value):
        return value in self._data

class MaxHeap: 
    def __init__(self):
        self._data = []

    def is_empty(self):
        return len(self._data) == 0
    
    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self._data[index] > self._data[parent_index]:
            self._data[index], self._data[parent_index] = self._data[parent_index], self._data[index]
            index = parent_index
            parent_index = (index - 1) // 2    

    def insert(self, value):
        self._data.append(value)
        self._heapify_up(len(self._data) - 1)

    def _heapify_down(self, index):
        size = len(self._data)
        while True:
            largest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self._data[left] > self._data[largest]:
                largest = left
            if right < size and self._data[right] > self._data[largest]:
                largest = right

            if largest != index:
                self._data[index], self._data[largest] = self._data[largest], self._data[index]
                index = largest
            else:
                break
            
    def extract_max(self):
        if self.is_empty():
            raise IndexError("extract_max from empty heap")
        max_value = self._data[0]
        last_value = self._data.pop()
        if not self.is_empty():
            self._data[0] = last_value
            self._heapify_down(0)
        return max_value

    def contains(self, value):
        return value in self._data

class FIFOQueue:
    def __init__(self):
        self._items = []
        self._head = 0

    def is_empty(self):
        return self._head >= len(self._items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        item = self._items[self._head]
        self._head += 1
        if self._head > 50 and self._head > len(self._items) // 2:
            self._items = self._items[self._head:]
            self._head = 0
        return item