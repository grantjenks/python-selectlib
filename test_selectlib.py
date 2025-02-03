#!/usr/bin/env python
"""
Tests for both quickselect and heapselect implementations,
as well as the version attribute.
"""

import unittest
import random
import selectlib


class TestSelectLib(unittest.TestCase):

    def setUp(self):
        # Define the algorithms to test as tuples: (name, function)
        self.algorithms = [
            ("quickselect", selectlib.quickselect),
            ("heapselect", selectlib.heapselect),
        ]

    def sorted_index_check(self, func, values, k, key=None):
        """
        Helper function:
        - Compute the expected order using sorted() (with optional key).
        - Run the given selection function to partition the list in place.
        - Verify that the element at index k equals the kth smallest,
          and that all elements before are <= and all elements after are >=.
        """
        expected = sorted(values, key=key) if key else sorted(values)
        if key:
            func(values, k, key=key)
        else:
            func(values, k)
        self.assertEqual(values[k], expected[k])
        kth_value = values[k]
        for item in values[:k]:
            if key:
                self.assertLessEqual(key(item), key(kth_value))
            else:
                self.assertLessEqual(item, kth_value)
        for item in values[k + 1:]:
            if key:
                self.assertGreaterEqual(key(item), key(kth_value))
            else:
                self.assertGreaterEqual(item, kth_value)

    def test_ordered_list(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                values = list(range(10))
                k = 5
                func(values, k)
                # Since the list is already ordered, the kth element should be k.
                self.assertEqual(values[k], 5)
                for item in values[:k]:
                    self.assertLessEqual(item, values[k])
                for item in values[k + 1:]:
                    self.assertGreaterEqual(item, values[k])

    def test_reversed_list(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                values = list(range(10, 0, -1))
                k = 3
                self.sorted_index_check(func, values, k)

    def test_random_list(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                values = [random.randint(0, 100) for _ in range(20)]
                k = random.randint(0, len(values) - 1)
                self.sorted_index_check(func, values, k)

    def test_with_duplicates(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                values = [5, 1, 3, 5, 2, 5, 4, 1, 3]
                k = 4
                self.sorted_index_check(func, values, k)

    def test_with_key_function(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                # In this test we use a key that negates the value,
                # effectively making the selection work for the kth largest element.
                values = [random.randint(0, 100) for _ in range(15)]
                k = 7
                expected = sorted(values, key=lambda x: -x)
                # Apply selection with the key; this partitions based on -x.
                func(values, k, key=lambda x: -x)
                self.assertEqual(values[k], expected[k])
                kth_value = values[k]
                for item in values[:k]:
                    self.assertLessEqual(-item, -kth_value)
                for item in values[k + 1:]:
                    self.assertGreaterEqual(-item, -kth_value)

    def test_non_list_input(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                with self.assertRaises(TypeError):
                    func("not a list", 0)

    def test_out_of_range_index(self):
        for name, func in self.algorithms:
            with self.subTest(algorithm=name):
                values = [3, 1, 2]
                with self.assertRaises(IndexError):
                    func(values, 5)

    def test_version_attribute(self):
        # Test that the module has a non-empty __version__ attribute.
        self.assertTrue(hasattr(selectlib, "__version__"))
        self.assertIsInstance(selectlib.__version__, str)
        self.assertNotEqual(selectlib.__version__, "")


if __name__ == '__main__':
    unittest.main()
