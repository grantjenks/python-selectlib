#!/usr/bin/env python3
"""
Benchmark comparisons for three methods to obtain the 100 smallest items from a list:

 1. Using the built-in sort: sort the list and slice the first 100 elements.
 2. Using heapq.nsmallest: use the heap-based algorithm.
 3. Using quickselect: partition the list with selectlib.quickselect and slice the first 100 elements.

Each method is run 5 times on the same randomly generated list, and the median runtime is computed.
The results are then plotted as a bar chart using matplotlib with the 'fivethirtyeight' style.
"""

import random
import timeit
import statistics
import heapq
import matplotlib.pyplot as plt
import selectlib

N = 100_000
K = 10_000

# ----------------------------
# Benchmark methods definition
# ----------------------------

def bench_sort(values):
    """Sort the list in-place and return the K smallest items."""
    lst = values.copy()
    lst.sort()
    return lst[:K]

def bench_heapq(values):
    """Use heapq.nsmallest to obtain the K smallest items."""
    lst = values.copy()
    return heapq.nsmallest(K, lst)

def bench_quickselect(values):
    """
    Use selectlib.quickselect to partition the list so that the item
    at index 99 is in its correct sorted position, then return the first K elements.
    Note: quickselect does not guarantee that the first K items are in sorted order,
    only that the kth position is correctly placed and all items before it are <= and items
    after are >=.
    """
    lst = values.copy()
    # Use quickselect to partition so that index 99 is in its correct sorted position.
    selectlib.quickselect(lst, K - 1)
    return lst[:K]

# ----------------------------
# Benchmark driver code
# ----------------------------
def run_benchmarks():
    # Generate a random list of integers.
    # Change 'n' to adjust the size of the list for benchmarking.
    n = N
    original = [random.randint(0, 1000000) for _ in range(n)]

    # Prepare the functions as lambdas capturing the original list.
    tests = {
        "sort": lambda: bench_sort(original),
        "heapq.nsmallest": lambda: bench_heapq(original),
        "quickselect": lambda: bench_quickselect(original),
    }

    median_times = {}

    print("Running benchmarks (each method is executed 5 times, taking the median)...\n")
    for name, func in tests.items():
        # Run the benchmark 5 times, each call executing the function once.
        times = timeit.repeat(stmt=func, repeat=5, number=1)
        med = statistics.median(times)
        median_times[name] = med
        print(f"{name:15}: median time = {med*1000:.3f} ms (runs: {[f'{t*1000:.3f}' for t in times]} ms)")

    return median_times

# ----------------------------
# Plotting the results
# ----------------------------
def plot_results(median_times):
    # Apply the fivethirtyeight style to the plot.
    plt.style.use('fivethirtyeight')

    methods = list(median_times.keys())
    times = [median_times[m] * 1000 for m in methods]  # Convert seconds to milliseconds for display

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(methods, times, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

    ax.set_ylabel('Median execution time (ms)')
    ax.set_title('Benchmark: K Smallest Elements Retrieval')
    ax.bar_label(bars, fmt='%.2f', padding=3)
    plt.tight_layout()
    plt.show()

# ----------------------------
# Main block
# ----------------------------
if __name__ == '__main__':
    medians = run_benchmarks()
    plot_results(medians)
