#!/usr/bin/env python3
"""
Benchmark comparisons for three methods to obtain the K smallest items from a list,
for various values of K with different list sizes N (varying from 1,000 to 1,000,000).

For each method and each chosen K (as a percentage of N), the test is run 5 times
and the median runtime is recorded.

Methods benchmarked:
  1. Using built‐in sort: sort the list and slice the first K elements.
  2. Using heapq.nsmallest: use the heap‐based algorithm.
  3. Using quickselect: partition the list with selectlib.quickselect and slice the first K elements.

The benchmark results are then plotted as grouped bar charts (one per N value) in a vertical stack.
"""

import random
import timeit
import statistics
import heapq
import matplotlib.pyplot as plt
import selectlib

# Define benchmark methods
def bench_sort(values, K):
    """Sort a copy of the list and return the first K smallest items."""
    lst = values.copy()
    lst.sort()
    return lst[:K]

def bench_heapq(values, K):
    """Use heapq.nsmallest on a copy of the list to obtain the first K smallest items."""
    lst = values.copy()
    return heapq.nsmallest(K, lst)

def bench_quickselect(values, K):
    """
    Use selectlib.quickselect on a copy of the list to partition it so that the element at index K-1
    is in the correct sorted position; then sort and return the first K elements.
    """
    lst = values.copy()
    # Partition in-place so that the element at index (K-1) is in the correct position.
    selectlib.quickselect(lst, K - 1)
    result = lst[:K]
    result.sort()
    return result

# List of methods to benchmark
methods = {
    "sort": bench_sort,
    "heapq.nsmallest": bench_heapq,
    "quickselect": bench_quickselect,
}

def run_benchmarks():
    """
    Runs the benchmarks for different list sizes.
    For each N in N_VALUES, constructs a random list of integers and then, for each K (as a percentage of N),
    runs each method 5 times and records the median runtime.
    Returns a dictionary mapping each N to its benchmark results.
    """
    # List sizes to test (varying by a factor of 10)
    N_values = [1000, 10_000, 100_000, 1_000_000]
    # Percentages for K (0.1%, 1%, 10%, and 50% of N)
    percentages = [0.001, 0.01, 0.1, 0.5]

    overall_results = {}  # {N: {"K_values": [...], "results": {method: {K: time, ...}} } }

    for N in N_values:
        # Compute K values (ensure at least 1)
        K_VALUES = [max(1, int(N * p)) for p in percentages]
        print(f"\nBenchmarking for N = {N} (K values: {K_VALUES})")
        # Generate a random list of integers
        original = [random.randint(0, 1_000_000) for _ in range(N)]

        # Prepare results for this list size
        results = {method: {} for method in methods}

        # For each K value, run each method 5 times and take the median time
        for K in K_VALUES:
            print(f"  K = {K}")
            for name, func in methods.items():
                test_callable = lambda: func(original, K)
                times = timeit.repeat(stmt=test_callable, repeat=5, number=1)
                med = statistics.median(times)
                results[name][K] = med
                times_ms = [f"{t*1000:.3f}" for t in times]
                print(f"    {name:15}: median = {med*1000:.3f} ms  (runs: {times_ms} ms)")
        overall_results[N] = {"K_values": K_VALUES, "results": results}
    return overall_results

def plot_results(overall_results):
    """
    Creates a vertical stack of grouped bar charts.
    Each subplot corresponds to a different N value.
    For each subplot, the x-axis shows K along with its percentage of N,
    and the y-axis shows the median time in ms.
    """
    # Determine the number of charts (one for each N)
    num_charts = len(overall_results)
    fig, axes = plt.subplots(nrows=num_charts, ncols=1, figsize=(10, 4*num_charts))

    # If only one subplot, put it into a list for uniform processing.
    if num_charts == 1:
        axes = [axes]

    # Define bar appearance
    bar_width = 0.2
    method_offsets = {
        "sort": -bar_width,
        "heapq.nsmallest": 0,
        "quickselect": bar_width,
    }
    method_colors = {
        "sort": '#1f77b4',
        "heapq.nsmallest": '#ff7f0e',
        "quickselect": '#2ca02c'
    }

    # Sort the overall_results by N for proper ordering (smallest to largest)
    for ax, (N, data) in zip(axes, sorted(overall_results.items(), key=lambda x: x[0])):
        K_VALUES = data["K_values"]
        results = data["results"]
        # Create x positions (one per K value)
        x_positions = list(range(len(K_VALUES)))
        # Create x-axis labels as "K (percentage)"
        x_labels = [f"{K} ({(K/N)*100:.1f}%)" for K in K_VALUES]

        for method, timing_dict in results.items():
            # Extract times (convert seconds to milliseconds)
            times_ms = [timing_dict[K]*1000 for K in K_VALUES]
            # Compute adjusted positions for grouped bars
            positions = [x + method_offsets[method] for x in x_positions]
            bars = ax.bar(positions, times_ms, width=bar_width, label=method, color=method_colors.get(method))
            ax.bar_label(bars, fmt='%.2f', padding=3, fontsize=8)

        ax.set_title(f"N = {N}")
        ax.set_xlabel("K (percentage of N)")
        ax.set_ylabel("Median time (ms)")
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels)
        ax.legend(title="Method")
        ax.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle("Benchmark: Performance Comparison for Varying K and N", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('plot.png')
    plt.show()

if __name__ == '__main__':
    bench_results = run_benchmarks()
    plot_results(bench_results)
