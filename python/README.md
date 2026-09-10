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

