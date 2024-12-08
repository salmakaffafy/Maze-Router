import matplotlib.pyplot as plt
import matplotlib.patches as patches


class MazeRouter:
    def __init__(self, width, height, bend_penalty, via_penalty):
        self.width = width
        self.height = height
        self.bend_penalty = bend_penalty
        self.via_penalty = via_penalty
        self.obstacles = []

    def add_obstacle(self, layer, x, y):
        self.obstacles.append((layer, x, y))


def parse_input_file(input_file):
    """
    Parses the input file to extract grid dimensions, obstacles, and nets.

    Args:
        input_file: Path to the input file.

    Returns:
        Tuple containing a MazeRouter instance and a dictionary of nets.
    """
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


def draw_routed_net(ax, path, net_color, via_color, wire_thickness):
    """
    Draws a routed net on the given axis.

    Args:
        ax: Matplotlib axis object.
        path: List of (layer, x, y) coordinates representing the net's path.
        net_color: Dictionary with colors for each layer (e.g., {0: 'blue', 1: 'yellow'}).
        via_color: Color for vias connecting layers.
        wire_thickness: The thickness of the wire (same as the obstacles).
    """
    # Draw wire segments first
    for i in range(len(path) - 1):
        layer1, x1, y1 = path[i]
        layer2, x2, y2 = path[i + 1]

        if layer1 == layer2:  # Same layer (horizontal or vertical)
            if x1 == x2:  # Vertical segment
                ax.plot([x1 + 0.5, x1 + 0.5], [min(y1, y2) + 0.5, max(y1, y2) + 0.5],
                        color=net_color[layer1], lw=wire_thickness)
            elif y1 == y2:  # Horizontal segment
                ax.plot([min(x1, x2) + 0.5, max(x1, x2) + 0.5], [y1 + 0.5, y1 + 0.5],
                        color=net_color[layer1], lw=wire_thickness)


    for i in range(len(path) - 1):
        layer1, x1, y1 = path[i]
        layer2, x2, y2 = path[i + 1]

        if layer1 != layer2:  # Same layer (horizontal or vertical)
            ax.add_patch(patches.Rectangle((x1 + 0.0, y1 + 0.0), 0.8, 0.8, color=via_color))


def visualize_routed_nets(input_file):
    """
    Visualizes the routed nets, obstacles, and vias from the routing output.

    Args:
        input_file (str): Path to the input file containing grid and obstacle information.
    """
    # Parse input and output files
    router, nets = parse_input_file(input_file)
    if not router or not nets:
        print("Error parsing the input or output files.")
        return

    # Check if nets were parsed correctly
    print("Parsed nets from output file:")
    for net_name, path in nets.items():
        print(f"Net: {net_name}, Path: {path}")

    grid_width = router.width
    grid_height = router.height
    obstacles = router.obstacles

    # Set up the plot
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_aspect('equal')
    ax.grid(which='both', color='gray', linestyle='--', linewidth=0.5)

    # Draw grid
    for x in range(grid_width):
        for y in range(grid_height):
            ax.add_patch(patches.Rectangle((x, y), 1, 1, edgecolor='gray', facecolor='white'))

    # Define layer-specific patterns/colors
    net_color = {0: 'blue', 1: 'yellow'}
    via_color = 'red'
    obstacle_color_layer1 = 'black'  # Color for layer 1 obstacles
    obstacle_color_layer2 = 'brown'  # Color for layer 2 obstacles

    # Set wire thickness to match obstacle size
    wire_thickness = 12  # Same thickness as obstacles

    # Draw obstacles with layer-specific colors
    for layer, x, y in obstacles:
        if layer == 0:
            ax.add_patch(patches.Rectangle((x, y), 1, 1, color=obstacle_color_layer1))
        elif layer == 1:
            ax.add_patch(patches.Rectangle((x, y), 1, 1, color=obstacle_color_layer2))

    # Draw each net
    for net_name, path in nets.items():
        if path:  # Check if path is valid
            draw_routed_net(ax, path, net_color, via_color, wire_thickness)

    # Add legend
    legend_patches = [
        patches.Patch(color='blue', label='M0'),
        patches.Patch(color='yellow', label='M1'),
        patches.Patch(color='red', label='VIA'),
        patches.Patch(color='black', label='Obstacle (Layer 1)'),
        patches.Patch(color='brown', label='Obstacle (Layer 2)')
    ]
    ax.legend(handles=legend_patches, loc='upper right')

    # Final touches
    ax.set_xticks(range(grid_width))
    ax.set_yticks(range(grid_height))
    ax.set_xticklabels(range(grid_width))
    ax.set_yticklabels(range(grid_height))
    plt.title("Routed Nets Visualization")
    plt.show()


if __name__ == "__main__":
    # Example input file path
    input_file = r'C:\Users\ae912\OneDrive\Desktop\DSP\pythonProject\output.txt'

    # Visualize the routed nets
    visualize_routed_nets(input_file)
