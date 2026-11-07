class GroupDispatcher:
    def __init__(self, elevators, total_floors=12):
        self.elevators = elevators
        self.total_floors = total_floors

    def calculate_cost(self, elevator, request):
        distance = abs(elevator.current_floor - request.floor)
        idle_penalty = self.total_floors
        opposite_direction_penalty = 2 * self.total_floors

        moving_toward_request = (
            elevator.state == "MOVING_UP"
            and request.direction == "UP"
            and elevator.current_floor <= request.floor
        ) or (
            elevator.state == "MOVING_DOWN"
            and request.direction == "DOWN"
            and elevator.current_floor >= request.floor
        )

        # Ưu tiên 1: Thang đang đi cùng chiều và chưa vượt qua tầng gọi
        if moving_toward_request:
            return distance

        # Ưu tiên 2: Thang đang đứng yên (IDLE)
        if elevator.state == "IDLE":
            return distance + idle_penalty

        # Ưu tiên 3: Thang đi ngược chiều hoặc đã vượt qua tầng gọi
        return distance + opposite_direction_penalty

    def dispatch_external(self, req):
        """Giao yêu cầu cho thang máy có chi phí thấp nhất."""
        best_elevator = self.elevators[0]
        min_cost = self.calculate_cost(best_elevator, req)

        for elevator in self.elevators[1:]:
            cost = self.calculate_cost(elevator, req)
            if cost < min_cost:
                min_cost = cost
                best_elevator = elevator

        best_elevator.add_stop(req.floor, req.direction)
        return best_elevator, min_cost

    def process_cabin(self, req):
        elevator = self.elevators[req.elevator_id - 1]
        return elevator.add_stop(req.target_floor)

    def run_dispatch(self, external_queue, cabin_requests, down_queue=None):
        """Thực thi điều phối theo thứ tự: Cabin -> Hàng đợi Lên -> Hàng đợi Xuống."""
        logs = []

        for cab_req in cabin_requests:
            added = self.process_cabin(cab_req)
            if added:
                logs.append(
                    f"Yêu cầu trong cabin -> Thang máy #{cab_req.elevator_id} sẽ dừng tại tầng {cab_req.target_floor}"
                )
            else:
                logs.append(
                    f"Yêu cầu trong cabin -> Thang máy #{cab_req.elevator_id} bỏ qua tầng "
                    f"{cab_req.target_floor} (đang ở tầng này hoặc yêu cầu bị trùng)"
                )

        queues_to_process = [external_queue]
        if down_queue is not None:
            queues_to_process.append(down_queue)

        for q in queues_to_process:
            while not q.is_empty():
                ext_req = q.dequeue()
                assigned_elev, cost = self.dispatch_external(ext_req)
                dir_str = "LÊN" if ext_req.direction == "UP" else "XUỐNG"
                logs.append(
                    f"Yêu cầu gọi tầng {ext_req.floor} đi {dir_str} -> "
                    f"Giao cho thang máy #{assigned_elev.id} (chi phí: {cost})"
                )

        return logs