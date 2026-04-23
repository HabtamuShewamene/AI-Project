import heapq


def reconstruct_path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def neighbors(state):
    idx = state.index(0)
    r, c = divmod(idx, 3)
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nidx = nr * 3 + nc
            new_state = list(state)
            new_state[idx], new_state[nidx] = new_state[nidx], new_state[idx]
            moves.append(tuple(new_state))
    return moves


def misplaced_tiles(state, goal):
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])


def a_star_puzzle(start, goal):
    frontier = [(misplaced_tiles(start, goal), 0, start)]
    parent = {start: None}
    best_cost = {start: 0}

    while frontier:
        _f, cost, state = heapq.heappop(frontier)
        if state == goal:
            return reconstruct_path(parent, goal), cost
        if cost != best_cost.get(state, float("inf")):
            continue
        for neighbor in neighbors(state):
            new_cost = cost + 1
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                parent[neighbor] = state
                heapq.heappush(frontier, (new_cost + misplaced_tiles(neighbor, goal), new_cost, neighbor))
    return None, float("inf")


def main():
    start = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    path, moves = a_star_puzzle(start, goal)
    print("Best solution (A* with misplaced tiles):")
    print("Moves:", moves)
    print("Path:")
    for state in path:
        print(state)


if __name__ == "__main__":
    main()
