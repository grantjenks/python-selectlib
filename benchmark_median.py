#!/usr/bin/env python3
"""
Benchmark comparisons between the built‐in statistics.median_low function
and the selectlib selection functions (nth_element, quickselect, and heapselect)
for computing the median (low median for even lengths) of a list.

For each list size (ranging from 1,000 to 1,000,000 elements),
the script generates a random list of integers. For each method, the test is run 5 times
and the median runtime (in seconds) is recorded.

Methods benchmarked:
  1. median_low        – Uses statistics.median_low to compute the median.
  2. nth_element       – Uses selectlib.nth_element to partition the list so that the median element is positioned correctly.
  3. quickselect       – Uses selectlib.quickselect for the median selection.
  4. heapselect        – Uses selectlib.heapselect for the median selection.

The results are then displayed as a grouped bar chart with one group per list size.
"""

import random
import timeit
import statistics
import matplotlib.pyplot as plt
import selectlib  # our C extension module
import statistics as stats

# ---------------------------------------------------------------------------
# Benchmark method definitions
# Each method gets a copy of the original list and computes the median (low)
# using the corresponding approach.
# The median index is computed as (n-1)//2.
# ---------------------------------------------------------------------------

def bench_median_low(values):
    """
    Uses the built‐in statistics.median_low function.
    """
    lst = values.copy()
    # statistics.median_low returns the median (for even-length lists, the lower of the two)
    return stats.median_low(lst)

def bench_nth_element(values):
    """
    Uses selectlib.nth_element to repartition the list so that the median is at index (n-1)//2.
    After partitioning, the median is obtained directly.
    """
    lst = values.copy()
    n = len(lst)
    median_index = (n - 1) // 2
    selectlib.nth_element(lst, median_index)
    return lst[median_index]

def bench_quickselect(values):
    """
    Uses selectlib.quickselect to reposition the median element in the list.
    """
    lst = values.copy()
    n = len(lst)
    median_index = (n - 1) // 2
    selectlib.quickselect(lst, median_index)
    return lst[median_index]

def bench_heapselect(values):
    """
    Uses selectlib.heapselect to reposition the median element in the list.
    """
    lst = values.copy()
    n = len(lst)
    median_index = (n - 1) // 2
    selectlib.heapselect(lst, median_index)
    return lst[median_index]

# Dictionary of methods to benchmark.
methods = {
    "median_low": bench_median_low,
    "nth_element": bench_nth_element,
    "quickselect": bench_quickselect,
    "heapselect" : bench_heapselect,
}

# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------
def run_benchmarks():
    """
    Runs the benchmarks for various list sizes.
    For each list size N (from 1,000 to 1,000,000), a random list of integers is generated.
    For each method, the benchmark calls the method 5 times (using timeit.repeat)
    and the median runtime is recorded.
    Returns a dictionary mapping each list size to its benchmark results.
    """
    # List sizes to test
    N_values = [1000, 10_000, 100_000, 1_000_000]

    overall_results = {}  # {N: { method: time_in_seconds, ... } }

    for N in N_values:
        print(f"\nBenchmarking for N = {N:,} (median index = {(N-1)//2:,})")
        # Generate a random list of integers
        original = [random.randint(0, 1_000_000) for _ in range(N)]

        results = {}
        for name, func in methods.items():
            # Prepare a callable that calls the method for the given list
            test_callable = lambda: func(original)
            # Run 5 times
            times = timeit.repeat(stmt=test_callable, repeat=5, number=1)
            med_time = statistics.median(times)
            results[name] = med_time
            times_ms = [f"{t*1000:,.3f}" for t in times]  # format as milliseconds
            print(f"  {name:12}: median = {med_time*1000:,.3f} ms  (runs: {times_ms})")
        overall_results[N] = results
    return overall_results

# ---------------------------------------------------------------------------
# Plotting results
# ---------------------------------------------------------------------------
def plot_results(results):
    """
    Creates a grouped bar chart.
    Each group corresponds to a different list size N.
    Each bar in a group shows the median runtime (in ms) for a given method.
    """
    # Get the list sizes and sort them
    N_values = sorted(results.keys())
    num_groups = len(N_values)

    # Method ordering and colors (similar to benchmark.py)
    methods_order = ["median_low", "nth_element", "quickselect", "heapselect"]
    method_colors = {
        "median_low": '#1f77b4',
        "nth_element": '#ff7f0e',
        "quickselect": '#2ca02c',
        "heapselect":  '#d62728',
    }

    # X positions for the groups
    group_positions = list(range(num_groups))

    # Bar appearance settings
    bar_width = 0.18
    offsets = {
        "median_low": -1.5*bar_width,
        "nth_element": -0.5*bar_width,
        "quickselect": 0.5*bar_width,
        "heapselect":  1.5*bar_width,
    }

    plt.figure(figsize=(10, 6))

    # For each method, plot a bar for each list size
    for method in methods_order:
        times_ms = [results[N][method]*1000 for N in N_values]
        positions = [pos + offsets[method] for pos in group_positions]
        bars = plt.bar(positions, times_ms, width=bar_width, label=method, color=method_colors.get(method))
        plt.bar_label(bars, fmt='%.2f', padding=3, fontsize=8)

    # Configure x-axis with list sizes (formatted with commas)
    plt.xticks(group_positions, [f"{N:,}" for N in N_values])
    plt.xlabel("List size (N)")
    plt.ylabel("Time (ms)")
    plt.title("Benchmark: statistics.median_low vs. selectlib selection methods (median)")
    plt.legend(title="Method")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("plot_median.png")
    plt.show()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    bench_results = run_benchmarks()
    plot_results(bench_results)
