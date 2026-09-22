# Fully Persistent Dynamic Graph
# Adjacency List + Fat Node Method

graph_nodes = {}
versions = {0: {"parent": None, "operation": "BASE", "name": "Base"}}
latest_version = 0


# -------------------- Core Functions --------------------

def create_version(operation, parent_version):
    """Create a new version branching from any parent version."""
    global latest_version
    new = latest_version + 1
    versions[new] = {
        "parent": parent_version,
        "operation": operation,
        "name": f"V{new}"
    }
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
# -------------------- Update Operations --------------------

def add_vertex(vertex, base_version):
    adj = get_adjacency(base_version)
    if vertex in adj:
        print("Vertex already exists.")
        return None
    new = create_version(("addVertex", vertex), base_version)
    if vertex not in graph_nodes:
        graph_nodes[vertex] = {"history": {}}
    store_value(vertex, new, [])
    print(f"Created V{new} with vertex {vertex} (branched from V{base_version}).")

def add_edge(u, v, base_version):
    adj = get_adjacency(base_version)
    if u not in adj or v not in adj:
        print("Both vertices must exist.")
        return None
    if v in adj[u]:
        print("Edge already exists.")
        return None
    new = create_version(("addEdge", u, v), base_version)
    store_value(u, new, adj[u] + [v])
    store_value(v, new, adj[v] + [u])
    print(f"Created V{new} with edge ({u}, {v}) (branched from V{base_version}).")

def remove_edge(u, v, base_version):
    adj = get_adjacency(base_version)
    if u not in adj or v not in adj or v not in adj[u]:
        print("Edge does not exist.")
        return None
    new = create_version(("removeEdge", u, v), base_version)
    store_value(u, new, [x for x in adj[u] if x != v])
    store_value(v, new, [x for x in adj[v] if x != u])
    print(f"Created V{new} after removing edge ({u}, {v}) (branched from V{base_version}).")

def remove_vertex(vertex, base_version):
    adj = get_adjacency(base_version)
    if vertex not in adj:
        print("Vertex does not exist.")
        return None
    new = create_version(("removeVertex", vertex), base_version)
    for neighbour in adj[vertex]:
        store_value(neighbour, new, [x for x in adj[neighbour] if x != vertex])
    store_value(vertex, new, None)
    print(f"Created V{new} after removing vertex {vertex} (branched from V{base_version}).")


# -------------------- Queries --------------------

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


# -------------------- Modify Version --------------------

def modify_version(version):
    if version not in versions:
        print("Version does not exist.")
        return
    print(f"Current info: {versions[version]}")
    new_name = input("Enter new name (leave blank to keep): ").strip()
    new_op = input("Enter new operation (leave blank to keep): ").strip()

    if new_name:
        versions[version]["name"] = new_name
    if new_op:
        versions[version]["operation"] = new_op

    print(f"Version V{version} updated: {versions[version]}")


# -------------------- Main Menu --------------------

def main():
    print("=== Fully Persistent Dynamic Graph ===")
    graph_nodes["A"] = {"history": {0: ["B"]}}
    graph_nodes["B"] = {"history": {0: ["A", "C"]}}
    graph_nodes["C"] = {"history": {0: ["B"]}}

    while True:
        print("\n=== Main Menu ===")
        print("Latest created version: V", latest_version)
        print("1. Add Vertex")
        print("2. Add Edge")
        print("3. Remove Edge")
        print("4. Remove Vertex")
        print("5. Show Graph")
        print("6. Show Version History")
        print("7. Modify Version")
        print("8. Measure Space Usage")
        print("9. NeighboursAt / DegreeAt / EdgeAt / ReachableAt")
        print("10. Exit")
        choice = input("Choose: ").strip()

        if choice == "9":
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

        elif choice == "10":
            print("Program ended.")
            break
        # keep other options same as before...

if __name__ == "__main__":
    main()