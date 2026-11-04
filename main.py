from models import Elevator, ExternalRequest, CabinRequest
from data_structures import FIFOQueue
from dispatcher import GroupDispatcher

TOTAL_FLOORS = 12
TOTAL_ELEVATORS = 10


def parse_integer(value, description):
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{description} phải là số nguyên: '{value}'.")


def parse_elevators_input(line):
    """Đọc trạng thái ban đầu của 10 thang máy (Ví dụ: '1 3 5:10 8:2 4 6 7 9 11 12')."""
    tokens = line.strip().split()
    if len(tokens) != TOTAL_ELEVATORS:
        raise ValueError(f"Cần nhập đúng {TOTAL_ELEVATORS} trạng thái thang máy, hiện có {len(tokens)}.")

    elevators = []
    for idx, token in enumerate(tokens, start=1):
        if ":" in token:
            parts = token.split(":")
            if len(parts) != 2:
                raise ValueError(f"Định dạng '{token}' của thang #{idx} không hợp lệ. Cần nhập <tầng>:<tầng_đích>.")
            init_floor = parse_integer(parts[0], f"Tầng hiện tại của thang #{idx}")
            dest_floor = parse_integer(parts[1], f"Tầng đích của thang #{idx}")
            if not (1 <= init_floor <= TOTAL_FLOORS) or not (1 <= dest_floor <= TOTAL_FLOORS):
                raise ValueError(f"Tầng của thang #{idx} phải nằm trong khoảng [1..{TOTAL_FLOORS}].")
            if init_floor == dest_floor:
                raise ValueError(f"Tầng đích của thang #{idx} không thể trùng tầng hiện tại.")
            elevators.append(Elevator(idx, init_floor, dest_floor))
        else:
            init_floor = parse_integer(token, f"Tầng hiện tại của thang #{idx}")
            if not (1 <= init_floor <= TOTAL_FLOORS):
                raise ValueError(f"Tầng của thang #{idx} phải nằm trong khoảng [1..{TOTAL_FLOORS}].")
            elevators.append(Elevator(idx, init_floor, None))

    return elevators


def parse_external_requests(line):
    """Đọc yêu cầu gọi tầng ngoài sảnh không cần Regex (Ví dụ: '6U 3D 10D')."""
    tokens = line.strip().split()
    requests = []
    for token in tokens:
        if len(token) < 2:
            raise ValueError(f"Yêu cầu '{token}' không hợp lệ. Cần nhập <tầng><U|D> (ví dụ: 5U, 2D).")
        floor_str = token[:-1]
        dir_char = token[-1].upper()

        if not floor_str.isdigit() or dir_char not in ("U", "D"):
            raise ValueError(f"Yêu cầu '{token}' không hợp lệ. Cần nhập <tầng><U|D> (ví dụ: 5U, 2D).")

        floor = int(floor_str)
        if not (1 <= floor <= TOTAL_FLOORS):
            raise ValueError(f"Tầng gọi {floor} phải nằm trong khoảng [1..{TOTAL_FLOORS}].")
        if floor == 1 and dir_char == "D":
            raise ValueError("Tầng 1 không thể gọi thang đi xuống.")
        if floor == TOTAL_FLOORS and dir_char == "U":
            raise ValueError(f"Tầng trên cùng {TOTAL_FLOORS} không thể gọi thang đi lên.")

        direction = "UP" if dir_char == "U" else "DOWN"
        requests.append(ExternalRequest(floor, direction))
    return requests


def parse_cabin_requests(line):
    """Đọc yêu cầu chọn tầng trong cabin (Ví dụ: '1:10 3:1')."""
    tokens = line.strip().split()
    requests = []
    for token in tokens:
        parts = token.split(":")
        if len(parts) != 2:
            raise ValueError(f"Yêu cầu trong cabin '{token}' không hợp lệ. Cần nhập <mã_thang>:<tầng_đích>.")
        elev_id = parse_integer(parts[0], "Mã thang máy")
        target_floor = parse_integer(parts[1], "Tầng đích")
        if not (1 <= elev_id <= TOTAL_ELEVATORS):
            raise ValueError(f"Mã thang máy {elev_id} phải nằm trong khoảng [1..{TOTAL_ELEVATORS}].")
        if not (1 <= target_floor <= TOTAL_FLOORS):
            raise ValueError(f"Tầng đích {target_floor} phải nằm trong khoảng [1..{TOTAL_FLOORS}].")
        requests.append(CabinRequest(elev_id, target_floor))
    return requests


