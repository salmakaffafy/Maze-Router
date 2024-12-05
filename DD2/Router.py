from heapq import heappop, heappush
import sys  # For argc and argv

class MazeRouter:
    def __init__(self, grid_width, grid_height, bend_penalty, via_penalty):
        print(f"Initializing MazeRouter with grid {grid_width}x{grid_height}, "
              f"bend_penalty={bend_penalty}, via_penalty={via_penalty}")
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        self.obstacles = set()  # Set of tuples (layer, x, y)
        self.used_pins = set()  # Set of pins used by other nets
        self.total_cost = 0  # Total routing cost
        self.total_wire_length = 0  # Total wire length
        self.longest_route_length = 0  # Length of the longest routed net
        self.total_vias = 0  # Total number of vias used

    def add_obstacle(self, layer, x, y):
        print(f"Adding obstacle at layer={layer}, ({x}, {y})")
        self.obstacles.add((layer, x, y))

    def is_valid(self, layer, x, y):
        valid = (0 <= x < self.grid_width and
                 0 <= y < self.grid_height and
                 (layer, x, y) not in self.obstacles and
                 (layer, x, y) not in self.used_pins)  # Block pins used by other nets
        return valid

    def bfs(self, start, end):
        print(f"Running BFS from {start} to {end}")
        directions = [
            (0, 1),  # Right
            (0, -1),  # Left
            (1, 0),  # Down
            (-1, 0),  # Up
        ]
        queue = []
        heappush(queue, (0, start, None))  # (cost, position, last_direction)
        came_from = {start: None}
        cost_so_far = {start: 0}

        while queue:
            current_cost, current, last_direction = heappop(queue)

            if current == end:
                self.total_cost += current_cost  # Update total cost
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            layer, x, y = current

            # Explore neighbors
            for i, direction in enumerate(directions):
                neighbor = (layer, x + direction[0], y + direction[1])
                if self.is_valid(*neighbor):
                    # Calculate movement cost
                    movement_cost = 1
                    if last_direction is not None and last_direction != i:
                        movement_cost += self.bend_penalty  # Add bend penalty if direction changes

                    new_cost = current_cost + movement_cost
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        heappush(queue, (new_cost, neighbor, i))
                        came_from[neighbor] = current

            # Handle layer changes (via)
            for new_layer in range(2):  # Assuming 2 layers
                if new_layer != layer:
                    neighbor = (new_layer, x, y)
                    if self.is_valid(*neighbor):
                        new_cost = current_cost + self.via_penalty
                        if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                            cost_so_far[neighbor] = new_cost
                            heappush(queue, (new_cost, neighbor, last_direction))
                            came_from[neighbor] = current

        return None  # No path found

    def route_net(self, pins):
        path = []
        for i in range(len(pins) - 1):
            start = pins[i]
            end = pins[i + 1]
            segment = self.bfs(start, end)
            if segment is None:
                print(f"Failed to route segment from {start} to {end}")
                return None  # If any segment fails, the whole net fails
            path.extend(segment[:-1])  # Append all but the last point to avoid duplication
        path.append(pins[-1])  # Add the last pin's coordinates

        # Update metrics
        wire_length = len(path) - 1
        self.total_wire_length += wire_length
        self.longest_route_length = max(self.longest_route_length, wire_length)
        self.total_vias += sum(1 for (layer1, x, y), (layer2, _, _) in zip(path, path[1:]) if layer1 != layer2)

        # Add all routed pins to the used_pins set
        self.used_pins.update(path)
        return path

    def generate_output(self, nets, output_file):
        with open(output_file, 'w') as f:
            # Write grid info (first line)
            f.write(f"{self.grid_width}, {self.grid_height}, {self.bend_penalty}, {self.via_penalty}\n")
            print(f"Grid Info: {self.grid_width}, {self.grid_height}, {self.bend_penalty}, {self.via_penalty}")

            # Write obstacles
            for (layer, x, y) in self.obstacles:
                f.write(f"OBS({layer}, {x}, {y})\n")

            # Route each net and write results
            for net_name, pins in nets.items():
                print(f"Routing net: {net_name}")
                path = self.route_net(pins)
                if path:
                    f.write(f"{net_name} ")
                    for (layer, x, y) in path:
                        f.write(f"({layer}, {x}, {y}) ")
                    f.write("\n")
                else:
                    f.write(f"{net_name} failed to route.\n")

            # Write summary to the output file
            f.write("\nSummary:\n")
            f.write(f"Total cost of routing: {self.total_cost}\n")
            f.write(f"Total wire length: {self.total_wire_length}\n")
            f.write(f"Longest route length: {self.longest_route_length}\n")
            f.write(f"Total vias used: {self.total_vias}\n")

        # Print summary of routing to console
        print(f"Total cost of routing: {self.total_cost}")
        print(f"Total wire length: {self.total_wire_length}")
        print(f"Longest route length: {self.longest_route_length}")
        print(f"Total vias used: {self.total_vias}")


def parse_input(input_file):
    nets = {}
    router = None

    try:
        with open(input_file, 'r') as f:
            grid_info = f.readline().strip()
            grid_info = grid_info.split(', ')
            grid_width, grid_height = map(int, grid_info[:2])
            bend_penalty, via_penalty = map(int, grid_info[2:])

            router = MazeRouter(grid_width, grid_height, bend_penalty, via_penalty)

            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('OBS'):
                    parts = line.split('(')[1].split(')')[0].split(',')
                    layer, x, y = map(int, parts)
                    router.add_obstacle(layer, x, y)
                elif line.startswith('net'):
                    parts = line.split('(')
                    net_name = parts[0].strip()
                    pins = []
                    for part in parts[1:]:
                        part = part.split(')')[0]
                        layer, x, y = map(int, part.split(','))
                        pins.append((layer, x, y))
                    nets[net_name] = pins

        return router, nets

    except Exception as e:
        print(f"Error while parsing input file: {e}")
        return None, {}


def main():
    # Check for the correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python router.py <input_file> <output_file>")
        return

    # Get file paths from command-line arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print("Starting routing process...")
    router, nets = parse_input(input_file)

    if router and nets:
        router.generate_output(nets, output_file)
        print(f"Routing completed. Output saved to {output_file}")
    else:
        print("Failed to initialize router or parse nets. Exiting...")

if __name__ == "__main__":
    main()

