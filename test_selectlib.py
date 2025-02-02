#!/usr/bin/env python
import unittest
import random

# Import the compiled selectlib module.
import selectlib

class TestQuickselect(unittest.TestCase):

    def sorted_index_check(self, values, k):
        """
        Helper function: Given a list and a target index k,
        use quickselect to partition the list in place, then verify
        that the element at index k equals the kth smallest element.
        """
        # Create a copy of the original list to compute the sorted target.
        expected = sorted(values)
        # Call quickselect: this mutates the list in-place.
        selectlib.quickselect(values, k)
        # Check that the element at index k is what we expect.
        self.assertEqual(values[k], expected[k])

        # Additionally, verify that all elements before index k are less than or equal
        # to the kth element, and all elements after index k are greater than or equal.
        kth_value = values[k]
        for item in values[:k]:
            self.assertLessEqual(item, kth_value)
        for item in values[k+1:]:
            self.assertGreaterEqual(item, kth_value)

    def test_ordered_list(self):
        # Test on a sorted list.
        values = list(range(10))
        k = 5
        selectlib.quickselect(values, k)
        self.assertEqual(values[k], 5)
        # Check partition condition.
        for item in values[:k]:
            self.assertLessEqual(item, values[k])
        for item in values[k+1:]:
            self.assertGreaterEqual(item, values[k])

    def test_reversed_list(self):
        # Test on a reverse-sorted list.
        values = list(range(10, 0, -1))
        k = 3
        self.sorted_index_check(values, k)

    def test_random_list(self):
        # Test on a list of random integers.
        values = [random.randint(0, 100) for _ in range(20)]
        k = random.randint(0, len(values) - 1)
        self.sorted_index_check(values, k)

    def test_with_duplicates(self):
        # Test on a list with duplicate values.
        values = [5, 1, 3, 5, 2, 5, 4, 1, 3]
        k = 4
        self.sorted_index_check(values, k)

    def test_with_key_function(self):
        # Test the 'key' argument.
        # In this example, we use a simple key that returns the negative of the value,
        # effectively partitioning to find the kth largest element.
        values = [random.randint(0, 100) for _ in range(15)]
        k = 7  # kth largest element if we sort descending
        # Make a copy for expected result.
        expected = sorted(values, key=lambda x: -x)
        # When using a key, quickselect should partition based on the key.
        selectlib.quickselect(values, k, key=lambda x: -x)
        self.assertEqual(values[k], expected[k])
        kth_value = values[k]
        # Check that all prior items have keys less than or equal to the kth item.
        for item in values[:k]:
            self.assertLessEqual(-item, -kth_value)
        for item in values[k+1:]:
            self.assertGreaterEqual(-item, -kth_value)

    def test_non_list_input(self):
        # Test that providing a non-list as values raises a TypeError.
        with self.assertRaises(TypeError):
            selectlib.quickselect("not a list", 0)

    def test_out_of_range_index(self):
        # Test that an out-of-range index raises an IndexError.
        values = [3, 1, 2]
        with self.assertRaises(IndexError):
            selectlib.quickselect(values, 5)

if __name__ == '__main__':
    unittest.main()
