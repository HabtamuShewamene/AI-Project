import heapq


def reconstruct_path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def grid_neighbors(grid, node):
    rows = len(grid)
    cols = len(grid[0])
    r, c = node
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
            yield (nr, nc)


def a_star_grid(grid, start, goal):
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = [(h(start, goal), 0, start)]
    parent = {start: None}
    best_cost = {start: 0}

    while frontier:
        _f, cost, node = heapq.heappop(frontier)
        if node == goal:
            return reconstruct_path(parent, goal), cost
        if cost != best_cost.get(node, float("inf")):
            continue
        for neighbor in grid_neighbors(grid, node):
            new_cost = cost + 1
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                parent[neighbor] = node
                heapq.heappush(frontier, (new_cost + h(neighbor, goal), new_cost, neighbor))
    return None, float("inf")


def main():
    maze = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [1, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
    ]
    start, goal = (1, 1), (7, 7)
    path, steps = a_star_grid(maze, start, goal)
    print("Best solution (A*):", path)
    print("Steps:", steps)


if __name__ == "__main__":
    main()
