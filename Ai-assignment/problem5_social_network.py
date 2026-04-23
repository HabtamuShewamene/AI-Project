from collections import deque


def reconstruct_path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def stitch_paths(parent_f, parent_b, meet):
    path_f = reconstruct_path(parent_f, meet)
    path_b = reconstruct_path(parent_b, meet)
    path_b.reverse()
    return path_f[:-1] + path_b


def bidirectional_bfs(graph, start, goal):
    if start == goal:
        return [start]
    frontier_f = deque([start])
    frontier_b = deque([goal])
    parent_f = {start: None}
    parent_b = {goal: None}

    while frontier_f and frontier_b:
        meet = expand_frontier(graph, frontier_f, parent_f, parent_b)
        if meet:
            return stitch_paths(parent_f, parent_b, meet)
        meet = expand_frontier(graph, frontier_b, parent_b, parent_f)
        if meet:
            return stitch_paths(parent_f, parent_b, meet)
    return None


def expand_frontier(graph, frontier, parent_this, parent_other):
    for _ in range(len(frontier)):
        node = frontier.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in parent_this:
                parent_this[neighbor] = node
                if neighbor in parent_other:
                    return neighbor
                frontier.append(neighbor)
    return None


def main():
    social_graph = {
        "Alice": ["Bob", "Cara"],
        "Bob": ["Alice", "Dan", "Eve"],
        "Cara": ["Alice", "Dan"],
        "Dan": ["Bob", "Cara", "Eve"],
        "Eve": ["Bob", "Dan"],
    }
    path = bidirectional_bfs(social_graph, "Alice", "Eve")
    print("Best solution (Bidirectional BFS):", path)


if __name__ == "__main__":
    main()
