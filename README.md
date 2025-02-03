# selectlib

selectlib is a lightweight C extension module for Python that implements several in‑place selection algorithms for efficiently finding the kth smallest element in an unsorted list. The module provides three main functions—`nth_element`, `quickselect`, and `heapselect`—that allow you to partition a list so that the element at a given index is in its final sorted position, without performing a full sort.

You can install selectlib using pip:

```bash
python -m pip install selectlib
```

## Features

- **In‑place partitioning using three different strategies:**
  - **`nth_element`:** An adaptive selection function that chooses the optimal strategy based on the target index. For small indices, it uses the heapselect method; otherwise, it starts with quickselect and falls back to heapselect if necessary.
  - **`quickselect`:** A classic partition‑based selection algorithm that uses random pivots to position the kth smallest element in its correct sorted order. If the operation exceeds an iteration limit, it automatically falls back to heapselect.
  - **`heapselect`:** A heap‑based approach that builds a fixed‑size max‑heap to efficiently locate the kth smallest element.
- **Performance as a feature!**
  Selectlib comes with benchmark scripts that run multiple tests for varying list sizes and selection percentages, then produce visual output as grouped bar charts.
- **Median Benchmarking:**
  In addition to the benchmark for selecting the k‑smallest elements, selectlib provides a dedicated median benchmark script (`benchmark_median.py`) that compares Python’s built‑in `statistics.median_low` with selectlib’s `nth_element`, `quickselect`, and `heapselect` methods for computing the median of a list. This benchmark runs the tests for list sizes ranging from 1,000 to 1,000,000 elements and displays the median computation performance in a grouped bar chart.

## Usage Example

Below is an example demonstrating how to use each of the three selection algorithms to find the kth smallest element in a list:

```python
import selectlib

data = [9, 3, 7, 1, 5, 8, 2]
k = 3  # We wish to position the element at index 3, as in a sorted list

# Using nth_element:
selectlib.nth_element(data, k)
print("After nth_element, kth smallest element is:", data[k])

# Reset the list for a fresh example:
data = [9, 3, 7, 1, 5, 8, 2]

# Using quickselect:
selectlib.quickselect(data, k)
print("After quickselect, kth smallest element is:", data[k])

# Reset the list:
data = [9, 3, 7, 1, 5, 8, 2]

# Using heapselect:
selectlib.heapselect(data, k)
print("After heapselect, kth smallest element is:", data[k])
```

You can also provide an optional key function to customize comparisons. For example, if you wish to determine the kth largest element rather than the kth smallest, simply negate the value in a lambda function:

```python
data = [15, 8, 22, 5, 13]
k = 2
selectlib.quickselect(data, k, key=lambda x: -x)
print("The kth largest element is:", data[k])
```

## Median Benchmarking

In addition to the k‑smallest elements benchmark, selectlib provides a median benchmark script named `benchmark_median.py`. This script compares the performance of the following methods for computing the median (using the low median for even‑length lists):

1. **`median_low`** – Uses Python’s built‑in `statistics.median_low`.
2. **`nth_element`** – Uses `selectlib.nth_element` to partition the list so that the median element is in place.
3. **`quickselect`** – Uses `selectlib.quickselect` for median selection.
4. **`heapselect`** – Uses `selectlib.heapselect` for median selection.

For each list size (from 1,000 to 1,000,000 elements), the script runs 5 iterations and records the median runtime. The performance results are then plotted as a grouped bar chart, with each group corresponding to a different list size.

![Median Benchmark Results](https://github.com/grantjenks/python-selectlib/blob/main/plot_median.png?raw=true)

To run the median benchmark, execute:

```bash
python benchmark_median.py
```

## K-Smallest Benchmarking

Selectlib comes with a benchmark script named `benchmark.py` that compares the following five methods to obtain the K smallest items from a list:

1. **`sort`** – Creates a sorted copy of the list and slices the first k elements.
2. **`heapq.nsmallest`** – Uses Python’s standard library heap algorithm.
3. **`quickselect`** – Partitions using `selectlib.quickselect`, then slices and sorts the first k elements.
4. **`heapselect`** – Partitions using `selectlib.heapselect`, then slices and sorts the first k elements.
5. **`nth_element`** – Partitions using `selectlib.nth_element`, then slices and sorts the first k elements.

For each list size (ranging from 1,000 to 1,000,000 elements) and for several values of k (0.2%, 1%, 10%, and 25% of N), each method is executed five times, and the median runtime is recorded. The benchmark results are then visualized as grouped bar charts.

![Benchmark Results](https://github.com/grantjenks/python-selectlib/blob/main/plot.png?raw=true)

To run the benchmark, execute:

```bash
python benchmark.py
```

## Development & Continuous Integration

Before installing locally, ensure you have a C compiler and the Python development headers installed for your platform.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/grantjenks/python-selectlib.git
   cd python-selectlib
   ```

2. **Build and install in editable mode:**

   ```bash
   python -m pip install -e .
   ```

This project uses GitHub Actions for CI/CD. The available workflows cover:

- **release.yml** – Builds wheels for multiple platforms and publishes packages to PyPI.
- **test.yml** – Runs automated tests and linting on multiple Python versions.

## License

selectlib is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for full details.
