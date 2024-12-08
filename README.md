#  Maze Routing Algorithm with Net Ordering Heuristic
# Overview
This project implements a Maze Routing Algorithm to solve grid-based routing problems in multi-layered VLSI design. The solution incorporates an advanced net ordering heuristic, optimizing routing efficiency by dynamically prioritizing nets based on their lengths. The project includes two Python modules:

router.py: Implements the maze routing algorithm.

visualization.py: Provides tools for visualizing the routed nets, obstacles, and vias.


# Features
1. Routing Algorithm (router.py)
Maze Routing Algorithm: Routes nets using a breadth-first search (BFS)-based approach, avoiding obstacles and considering penalties for bends and vias.
Net Ordering Heuristic: Sorts nets by length (ascending or descending) to reduce conflicts and improve routing efficiency.
Multi-layer Support: Routes nets across two layers with via penalties.
Metrics Tracking: Tracks:
Total routing cost
Total wire length
Longest route length
Number of vias used
2. Visualization (visualization.py)
Renders a 2D grid with:
Routed nets (color-coded by layers)
Obstacles (layer-specific colors)
Vias (marked in red)
Adds a legend for easy interpretation of grid elements.

# Project Files
router.py: Main routing logic with net ordering heuristic.
visualization.py: Visualization tools for routed output.
input.txt: Sample input file specifying grid dimensions, obstacles, and nets.
output.txt: Generated output file with routed paths and summary metrics.
README.md: Documentation file (this file).

# Setup and Usage
Requirements
Python 3.8+
Required libraries: matplotlib, heapq, sys
Install required packages:
      pip install matplotlib

Usage
Router (router.py)
Run the router with the following command:
      python3 router.py <input_file> <output_file> <sort_order>
Example: 
      python3 router.py input.txt output.txt asc

      


# How It Works

 Router Algorithm:

Parses input to extract grid info, obstacles, and nets.
Sorts nets by length using the specified order (asc or desc).
Routes nets sequentially, accounting for penalties and avoiding obstacles.
Updates grid and metrics dynamically.

 Visualization:

Reads the routed output file.
Displays a grid with routed nets, obstacles, and vias, using distinct colors for clarity.
Metrics Tracked
Total Cost: Sum of individual net costs (length + penalties).
Total Wire Length: Total grid cells occupied by all routed paths.
Longest Route Length: Length of the longest net in the solution.
Total Vias Used: Count of vias (layer transitions).
Future Improvements
Support for more layers.
Optimized algorithms for faster routing in large grids.
Integration with advanced visualization tools for 3D rendering.

# Work Distribution

All the work on the code was done collaboratively. 

Ahmed Emad: did most of the debugging.

Salma Kaffafy: did the presentation slides. 
