# Maze Router

A Python-based routing algorithm for connecting electrical circuit nets on a grid. This project uses a Breadth-First Search (BFS) algorithm to find feasible paths between specified pins while avoiding obstacles, adhering to grid constraints, and considering multi-layer routing.

How It Works

	1.	Reads grid dimensions, obstacles, and net definitions from an input file.
	2.	Routes each net using BFS to connect pins sequentially.
	3.	Outputs the path for each net or indicates failure if routing is not possible.

 Input Format

The input file should have:
	1.	Grid Details:
         grid_width, grid_height, bend_penalty, via_penalty

  2.	Obstacles:
        OBS(layer, x, y)
    
  3.	Net Definitions:
        net_name(layer, x, y)(layer, x, y)
  4.	Example Input:
         10, 10, 1, 2
         OBS(1, 5, 5)
         net1(1, 0, 0)(1, 9, 9)

 Output Format

The output file contains:
	•	Routed paths for successful nets:
       net_name (layer, x, y) (layer, x, y) ...

Failure messages for unroutable nets:
  •	net_name failed to route.

  How to Run

	1.	Ensure Python 3 is installed.
	2.	Place the input file in the same directory as the script.
	3.	Update the file paths in the main() function:
         input_file = 'path_to_input_file'
         output_file = 'path_to_output_file'

Run the script:
    python maze_router.py  
