# Real-World Problems Solved Using Search Algorithms

This project implements all eight problems from the prompt and prints clear, per-algorithm results.

## 1) City Map Navigation (Route Planning)
**Goal:** Find the shortest/fastest path from Arad to Bucharest.

**Expected learning:** Compare BFS, UCS, A*, Greedy, and Bidirectional Search; understand optimal vs non-optimal paths.

**Clear answers:**
- **BFS:** Finds a path with the fewest edges, not necessarily the shortest distance.
- **UCS:** Finds the shortest distance (optimal).
- **A\*:** Finds the shortest distance (optimal) with an admissible heuristic.
- **Greedy:** Fast but can be non-optimal.
- **Bidirectional BFS:** Efficient for unweighted graphs, but non-optimal with weights.

## 2) Robot Pathfinding (Grid Navigation)
**Goal:** Move from (0,0) to (4,4) while avoiding obstacles.

**Expected learning:** BFS shortest path, DFS limitations, A* with heuristics.

**Clear answers:**
- **BFS:** Returns the shortest grid path.
- **DFS:** Can find a path, but often longer than BFS.
- **A\*:** Returns the shortest grid path using Manhattan distance.

## 3) 8-Puzzle Solver (Sliding Tile Puzzle)
**Goal:** Transform [1,2,3,4,0,5,6,7,8] into [1,2,3,4,5,6,7,8,0] with fewest moves.

**Expected learning:** Compare BFS vs A* using misplaced tiles heuristic.

**Clear answers:**
- **BFS:** Returns the minimum-move solution.
- **A\*:** Returns the same minimum-move solution, typically with fewer expansions.

## 4) Web Crawler Simulation
**Goal:** Reach the target webpage by following links.

**Expected learning:** BFS (level-order), DFS, and DLS (depth-limited).

**Clear answers:**
- **BFS:** Finds the shortest click path.
- **DFS:** Finds a path, but not necessarily the shortest.
- **DLS:** Finds a path only if it is within the depth limit.

## 5) Social Network Connection Finder
**Goal:** Find the shortest friendship chain between Alice and Eve.

**Expected learning:** Apply BFS and Bidirectional Search to find minimal connections.

**Clear answers:**
- **BFS:** Finds the shortest chain.
- **Bidirectional BFS:** Finds the same shortest chain with fewer expansions.

## 6) Network Packet Routing
**Goal:** Find the lowest-cost route from router A to router G.

**Expected learning:** Apply UCS and A* for optimal routing.

**Clear answers:**
- **UCS:** Returns the minimum total latency (optimal).
- **A\*:** Returns the same optimal route with a heuristic.
- **Greedy:** Fast but can be non-optimal.

## 7) Game AI Pathfinding
**Goal:** Move from (1,1) to (7,7) while avoiding walls.

**Expected learning:** Differences between DFS, Greedy, and A*.

**Clear answers:**
- **DFS:** Finds a path but usually not optimal.
- **Greedy:** Can be fast but may take longer routes.
- **A\*:** Finds the shortest path using a heuristic.

## 8) Word Ladder (Word Transformation Game)
**Goal:** Transform "hit" to "cog" using valid dictionary words.

**Expected learning:** Compare BFS, A*, and Bidirectional Search.

**Clear answers:**
- **BFS:** Finds the shortest word sequence.
- **A\*:** Finds the shortest sequence with a heuristic.
- **Bidirectional BFS:** Also finds the shortest sequence faster.

## Run
```bash
python search_real_world_problems.py
```

If you want only the Romania map problem, you can still run:
```bash
python search_algorithms_arad_bucharest.py
```
