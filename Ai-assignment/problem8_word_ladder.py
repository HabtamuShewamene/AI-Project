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


def word_neighbors(word, word_set):
    letters = "abcdefghijklmnopqrstuvwxyz"
    neighbors = []
    for i in range(len(word)):
        for ch in letters:
            if ch == word[i]:
                continue
            cand = word[:i] + ch + word[i + 1 :]
            if cand in word_set:
                neighbors.append(cand)
    return neighbors


def bidirectional_bfs(start, goal, word_set):
    if start == goal:
        return [start]
    frontier_f = deque([start])
    frontier_b = deque([goal])
    parent_f = {start: None}
    parent_b = {goal: None}

    while frontier_f and frontier_b:
        meet = expand_frontier(frontier_f, parent_f, parent_b, word_set)
        if meet:
            return stitch_paths(parent_f, parent_b, meet)
        meet = expand_frontier(frontier_b, parent_b, parent_f, word_set)
        if meet:
            return stitch_paths(parent_f, parent_b, meet)
    return None


def expand_frontier(frontier, parent_this, parent_other, word_set):
    for _ in range(len(frontier)):
        word = frontier.popleft()
        for neighbor in word_neighbors(word, word_set):
            if neighbor not in parent_this:
                parent_this[neighbor] = word
                if neighbor in parent_other:
                    return neighbor
                frontier.append(neighbor)
    return None


def main():
    word_list = {"hit", "hot", "dot", "dog", "cog", "lot", "log", "lit", "lie", "pie", "pig", "fig"}
    path = bidirectional_bfs("hit", "cog", word_list)
    print("Best solution (Bidirectional BFS):", path)
    print("Moves:", len(path) - 1)


if __name__ == "__main__":
    main()
