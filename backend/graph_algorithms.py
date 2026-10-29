"""Genuine search and graph pathfinding algorithms with step-by-step traces.

Supports:
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform-Cost Search (UCS)
- Greedy Best-First Search
- A* Search
- Hill Climbing Local Search
"""
import heapq
import math
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Dict[str, Any]]] = {}

    def add_node(self, node_id: str, label: Optional[str] = None, data: Optional[Dict[str, Any]] = None, x: float = 0.0, y: float = 0.0):
        self.nodes[node_id] = {
            "id": node_id,
            "label": label or node_id,
            "data": data or {},
            "x": x,
            "y": y
        }
        if node_id not in self.adj:
            self.adj[node_id] = []

    def add_edge(self, u: str, v: str, weight: float = 1.0, relation: str = "relates", data: Optional[Dict[str, Any]] = None):
        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)
        self.adj[u].append({"target": v, "weight": float(weight), "relation": relation, "data": data or {}})
        if not self.directed:
            self.adj[v].append({"target": u, "weight": float(weight), "relation": relation, "data": data or {}})

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        return self.adj.get(node_id, [])

    def euclidean_heuristic(self, u: str, target: str) -> float:
        n1 = self.nodes.get(u, {})
        n2 = self.nodes.get(target, {})
        x1, y1 = n1.get("x", 0.0), n1.get("y", 0.0)
        x2, y2 = n2.get("x", 0.0), n2.get("y", 0.0)
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def reconstruct_path(parents: Dict[str, Optional[str]], current: str) -> List[str]:
    path = []
    curr: Optional[str] = current
    while curr is not None:
        path.append(curr)
        curr = parents.get(curr)
    path.reverse()
    return path


def bfs(graph: Graph, start: str, target: str) -> Dict[str, Any]:
    """Breadth-First Search with full frontier state and cycle prevention."""
    if start not in graph.nodes or target not in graph.nodes:
        return {"found": False, "path": [], "steps": [], "visited": [], "error": "Start or target node not found in graph"}

    queue = deque([start])
    visited_order: List[str] = []
    visited_set: Set[str] = {start}
    parents: Dict[str, Optional[str]] = {start: None}
    steps: List[Dict[str, Any]] = []

    step_idx = 0
    found = False

    while queue:
        step_idx += 1
        current = queue.popleft()
        visited_order.append(current)

        step_info = {
            "step": step_idx,
            "current": current,
            "frontier": list(queue),
            "visited": list(visited_order),
            "action": f"Exploring node '{current}'"
        }

        if current == target:
            found = True
            step_info["action"] = f"Target '{target}' reached!"
            steps.append(step_info)
            break

        # Explore neighbors
        for edge in graph.get_neighbors(current):
            nxt = edge["target"]
            if nxt not in visited_set:
                visited_set.add(nxt)
                parents[nxt] = current
                queue.append(nxt)

        step_info["frontier_after"] = list(queue)
        steps.append(step_info)

    path = reconstruct_path(parents, target) if found else []
    return {
        "algorithm": "Breadth-First Search (BFS)",
        "found": found,
        "path": path,
        "path_length": len(path),
        "steps": steps,
        "visited_count": len(visited_order),
        "visited": visited_order
    }


def dfs(graph: Graph, start: str, target: str) -> Dict[str, Any]:
    """Depth-First Search with full frontier/stack state and cycle prevention."""
    if start not in graph.nodes or target not in graph.nodes:
        return {"found": False, "path": [], "steps": [], "visited": [], "error": "Start or target node not in graph"}

    stack = [start]
    visited_order: List[str] = []
    visited_set: Set[str] = set()
    parents: Dict[str, Optional[str]] = {start: None}
    steps: List[Dict[str, Any]] = []

    step_idx = 0
    found = False

    while stack:
        step_idx += 1
        current = stack.pop()
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)

        step_info = {
            "step": step_idx,
            "current": current,
            "frontier": list(stack),
            "visited": list(visited_order),
            "action": f"Popped '{current}' from stack"
        }

        if current == target:
            found = True
            step_info["action"] = f"Target '{target}' reached!"
            steps.append(step_info)
            break

        # Push unvisited neighbors in reverse for natural ordering
        neighbors = graph.get_neighbors(current)
        for edge in reversed(neighbors):
            nxt = edge["target"]
            if nxt not in visited_set:
                parents[nxt] = current
                stack.append(nxt)

        step_info["frontier_after"] = list(stack)
        steps.append(step_info)

    path = reconstruct_path(parents, target) if found else []
    return {
        "algorithm": "Depth-First Search (DFS)",
        "found": found,
        "path": path,
        "path_length": len(path),
        "steps": steps,
        "visited_count": len(visited_order),
        "visited": visited_order
    }


