# UTSA ICPC Lib (Python)

This is an instructive library meant for teaching and learning about data structures and algorithms used in competitive programming contests and similarly structured websites like LeetCode and Kattis. The focus is not on performance of the specific implementations, but abstracting the concepts elegantly so that they can be reused and related to one another, increasing the student's understanding of them as a whole. A problem that requires strict performance tuning may require rewriting a more efficient implementation or even using a faster language such as C.

## Instructional Usage

Because the data structures and algorithms are prebuilt in this library, the student can focus on how they are used in solving problems without worrying about they are implemented.

Another way to use the library is to remove the implementation of a particular data structure or algorithm, and have the student build it from scratch. Then the suite of unit tests can be run via simply running `pytest` to validate the code.

This library can also be used to show how to decompose problems and structure them in code so that a prebuilt algorithm can solve them.

## Usage

Add the `./python/src` folder to your `PYTHONPATH`. This library is built on Python 3.11, which is currently used by the PyPy project and thus some competitive programming sites such as Kattis. No external libraries are included.

Most competitive programming formats flatten all folder structures, and for this reason, no folder structure exists within the source folder.

Developers will want to create a virtual environment via:
- `python -m venv .venv` (`.venv` is the name of the virtual environment folder - you can change this if you wish.)
- Activate the virtual environment:
  - Linux / MacOS:
    - bash / zsh: `source .venv/scripts/activate`
    - fish: `source .venv/scripts/activate.fish`
    - csh / tcsh: `source .venv/scripts/activate.csh`
  - Windows
    - Command Prompt (cmd): `.venv\scripts\activate.bat`
    - PowerShell: `.\.venv\scripts\Activate.ps1`
    - Git Bash: `source .venv/scripts/activate` (note bash above)
- `python -m pip install ./python/src/requirements_dev.txt`

## Project Structure

### bag

This module contains implementations of "bags", which are objects that fundamentally have two operations: putting an item in (a `push`), and taking an item out (a `pop`). This library also includes `peek` to get the next item without `pop`ping it, the size via the `len()` function, and truthiness dependent on whether the bag is empty or not.

Common types of bags are the `Stack`, the `Queue`, and the `Heap` (sometimes called a `PriorityQueue`). Because there are multiple ways to implement these, the concrete classes include the name of the implementation used (such as a `ListHeap` using a `list` to create the heap).

### graph

A graph is a data structure that consists of nodes and edges that connect two nodes.

This library treats graphs as directed, weighted multigraphs. That is, all edges have directions (directed graph), and all edges have weight (weighted graph). Edges can connect the same node to itself, and multiple edges between the same nodes are allowed (multigraph). Read on to see how to simulate an undirected or unweighted graph.

An unweighted graph is very easy to implement. Algorithms can simply ignore the edge weight. By default, edges all have a weight of 1, which could potentially be used to count the number of steps taken in a traversal.

Similarly, to create an undirected graph, the edge direction can be ignored. Traversal is done with the `Direction` enum, which has the values `OUT`, `IN`, and `BOTH`. Thus, an undirected graph can be thought of as a graph where there is no edge `(u, v)` with a counterpart `(v, u)`, and the algorithm can simply utilize `Direction.BOTH` to traverse.

#### Abstract Base Classes

Importantly, a `Graph` is an abstract class. That is, it defines the methods that are available (such as getting the nodes, edges, and neighbors, as well as adding/removing them), but how the information is stored and retrieved is an implementation detail for subclasses. A graph can be constructed many ways (like the `bag`s above); currently there is `AdjacencySet`, `ElementSet`, and `EdgeLookup` as concrete classes.

The graph subclasses do not implement all of the methods if they are inefficient in doing so. For example, the `EdgeLookup` class is designed solely to get a list of edges from node `u` to `v` in constant time, but cannot efficiently count the number of edges. Trying to call a method which is not implemented will raise a `NotImplementedError` exception at runtime.

A programmer could combine the benefits and drawbacks of different implementations by creating a subclass composed of multiple concrete implementations (a composite graph model). Adding or removing a node or edge is broadcast to the underlying implementations, and the best implementation is picked for each method, such as the edge lookup question vs. the number of edges question.

### grid

This module provides helpers to turn a matrix into a graph for use in graph algorithms. There are also helpers to get nodes by their row and column. Note that these grid graphs can be connected in interesting ways such as knight movements.

This module also defines a `Point` class which is a helper around x/y and row/col representations of coordinates, since they are inverses of each other. These are integer coordinates.

### utils

Various utilities for common programming patterns not offered by the standard library.

