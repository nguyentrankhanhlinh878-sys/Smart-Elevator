from data_structures import MinHeap, MaxHeap

class ExternalRequest:
    """Yêu cầu gọi thang từ ngoài sảnh gồm số tầng và hướng đi ('UP' hoặc 'DOWN')."""
    def __init__(self, floor, direction):
        self.floor = floor
        self.direction = direction


class CabinRequest:
    """Yêu cầu bấm chọn tầng từ bên trong khoang thang máy."""
    def __init__(self, elevator_id, target_floor):
        self.elevator_id = elevator_id
        self.target_floor = target_floor


class Elevator:
    """Mô hình thang máy sử dụng 2 Heap (MinHeap và MaxHeap) theo thuật toán LOOK."""
    def __init__(self, elevator_id, initial_floor, initial_dest=None):
        self.id = elevator_id
        self.initial_floor = initial_floor
        self.current_floor = initial_floor
        self.initial_dest = initial_dest

        self.up_queue = MinHeap()
        self.down_queue = MaxHeap()
        self.planned_stops = set()

        if initial_dest is not None and initial_dest != initial_floor:
            if initial_dest > initial_floor:
                self.state = "MOVING_UP"
                self.up_queue.insert(initial_dest)
            else:
                self.state = "MOVING_DOWN"
                self.down_queue.insert(initial_dest)
            self.planned_stops.add(initial_dest)
        else:
            self.state = "IDLE"

    def add_stop(self, floor, dir_intent="NONE"):
        """Thêm tầng dừng vào MinHeap hoặc MaxHeap tương ứng, tránh trùng lặp."""
        if floor == self.current_floor and self.state == "IDLE" and dir_intent == "NONE":
            return False

        target_up = False
        target_down = False

        if dir_intent == "UP":
            target_up = True
        elif dir_intent == "DOWN":
            target_down = True
        elif floor > self.current_floor:
            target_up = True
        elif floor < self.current_floor:
            target_down = True
        else:
            if self.state == "MOVING_UP":
                target_up = True
            elif self.state == "MOVING_DOWN":
                target_down = True
            else:
                return False

        added = False
        if target_up:
            if not self.up_queue.contains(floor):
                self.up_queue.insert(floor)
                added = True
        elif target_down:
            if not self.down_queue.contains(floor):
                self.down_queue.insert(floor)
                added = True

        if added:
            self.planned_stops.add(floor)
            if self.state == "IDLE":
                if floor > self.current_floor:
                    self.state = "MOVING_UP"
                elif floor < self.current_floor:
                    self.state = "MOVING_DOWN"
                else:
                    self.state = "MOVING_UP" if dir_intent == "UP" else "MOVING_DOWN"

        return added

    def has_movement(self):
        return len(self.planned_stops) > 0

    def finish_route(self):
        self.up_queue = MinHeap()
        self.down_queue = MaxHeap()
        self.planned_stops.clear()
        self.initial_dest = None
        self.state = "IDLE"

    def complete_route(self):
        route = self.generate_route()
        self.current_floor = route[-1]
        self.finish_route()
        return route

    def generate_route(self):
        """Tạo lộ trình di chuyển 3 pha theo thuật toán LOOK."""
        route = [self.current_floor]
        if not self.has_movement():
            return route

        curr = self.current_floor
        up_copy = self.up_queue.copy()
        down_copy = self.down_queue.copy()

        up_stops = []
        while not up_copy.is_empty():
            up_stops.append(up_copy.extract_min())

        down_stops = []
        while not down_copy.is_empty():
            down_stops.append(down_copy.extract_max())

        primary_dir = self.state
        if primary_dir == "IDLE":
            if up_stops and down_stops:
                dist_up = min(abs(s - curr) for s in up_stops)
                dist_down = min(abs(s - curr) for s in down_stops)
                primary_dir = "MOVING_UP" if dist_up <= dist_down else "MOVING_DOWN"
            elif up_stops:
                primary_dir = "MOVING_UP"
            else:
                primary_dir = "MOVING_DOWN"

        if primary_dir == "MOVING_UP":
            phase1 = [f for f in up_stops if f >= curr]
            phase2 = down_stops
            phase3 = [f for f in up_stops if f < curr]
            all_stops = phase1 + phase2 + phase3
        else:
            phase1 = [f for f in down_stops if f <= curr]
            phase2 = up_stops
            phase3 = [f for f in down_stops if f > curr]
            all_stops = phase1 + phase2 + phase3

        for stop in all_stops:
            if stop != route[-1]:
                route.append(stop)

        return route