def uniform_cost_search(graph: Graph, start: str, target: str) -> Dict[str, Any]:
    """Uniform-Cost Search (Dijkstra) with priority queue and path cost."""
    if start not in graph.nodes or target not in graph.nodes:
        return {"found": False, "path": [], "steps": [], "cost": 0.0, "error": "Node not in graph"}

    pq: List[Tuple[float, int, str]] = []
    counter = 0
    heapq.heappush(pq, (0.0, counter, start))
    dist: Dict[str, float] = {start: 0.0}
    parents: Dict[str, Optional[str]] = {start: None}
    visited_order: List[str] = []
    visited_set: Set[str] = set()
    steps: List[Dict[str, Any]] = []

    step_idx = 0
    found = False

    while pq:
        cost, _, current = heapq.heappop(pq)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        step_idx += 1

        step_info = {
            "step": step_idx,
            "current": current,
            "cost_so_far": round(cost, 2),
            "frontier": [(round(c, 2), node) for c, _, node in pq],
            "visited": list(visited_order),
            "action": f"Expanding '{current}' with g={round(cost, 2)}"
        }

        if current == target:
            found = True
            step_info["action"] = f"Target reached with optimal cost {round(cost, 2)}"
            steps.append(step_info)
            break

        for edge in graph.get_neighbors(current):
            nxt = edge["target"]
            w = edge["weight"]
            new_cost = cost + w
            if nxt not in dist or new_cost < dist[nxt]:
                dist[nxt] = new_cost
                parents[nxt] = current
                counter += 1
                heapq.heappush(pq, (new_cost, counter, nxt))

        step_info["frontier_after"] = [(round(c, 2), node) for c, _, node in pq]
        steps.append(step_info)

    path = reconstruct_path(parents, target) if found else []
    return {
        "algorithm": "Uniform-Cost Search (UCS)",
        "found": found,
        "path": path,
        "path_cost": round(dist.get(target, 0.0), 2) if found else None,
        "steps": steps,
        "visited_count": len(visited_order),
        "visited": visited_order
    }


def greedy_best_first_search(graph: Graph, start: str, target: str, heuristic: Optional[Callable[[str, str], float]] = None) -> Dict[str, Any]:
    """Greedy Best-First Search guided by heuristic h(n)."""
    if start not in graph.nodes or target not in graph.nodes:
        return {"found": False, "path": [], "steps": [], "error": "Node not in graph"}

    h_fn = heuristic or graph.euclidean_heuristic
    pq: List[Tuple[float, int, str]] = []
    counter = 0
    start_h = h_fn(start, target)
    heapq.heappush(pq, (start_h, counter, start))
    parents: Dict[str, Optional[str]] = {start: None}
    visited_order: List[str] = []
    visited_set: Set[str] = set()
    steps: List[Dict[str, Any]] = []

    step_idx = 0
    found = False

    while pq:
        h_val, _, current = heapq.heappop(pq)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        step_idx += 1

        step_info = {
            "step": step_idx,
            "current": current,
            "heuristic_h": round(h_val, 2),
            "frontier": [(round(h, 2), node) for h, _, node in pq],
            "visited": list(visited_order),
            "action": f"Expanding '{current}' with h={round(h_val, 2)}"
        }

        if current == target:
            found = True
            step_info["action"] = f"Target reached via greedy heuristic"
            steps.append(step_info)
            break

        for edge in graph.get_neighbors(current):
            nxt = edge["target"]
            if nxt not in visited_set:
                parents[nxt] = current
                counter += 1
                heapq.heappush(pq, (h_fn(nxt, target), counter, nxt))

        step_info["frontier_after"] = [(round(h, 2), node) for h, _, node in pq]
        steps.append(step_info)

    path = reconstruct_path(parents, target) if found else []
    return {
        "algorithm": "Greedy Best-First Search",
        "found": found,
        "path": path,
        "path_length": len(path),
        "steps": steps,
        "visited_count": len(visited_order),
        "visited": visited_order
    }


