import heapq


def reconstruct_path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def a_star(graph, start, goal, heuristic):
    frontier = [(heuristic[start], 0, start)]
    parent = {start: None}
    best_cost = {start: 0}

    while frontier:
        _f, cost, node = heapq.heappop(frontier)
        if node == goal:
            return reconstruct_path(parent, goal), cost
        if cost != best_cost.get(node, float("inf")):
            continue
        for neighbor, edge_cost in graph.get(node, []):
            new_cost = cost + edge_cost
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                parent[neighbor] = node
                heapq.heappush(frontier, (new_cost + heuristic[neighbor], new_cost, neighbor))
    return None, float("inf")


def main():
    graph = {
        "A": [("B", 2), ("C", 5)],
        "B": [("A", 2), ("D", 4), ("E", 1)],
        "C": [("A", 5), ("E", 2)],
        "D": [("B", 4), ("F", 3)],
        "E": [("B", 1), ("C", 2), ("F", 6), ("G", 7)],
        "F": [("D", 3), ("E", 6), ("G", 1)],
        "G": [("E", 7), ("F", 1)],
    }
    heuristic = {"A": 7, "B": 6, "C": 7, "D": 3, "E": 6, "F": 1, "G": 0}
    path, cost = a_star(graph, "A", "G", heuristic)
    print("Best solution (A*):", path)
    print("Total cost:", cost)


if __name__ == "__main__":
    main()
