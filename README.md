# Dynamic Graphs with Persistence

Partially and fully persistent dynamic graphs in pure Python, built with the **fat-node method**.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Persistence Models](#persistence-models)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Menu Reference](#menu-reference)
- [Version Queries](#version-queries)
- [Example Session](#example-session)
- [How It Works](#how-it-works)
- [Space Efficiency](#space-efficiency)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [Why It Matters](#why-it-matters)

---

## Overview

A dynamic graph changes over time as vertices and edges are added or removed. A **persistent** graph keeps every previous state accessible, so you can ask "what did the graph look like at version *k*?" at any point.

This project provides two implementations:

| File | Persistence model | Editable versions |
|------|-------------------|-------------------|
| `partial_persistent_graph.py` | Partial | Latest version only |
| `full_persistent_graph.py` | Full | Any version (branching) |

Both store changes with the **fat-node method**: each vertex keeps a timestamped record of its changes rather than a full copy of the graph per version.

---

## Persistence Models

### Partial Persistence
- Versions form a **linear chain**: `v0 → v1 → v2 → ...`
- Only the newest version can be modified.
- Older versions are **read-only** but fully queryable.

### Full Persistence
- Versions form a **branching version DAG**.
- Any version can be used as the base for a new edit, creating a new branch.
- Every version remains queryable.

```
Partial:   v0 ── v1 ── v2 ── v3

Full:      v0 ── v1 ── v2 ── v4
                   \
                    └── v3 ── v5
```

---

## Features

- **Dynamic graph operations**: `addVertex`, `addEdge`, `removeEdge`, `removeVertex`
- **Versioned display**: `show_graph` (graph at any version) and `show_versions` (version history)
- **Versioned queries**: `NeighboursAt`, `DegreeAt`, `EdgeAt`, and `ReachableAt` answer questions about the graph as it existed at any chosen version
- **Space measurement**: compares fat-node entry counts against a naïve full-copy approach
- **Menu-driven interface**: simple terminal interaction, no setup required
- **Modify Version** *(full persistence only)*: rename or update metadata of any version

---

## Project Structure

```
.
├── partial_persistent_graph.py   # Partial persistence (linear versions)
├── full_persistent_graph.py      # Full persistence (branching versions)
└── README.md
```

---

## Requirements

- **Python** 3.9 or newer
- **No external libraries**: standard library only
- **Tested on**: Ubuntu 20.04 LTS and Windows 10

---

## Getting Started

1. Place both Python files and this README in the same folder.
2. Open a terminal in that folder.
3. Run whichever version you want to explore:

```bash
# Partial persistence
python partial_persistent_graph.py
```

```bash
# Full persistence
python full_persistent_graph.py
```

On some systems you may need to use `python3` instead of `python`.

---

## Menu Reference

Both programs are menu-driven. Use the menu to:

| Action | Description |
|--------|-------------|
| Add vertex | Creates a new version containing the added vertex |
| Add edge | Creates a new version containing the added edge |
| Remove edge | Creates a new version with the edge removed |
| Remove vertex | Creates a new version with the vertex (and its incident edges) removed |
| Show graph | Prints the adjacency structure as of a chosen version |
| Show versions | Lists all versions and their history |
| Measure space | Compares fat-node entries with naïve-copy entries and prints the ratio |
| Modify version | *(Full persistence only)* Rename or update metadata of any version |
| NeighboursAt / DegreeAt / EdgeAt / ReachableAt | Query the graph as it existed at any chosen version (see below) |

> Exact menu numbering and prompts may differ slightly between the two programs. Follow the on-screen instructions.

---

## Version Queries

Four read-only queries answer questions about the graph as it existed at a chosen version, regardless of any later edits.

| Query | Inputs | Returns |
|-------|--------|---------|
| `NeighboursAt` | vertex, version | The vertices adjacent to the given vertex at that version |
| `DegreeAt` | vertex, version | The number of edges incident to the vertex at that version |
| `EdgeAt` | vertex u, vertex v, version | Whether an edge between u and v existed at that version |
| `ReachableAt` | source u, target v, version | Whether v can be reached from u by following edges at that version |

These queries never create a new version, so they are safe to run on any version in both the partial and full persistence programs.

---

## Example Session

An illustrative flow (your exact prompts and output formatting may differ):

```
1. Add vertex A          -> creates version 1
2. Add vertex B          -> creates version 2
3. Add edge A-B          -> creates version 3
4. Remove edge A-B       -> creates version 4
5. Show graph at v3      -> A and B connected by an edge
6. Show graph at v4      -> A and B present, no edge
7. Measure space         -> fat-node entries vs. naïve-copy entries
8. EdgeAt A B @ v3       -> True
9. EdgeAt A B @ v4       -> False
10. NeighboursAt A @ v3  -> {B}
11. DegreeAt A @ v4      -> 0
12. ReachableAt A B @ v3 -> True
```

Querying version 3 after version 4 has been created still returns the graph with the edge, which is the point of persistence.

---

## How It Works

### Fat-Node Method

Instead of copying the whole graph on every update, each node stores a list of `(version, value)` entries describing how it changed over time.

- **Update**: append a new entry tagged with the new version.
- **Query at version *v***: find the entry that applies to *v* and read its value.

For **partial persistence**, applicable entries are found along a single linear chain of versions. For **full persistence**, the version structure branches, so lookups must respect each version's ancestry.

---

## Space Efficiency

| Approach | What is stored per update |
|----------|---------------------------|
| **Fat-node** | Only the change itself |
| **Naïve copy** | A full copy of the adjacency list |

Total fat-node space grows with the **number of updates**, while naïve copying grows with the **number of versions × graph size**. The *Measure space* menu option prints both entry counts and their ratio so you can see the difference on your own data.

---

## Limitations

- **No DAG visualization**: versions are displayed as a list, not a drawn graph.
- **Approximate space measurement**: counts stored entries, not actual memory bytes.

---

## Future Work

- Render the version DAG (e.g., with Graphviz)
- Measure real memory usage instead of entry counts
- Add automated tests for version isolation and branching

---

## Why It Matters

Persistent data structures are valuable in **AI/ML pipelines** and **time-consistent feature construction**, where results must be reproducible across evolving datasets. Being able to query the exact state of a graph at any past version makes experiments auditable and repeatable.
