class GroupDispatcher:
    def __init__(self, elevators, total_floors=12):
        self.elevators = elevators
        self.total_floors = total_floors

    def calculate_cost(self, elevator, External_request):
        distance = abs(elevator.current_floor - External_request.floor)
        idle_elevator_penalty = self.total_floors
        opposite_direction_penalty = 2 * self.total_floors

        moving_toward_request = (
            elevator.state == "MOVING_UP"
            and External_request.direction == "UP"
            and elevator.current_floor <= External_request.floor) or (
            
            elevator.state == "MOVING_DOWN"
            and External_request.direction == "DOWN"
            and elevator.current_floor >= External_request.floor
        )

        if moving_toward_request:
            return distance

        if elevator.state == "IDLE":
            return distance + idle_elevator_penalty

        return distance + opposite_direction_penalty

    def dispatch_external(self, External_request):
        best_elevator = self.elevators[0]
        min_cost = self.calculate_cost(best_elevator, External_request)

        for elevator in self.elevators[1:]:
            cost = self.calculate_cost(elevator, External_request)
            if cost < min_cost:
                min_cost = cost
                best_elevator = elevator

        best_elevator.add_stop(External_request.floor, External_request.direction)
        return best_elevator, min_cost

    def process_cabin(self, Cabinrequest):
        elevator = self.elevators[Cabinrequest.elevator_id - 1]
        return elevator.add_stop(Cabinrequest.target_floor)

    def run_dispatch(self, up_external_queue, cabin_requests, down_external_queue=None):
        logs = []

        for cabin_request in cabin_requests:
            added = self.process_cabin(cabin_request)
            if added:
                logs.append(
                    f"Yêu cầu trong cabin -> Thang máy #{cabin_request.elevator_id} sẽ dừng tại tầng {cabin_request.target_floor}"
                )
            else:
                logs.append(
                    f"Yêu cầu trong cabin -> Thang máy #{cabin_request.elevator_id} bỏ qua tầng "
                    f"{cabin_request.target_floor} (đang ở tầng này hoặc yêu cầu bị trùng)"
                )

        queues_to_process = [up_external_queue]
        if down_external_queue is not None:
            queues_to_process.append(down_external_queue)

        for q in queues_to_process:
            while not q.is_empty():
                ext_req = q.dequeue()
                assigned_elevator, cost = self.dispatch_external(ext_req)
                direction = "LÊN" if ext_req.direction == "UP" else "XUỐNG"
                logs.append(
                    f"Yêu cầu gọi tầng {ext_req.floor} đi {direction} -> "
                    f"Giao cho thang máy #{assigned_elevator.id} (chi phí: {cost})"
                )

        return logs