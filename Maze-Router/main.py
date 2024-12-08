from collections import deque

class MazeRouter:
    def _init_(self, grid_width, grid_height, bend_penalty, via_penalty):
        print(f"Initializing MazeRouter with grid {grid_width}x{grid_height}, "
              f"bend_penalty={bend_penalty}, via_penalty={via_penalty}")
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        self.obstacles = set()  # Set of tuples (layer, x, y)

    def add_obstacle(self, layer, x, y):
        print(f"Adding obstacle at layer={layer}, ({x}, {y})")
        self.obstacles.add((layer, x, y))

    def is_valid(self, layer, x, y):
        valid = (0 <= x < self.grid_width and
                 0 <= y < self.grid_height and
                 (layer, x, y) not in self.obstacles)
        return valid

    def bfs(self, start, end):
        print(f"Running BFS from {start} to {end}")
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
        queue = deque([start])
        came_from = {start: None}
        path = []

        while queue:
            current = queue.popleft()

            if current == end:
                while current:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for direction in directions:
                neighbor = (current[0], current[1] + direction[0], current[2] + direction[1])
                if self.is_valid(neighbor[0], neighbor[1], neighbor[2]) and neighbor not in came_from:
                    queue.append(neighbor)
                    came_from[neighbor] = current

        return None

    def route_net(self, pins):
        path = []
        for i in range(len(pins) - 1):
            start = pins[i]
            end = pins[i + 1]
            segment = self.bfs(start, end)
            if segment is None:
                print(f"Failed to route segment from {start} to {end}")
                return None
            path.extend(segment[:-1])
        path.append(pins[-1])
        return path

    def generate_output(self, nets, output_file):
        with open(output_file, 'w') as f:
            for net_name, pins in nets.items():
                print(f"Routing net: {net_name}")
                path = self.route_net(pins)
                if path:
                    f.write(f"{net_name} ")
                    for (layer, x, y) in path:
                        f.write(f"({layer}, {x}, {y}) ")
                    f.write("\n")
                    print(f"Net {net_name} routed successfully.")
                else:
                    f.write(f"{net_name} failed to route.\n")
                    print(f"Failed to route net: {net_name}")

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
    input_file = r'C:\Users\ae912\OneDrive\Desktop\DSP\pythonProject\input.txt'
    output_file = r'C:\Users\ae912\OneDrive\Desktop\DSP\pythonProject\output.txt'

    print("Starting routing process...")
    router, nets = parse_input(input_file)

    if router and nets:
        router.generate_output(nets, output_file)
        print(f"Routing completed. Output saved to {output_file}")
    else:
        print("Failed to initialize router or parse nets. Exiting...")

if __name__ == "__main__":
    main()