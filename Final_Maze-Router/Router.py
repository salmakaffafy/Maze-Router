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
        self.initial_obstacles = set()  # To store original obstacles
        self.obstacles = set()  # Set of tuples (layer, x, y)
        self.used_pins = set()  # Set of pins used by other nets
        self.total_cost = 0  # Total routing cost
        self.total_wire_length = 0  # Total wire length
        self.longest_route_length = 0  # Length of the longest routed net
        self.total_vias = 0  # Total number of vias used
        self.net_costs = {}  # Dictionary to store costs of successfully routed nets

    def add_obstacle(self, layer, x, y):
        print(f"Adding obstacle at layer={layer}, ({x}, {y})")
        self.obstacles.add((layer, x, y))
        self.initial_obstacles.add((layer, x, y))  # Track initial obstacles

    def reset_state(self):
        """Reset the router's state to its initial configuration."""
        self.obstacles = self.initial_obstacles.copy()
        self.used_pins = set()
        self.total_cost = 0
        self.total_wire_length = 0
        self.longest_route_length = 0
        self.total_vias = 0

    def is_valid(self, layer, x, y):
        """Check if the given position is valid for routing (not out of bounds or blocked)."""
        return (0 <= x < self.grid_width and
                0 <= y < self.grid_height and
                (layer, x, y) not in self.obstacles and
                (layer, x, y) not in self.used_pins)

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
            current_cost_segment, current, last_direction = heappop(queue)

            if current == end:
                # Successfully routed the segment
                print(f"Segment successfully routed with cost: {current_cost_segment}")

                # Backtrack to construct the path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                for pin in path:
                    self.obstacles.add(pin)
                # Return the cost for this segment
                return path, current_cost_segment

            layer, x, y = current

            # Explore neighbors
            for i, direction in enumerate(directions):
                neighbor = (layer, x + direction[0], y + direction[1])
                if self.is_valid(*neighbor):
                    # Calculate movement cost
                    movement_cost = 1
                    if last_direction is not None and last_direction != i:
                        movement_cost += self.bend_penalty  # Add bend penalty if direction changes

                    new_cost = current_cost_segment + movement_cost
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        heappush(queue, (new_cost, neighbor, i))
                        came_from[neighbor] = current

            # Handle layer changes (via)
            for new_layer in range(2):  # Assuming 3 layers, layers 0 and 1
                if new_layer != layer:
                    neighbor = (new_layer, x, y)
                    if self.is_valid(*neighbor):
                        # Apply via penalty when moving to a different layer
                        new_cost = current_cost_segment + self.via_penalty
                        if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                            cost_so_far[neighbor] = new_cost
                            heappush(queue, (new_cost, neighbor, last_direction))
                            came_from[neighbor] = current

        print(f"Failed to route from {start} to {end}")
        return None, None  # No path found

    def route_net(self, net_name, pins):
        """Route a net by connecting its pins."""
        failed = False
        path = []
        current_net_cost = 0  # Track cost for the current net independently
        self.net_costs[net_name] = 0
        for i in range(len(pins) - 1):
            start = pins[i]
            end = pins[i + 1]
            segment, segment_cost = self.bfs(start, end)
            if segment is None:
                print(f"Failed to route segment from {start} to {end}")
                failed = True
                return None  # Abort routing for this net if any segment fails
            path.extend(segment[:-1])  # Avoid duplication
            current_net_cost += segment_cost  # Accumulate segment cost for this net
        path.append(pins[-1])  # Add the last pin


        # Update metrics
        self.total_wire_length += len(path) - 1
        self.longest_route_length = max(self.longest_route_length, len(path) - 1)
        self.total_vias += sum(1 for (layer1, _, _), (layer2, _, _) in zip(path, path[1:]) if layer1 != layer2)

        # Mark all visited points as used
        self.used_pins.update(path)
        self.obstacles.update(path)

        if not failed:
        # Save the cost of the successfully routed net
            self.net_costs[net_name] = current_net_cost
        print(f"Net {net_name} successfully routed. Current net cost: {current_net_cost}")
        return path

    def calculate_total_cost(self):
        """Recalculate total cost as the sum of successfully routed net costs."""
        self.total_cost = sum(self.net_costs.values())
        print(f"Total cost recalculated: {self.total_cost}")

    def calculate_net_lengths(self, nets):
        """Calculate the length of each net independently and return sorted nets."""
        net_lengths = []
        for net_name, pins in nets.items():
            self.reset_state()  # Reset to original state
            path = self.route_net(net_name, pins)  # Pass both net_name and pins
            if path:
                net_lengths.append((net_name, pins, len(path) - 1))  # Store name, pins, and length
        return sorted(net_lengths, key=lambda x: x[2])  # Sort by length

    def route_all_sorted_nets(self, sorted_nets):
        """Route all nets in the order provided."""
        self.reset_state()
        routed_paths = []
        for net_name, pins in sorted_nets:
            print(f"Routing sorted net: {net_name}")
            path = self.route_net(net_name, pins)  # Pass both net_name and pins
            if path:
                routed_paths.append((net_name, path))
            else:
                print(f"Failed to route net: {net_name}")
        return routed_paths

    def generate_output(self, nets, output_file):
        """Generate the output file with routing results."""
        print("Calculating net lengths and sorting them...")
        sorted_nets = self.calculate_net_lengths(nets)

        with open(output_file, 'w') as f:
            # Write grid info
            f.write(f"{self.grid_width}, {self.grid_height}, {self.bend_penalty}, {self.via_penalty}\n")

            # Write initial obstacles
            for (layer, x, y) in self.initial_obstacles:
                f.write(f"OBS({layer}, {x}, {y})\n")

            # Route sorted nets
            routed_paths = self.route_all_sorted_nets([(net_name, pins) for net_name, pins, _ in sorted_nets])
            for net_name, path in routed_paths:
                f.write(f"{net_name} ")
                for (layer, x, y) in path:
                    f.write(f"({layer}, {x}, {y}) ")
                f.write("\n")

            self.calculate_total_cost()
            # Write summary
            f.write("\nSummary:\n")
            f.write(f"Sorted nets by length:\n")
            for net_name, _, length in sorted_nets:
                f.write(f"{net_name}: {length}\n")
            f.write(f"Total cost of routing: {self.total_cost}\n")
            f.write(f"Total wire length: {self.total_wire_length}\n")
            f.write(f"Longest route length: {self.longest_route_length}\n")
            f.write(f"Total vias used: {self.total_vias}\n")


def parse_input(input_file):
    nets = {}
    router = None
    try:
        with open(input_file, 'r') as f:
            grid_info = f.readline().strip().split(', ')
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
                    pins = [tuple(map(int, part.split(')')[0].split(','))) for part in parts[1:]]
                    nets[net_name] = pins
    except Exception as e:
        print(f"Error parsing input file: {e}")
        return None, None
    return router, nets


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 maze_router.py <input_file> <output_file>")
        sys.exit(1)
    input_file, output_file = sys.argv[1:3]
    router, nets = parse_input(input_file)
    if router and nets:
        router.generate_output(nets, output_file)