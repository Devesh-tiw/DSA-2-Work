# Partial Persistent Dynamic Graph
# Adjacency List + Fat Node Method

graph_nodes = {}
versions = {0: {"parent": None, "operation": "BASE", "name": "Base"}}
latest_version = 0


# -------------------- Core Functions --------------------

def create_version(operation):
    global latest_version
    new = latest_version + 1
    versions[new] = {"parent": latest_version, "operation": operation, "name": f"V{new}"}
    latest_version = new
    return new

def store_value(vertex, version, neighbours):
    graph_nodes[vertex]["history"][version] = neighbours.copy() if neighbours else None

def get_value(vertex, version):
    if vertex not in graph_nodes:
        return None
    current = version
    history = graph_nodes[vertex]["history"]
    while current is not None:
        if current in history:
            return history[current].copy() if history[current] else None
        current = versions[current]["parent"]
    return None

def get_adjacency(version):
    return {v: get_value(v, version) for v in graph_nodes if get_value(v, version) is not None}


# -------------------- Versioned Queries --------------------

def neighboursAt(v, version):
    return get_value(v, version)

def degreeAt(v, version):
    nbrs = get_value(v, version)
    return len(nbrs) if nbrs else 0

def edgeAt(u, v, version):
    nbrs = get_value(u, version)
    return v in nbrs if nbrs else False

def reachableAt(start, target, version):
    adj = get_adjacency(version)
    visited, stack = set(), [start]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node not in visited:
            visited.add(node)
            stack.extend(adj.get(node, []))
    return False


# -------------------- Space Measurement --------------------

def measure_space():
    fat_cost = sum(len(graph_nodes[v]["history"]) for v in graph_nodes)
    naive_cost = 0
    for v in versions:
        adj = get_adjacency(v)
        naive_cost += sum(len(nbrs) for nbrs in adj.values())
    print("\n=== Space Measurement ===")
    print("Fat-node entries:", fat_cost)
    print("Naive copy entries:", naive_cost)
    if naive_cost > 0:
        print("Space saving ratio:", round(fat_cost / naive_cost, 3))


# -------------------- Main Menu --------------------

def main():
    print("=== Partial Persistent Dynamic Graph ===")
    graph_nodes["A"] = {"history": {0: ["B"]}}
    graph_nodes["B"] = {"history": {0: ["A", "C"]}}
    graph_nodes["C"] = {"history": {0: ["B"]}}

    while True:
        print("\n=== Main Menu ===")
        print("Latest editable version: V", latest_version)
        print("1. Add Vertex")
        print("2. Add Edge")
        print("3. Remove Edge")
        print("4. Remove Vertex")
        print("5. Show Graph")
        print("6. Show Version History")
        print("7. Measure Space Usage")
        print("8. NeighboursAt / DegreeAt / EdgeAt / ReachableAt")
        print("9. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            v = input("Enter new vertex: ").strip()
            add_vertex(v)
        elif choice == "2":
            u = input("Enter first vertex: ").strip()
            v = input("Enter second vertex: ").strip()
            add_edge(u, v)
        elif choice == "3":
            u = input("Enter first vertex: ").strip()
            v = input("Enter second vertex: ").strip()
            remove_edge(u, v)
        elif choice == "4":
            v = input("Enter vertex to remove: ").strip()
            remove_vertex(v)
        elif choice == "5":
            v = int(input("Enter version number: "))
            show_graph(v)
        elif choice == "6":
            show_versions()
        elif choice == "7":
            measure_space()
        elif choice == "8":
            v = int(input("Enter version number: "))
            op = input("Query type (n/d/e/r): ").strip().lower()
            if op == "n":
                node = input("Enter vertex: ")
                print("Neighbours:", neighboursAt(node, v))
            elif op == "d":
                node = input("Enter vertex: ")
                print("Degree:", degreeAt(node, v))
            elif op == "e":
                u = input("Enter first vertex: ")
                w = input("Enter second vertex: ")
                print("Edge exists:", edgeAt(u, w, v))
            elif op == "r":
                s = input("Enter start vertex: ")
                t = input("Enter target vertex: ")
                print("Reachable:", reachableAt(s, t, v))
        elif choice == "9":
            print("Program ended.")
            break
        else:
            print("Invalid option.")


# -------------------- Update Operations --------------------

def add_vertex(vertex):
    adj = get_adjacency(latest_version)
    if vertex in adj:
        print("Vertex already exists.")
        return None
    new = create_version(("addVertex", vertex))
    if vertex not in graph_nodes:
        graph_nodes[vertex] = {"history": {}}
    store_value(vertex, new, [])
    print(f"Created V{new} with vertex {vertex}.")

def add_edge(u, v):
    adj = get_adjacency(latest_version)
    if u not in adj or v not in adj:
        print("Both vertices must exist.")
        return None
    if v in adj[u]:
        print("Edge already exists.")
        return None
    new = create_version(("addEdge", u, v))
    store_value(u, new, adj[u] + [v])
    store_value(v, new, adj[v] + [u])
    print(f"Created V{new} with edge ({u}, {v}).")

def remove_edge(u, v):
    adj = get_adjacency(latest_version)
    if u not in adj or v not in adj or v not in adj[u]:
        print("Edge does not exist.")
        return None
    new = create_version(("removeEdge", u, v))
    store_value(u, new, [x for x in adj[u] if x != v])
    store_value(v, new, [x for x in adj[v] if x != u])
    print(f"Created V{new} after removing edge ({u}, {v}).")

def remove_vertex(vertex):
    adj = get_adjacency(latest_version)
    if vertex not in adj:
        print("Vertex does not exist.")
        return None
    new = create_version(("removeVertex", vertex))
    for neighbour in adj[vertex]:
        store_value(neighbour, new, [x for x in adj[neighbour] if x != vertex])
    store_value(vertex, new, None)
    print(f"Created V{new} after removing vertex {vertex}.")


def show_graph(version):
    adj = get_adjacency(version)
    print(f"\nGraph at V{version} / {versions[version]['name']}")
    if not adj:
        print("Graph is empty.")
        return
    for v, nbrs in adj.items():
        print(f"{v} -> {nbrs}")
    print("Vertices:", list(adj.keys()))
    print("Edges:", sum(len(nbrs) for nbrs in adj.values()) // 2)

def show_versions():
    print("\nVersion History:")
    for v in sorted(versions):
        parent = versions[v]["parent"]
        op = versions[v]["operation"]
        print(f"V{v} <- V{parent} : {op}" if parent is not None else f"V{v} <- BASE")


if __name__ == "__main__":
    main()