def astar_search(graph: Graph, start: str, target: str, heuristic: Optional[Callable[[str, str], float]] = None) -> Dict[str, Any]:
    """A* Search combining path cost g(n) and heuristic h(n) where f(n) = g(n) + h(n)."""
    if start not in graph.nodes or target not in graph.nodes:
        return {"found": False, "path": [], "steps": [], "cost": 0.0, "error": "Node not in graph"}

    h_fn = heuristic or graph.euclidean_heuristic
    pq: List[Tuple[float, float, int, str]] = []  # (f_score, g_score, counter, node)
    counter = 0
    g_score: Dict[str, float] = {start: 0.0}
    f_start = h_fn(start, target)
    heapq.heappush(pq, (f_start, 0.0, counter, start))
    parents: Dict[str, Optional[str]] = {start: None}
    visited_order: List[str] = []
    visited_set: Set[str] = set()
    steps: List[Dict[str, Any]] = []

    step_idx = 0
    found = False

    while pq:
        f_val, g_val, _, current = heapq.heappop(pq)
        if current in visited_set:
            continue
        visited_set.add(current)
        visited_order.append(current)
        step_idx += 1

        step_info = {
            "step": step_idx,
            "current": current,
            "g_cost": round(g_val, 2),
            "h_cost": round(f_val - g_val, 2),
            "f_total": round(f_val, 2),
            "frontier": [(round(f, 2), node) for f, _, _, node in pq],
            "visited": list(visited_order),
            "action": f"Expanding '{current}' with f={round(f_val, 2)} (g={round(g_val, 2)}, h={round(f_val - g_val, 2)})"
        }

        if current == target:
            found = True
            step_info["action"] = f"Target reached with optimal f={round(f_val, 2)}"
            steps.append(step_info)
            break

        for edge in graph.get_neighbors(current):
            nxt = edge["target"]
            tentative_g = g_val + edge["weight"]
            if nxt not in g_score or tentative_g < g_score[nxt]:
                g_score[nxt] = tentative_g
                parents[nxt] = current
                h_val_nxt = h_fn(nxt, target)
                f_val_nxt = tentative_g + h_val_nxt
                counter += 1
                heapq.heappush(pq, (f_val_nxt, tentative_g, counter, nxt))

        step_info["frontier_after"] = [(round(f, 2), node) for f, _, _, node in pq]
        steps.append(step_info)

    path = reconstruct_path(parents, target) if found else []
    return {
        "algorithm": "A* Search",
        "found": found,
        "path": path,
        "path_cost": round(g_score.get(target, 0.0), 2) if found else None,
        "steps": steps,
        "visited_count": len(visited_order),
        "visited": visited_order
    }


def hill_climbing(problem_states: Dict[str, float], neighbors: Dict[str, List[str]], initial_state: str) -> Dict[str, Any]:
    """Hill Climbing local search with local peak detection."""
    current = initial_state
    steps: List[Dict[str, Any]] = []
    step_idx = 0

    while True:
        step_idx += 1
        curr_score = problem_states.get(current, 0.0)
        curr_neighbors = neighbors.get(current, [])
        best_neighbor = None
        best_score = curr_score

        for n in curr_neighbors:
            score = problem_states.get(n, 0.0)
            if score > best_score:
                best_score = score
                best_neighbor = n

        steps.append({
            "step": step_idx,
            "current_state": current,
            "current_value": round(curr_score, 3),
            "candidate_neighbors": [(n, round(problem_states.get(n, 0.0), 3)) for n in curr_neighbors],
            "action": f"Moved to '{best_neighbor}' (value: {round(best_score, 3)})" if best_neighbor else "Local maximum reached: no neighbor has higher value."
        })

        if best_neighbor is None or best_score <= curr_score:
            break
        current = best_neighbor

    return {
        "algorithm": "Hill Climbing Search",
        "final_state": current,
        "final_value": round(problem_states.get(current, 0.0), 3),
        "steps": steps,
        "total_steps": step_idx
    }
