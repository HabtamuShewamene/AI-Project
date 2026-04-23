from collections import deque


def reconstruct_path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def bfs_web(graph, start, goal):
    frontier = deque([start])
    parent = {start: None}
    while frontier:
        node = frontier.popleft()
        if node == goal:
            return reconstruct_path(parent, goal)
        for neighbor in graph.get(node, []):
            if neighbor not in parent:
                parent[neighbor] = node
                frontier.append(neighbor)
    return None


def main():
    web_graph = {
        "Home": ["About", "Blog", "Shop"],
        "About": ["Team", "Careers"],
        "Blog": ["Post1", "Post2"],
        "Shop": ["Product", "Cart"],
        "Team": ["Target"],
        "Careers": [],
        "Post1": [],
        "Post2": [],
        "Product": ["Target"],
        "Cart": [],
        "Target": [],
    }
    path = bfs_web(web_graph, "Home", "Target")
    print("Best solution (BFS - shortest clicks):", path)


if __name__ == "__main__":
    main()