def display_results(elevators, logs, routes):
    """In nhật ký điều phối và bảng lộ trình di chuyển bằng lệnh print cơ bản."""
    print("\n" + "=" * 70)
    print("NHẬT KÝ ĐIỀU PHỐI")
    print("=" * 70)
    if logs:
        for log in logs:
            print(f" [NHẬT KÝ] {log}")
    else:
        print(" (Không có yêu cầu gọi tầng ngoài hoặc yêu cầu trong cabin)")

    max_steps = max((len(r) - 1 for r in routes.values()), default=0)

    if max_steps > 0:
        print("\n" + "=" * 70)
        print("BẢNG CÁC BƯỚC DI CHUYỂN CỦA THANG MÁY")
        print("=" * 70)

        headers = ["Thang", "Vị trí đầu"] + [f"Đích {step}" for step in range(1, max_steps + 1)]
        col_width = 10

        header_line = " | ".join(h.ljust(col_width) for h in headers)
        print(header_line)
        print("-" * len(header_line))

        for elev in elevators:
            route = routes[elev.id]
            steps = [
                f"{'↑' if target > current else '↓'} {target}"
                for current, target in zip(route, route[1:])
            ]
            row = [f"#{elev.id}", str(route[0])] + steps + ["-"] * (max_steps - len(steps))
            print(" | ".join(cell.ljust(col_width) for cell in row))
    else:
        print("\n>> Tất cả 10 thang máy đều ở trạng thái đứng yên (Không có yêu cầu di chuyển).")


def read_initial_elevators():
    while True:
        try:
            print("[BƯỚC 1] Nhập trạng thái ban đầu của 10 thang máy (cách nhau bằng dấu cách):")
            print("Định dạng: <tầng> nếu đứng yên, hoặc <tầng>:<tầng_đích> nếu đang di chuyển")
            print("Ví dụ: 1 3 5:10 8:2 4 6 7 9 11 12")
            elev_line = input("Thang máy> ").strip()
            if not elev_line:
                elev_line = "1 3 5:10 8:2 4 6 7 9 11 12"
                print(f">> Tự động sử dụng cấu hình mặc định: {elev_line}")
            return parse_elevators_input(elev_line)
        except ValueError as e:
            print(f">> Lỗi: {e} Vui lòng nhập lại.\n")


def run_simulator():
    print("=" * 70)
    print("MÔ PHỎNG ĐIỀU PHỐI THANG MÁY THÔNG MINH (CSD203 - FA26)")
    print("12 tầng (1-12) | 10 khoang thang máy")
    print("=" * 70)

    elevators = read_initial_elevators()

    while True:
        while True:
            try:
                print("\n[BƯỚC 2] Nhập yêu cầu gọi thang từ bên ngoài (ví dụ: 6U 3D 10D 6D):")
                ext_line = input("Gọi tầng> ")
                external_requests = parse_external_requests(ext_line)
                break
            except ValueError as e:
                print(f">> Lỗi: {e} Vui lòng nhập lại.")

        while True:
            try:
                print("\n[BƯỚC 3] Nhập yêu cầu chọn tầng bên trong thang máy (ví dụ: 1:12 3:1 4:1):")
                cab_line = input("Chọn tầng> ")
                cabin_requests = parse_cabin_requests(cab_line)
                break
            except ValueError as e:
                print(f">> Lỗi: {e} Vui lòng nhập lại.")

        # Đưa yêu cầu vào 2 hàng đợi FIFO tách biệt theo hướng LÊN và XUỐNG
        up_external_queue = FIFOQueue()
        down_external_queue = FIFOQueue()
        for req in external_requests:
            if req.direction == "UP":
                up_external_queue.enqueue(req)
            else:
                down_external_queue.enqueue(req)

        dispatcher = GroupDispatcher(elevators, total_floors=TOTAL_FLOORS)
        logs = dispatcher.run_dispatch(up_external_queue, cabin_requests, down_queue=down_external_queue)

        routes = {}
        for elevator in elevators:
            routes[elevator.id] = elevator.complete_route()

        display_results(elevators, logs, routes)

        print("\nChọn lượt tiếp theo:")
        print("1. Giữ nguyên vị trí hiện tại của các thang và nhập yêu cầu mới")
        print("2. Đặt lại toàn bộ thang và nhập trạng thái ban đầu mới")
        while True:
            choice = input("Lựa chọn (1/2): ").strip()
            if choice == "1":
                break
            if choice == "2":
                elevators = read_initial_elevators()
                break
            print(">> Lựa chọn không hợp lệ. Vui lòng nhập 1 hoặc 2.")


if __name__ == "__main__":
    run_simulator()