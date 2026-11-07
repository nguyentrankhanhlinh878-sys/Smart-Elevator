from data_structures import MinHeap, MaxHeap

class ExternalRequest:
    def __init__(self, floor, direction):
        self.floor = floor
        self.direction = direction

class CabinRequest:
    def __init__(self, elevator_id, target_floor):
        self.elevator_id = elevator_id
        self.target_floor = target_floor

class Elevator:
    def __init__(self, elevator_id, initial_floor, initial_dest=None):
        self.id = elevator_id
        self.initial_floor = initial_floor
        self.current_floor = initial_floor
        self.initial_dest = initial_dest

        self.up_queue = MinHeap()
        self.down_queue = MaxHeap()

        if initial_dest is not None and initial_dest != initial_floor:
            if initial_dest > initial_floor:
                self.state = "MOVING_UP"
                self.up_queue.insert(initial_dest)
            else:
                self.state = "MOVING_DOWN"
                self.down_queue.insert(initial_dest)
        else:
            self.state = "IDLE"

    def add_stop(self, floor, direction_intent="NONE"):
        if floor == self.current_floor and self.state == "IDLE" and direction_intent == "NONE":
            return False

        target_up = False
        target_down = False

        if direction_intent == "UP":
            target_up = True
        elif direction_intent == "DOWN":
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
            if self.state == "IDLE":
                if floor > self.current_floor:
                    self.state = "MOVING_UP"
                elif floor < self.current_floor:
                    self.state = "MOVING_DOWN"
                else:
                    self.state = "MOVING_UP" if direction_intent == "UP" else "MOVING_DOWN"

        return added

    def has_movement(self):
        return not self.up_queue.is_empty() or not self.down_queue.is_empty()

    def generate_route(self):
        route = [self.current_floor]
        if not self.has_movement():
            return route

        up_stops = []
        while not self.up_queue.is_empty():
            up_stops.append(self.up_queue.extract_min())

        down_stops = []
        while not self.down_queue.is_empty():
            down_stops.append(self.down_queue.extract_max())

        if self.state == "MOVING_UP":
            phase1 = [f for f in up_stops if f >= self.current_floor]
            phase2 = down_stops
            phase3 = [f for f in up_stops if f < self.current_floor]
            all_stops = phase1 + phase2 + phase3
        elif self.state == "MOVING_DOWN":
            phase1 = [f for f in down_stops if f <= self.current_floor]
            phase2 = up_stops
            phase3 = [f for f in down_stops if f > self.current_floor]
            all_stops = phase1 + phase2 + phase3

        for stop in all_stops:
            if stop != route[-1]:
                route.append(stop)

        return route

    def complete_route(self):
        route = self.generate_route()
        for floor in route[1:]:
            self.current_floor = floor
        self.initial_dest = None
        self.state = "IDLE"
        return route