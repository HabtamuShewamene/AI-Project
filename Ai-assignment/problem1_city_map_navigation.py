# 01_city_map_navigation.py
import heapq

graph = {
    'Arad': {'Zerind': 75, 'Sibiu': 140, 'Timisoara': 118},
    'Zerind': {'Arad': 75, 'Oradea': 71},
    'Sibiu': {'Arad': 140, 'Fagaras': 99, 'Rimnicu': 80},
    'Timisoara': {'Arad': 118, 'Lugoj': 111},
    'Fagaras': {'Sibiu': 99, 'Bucharest': 211},
    'Rimnicu': {'Sibiu': 80, 'Pitesti': 97},
    'Pitesti': {'Rimnicu': 97, 'Bucharest': 101},
    'Oradea': {'Zerind': 71},
    'Lugoj': {'Timisoara': 111, 'Mehadia': 70},
    'Mehadia': {'Lugoj': 70, 'Drobeta': 75},
    'Drobeta': {'Mehadia': 75, 'Craiova': 120},
    'Craiova': {'Drobeta': 120, 'Rimnicu': 146, 'Pitesti': 138},
    'Bucharest': {}
}

def ucs(start, goal):
    pq = [(0, start, [])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        path = path + [node]

        if node == goal:
            return cost, path

        visited.add(node)

        for neighbor, w in graph[node].items():
            heapq.heappush(pq, (cost + w, neighbor, path))

print(ucs("Arad", "Bucharest"))