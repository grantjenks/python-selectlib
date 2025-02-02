selectlib
=========

selectlib is a lightweight C extension module for Python that implements the quickselect algorithm. Quickselect is an efficient selection algorithm to find the kth smallest element in an unsorted list without fully sorting the data. The module supports an optional key function, allowing for flexible comparisons and custom ordering.

Features
--------

• Fast in-place selection using a C implementation
• Optional key function for custom comparisons
• Compatibility with Python 3.8 and later
• Easily integratable into your Python projects

Installation
------------

The selectlib module can be installed via pip after building from source. First, ensure you have a C compiler and Python development headers installed for your platform.

1. Clone the repository:

   git clone https://github.com/grantjenks/python-selectlib.git
   cd python-selectlib

2. Build and install:

   python -m pip install -e .

Usage Example
-------------

Below is a simple example using quickselect to find the kth smallest element in a list:

   import selectlib

   data = [9, 3, 7, 1, 5, 8, 2]
   k = 3  # Find the element that would be at index 3 if sorted
   selectlib.quickselect(data, k)

   print("The kth smallest element is:", data[k])

Using a key function to find the kth largest element:

   data = [15, 8, 22, 5, 13]
   k = 2  # kth largest element when sorted in descending order
   selectlib.quickselect(data, k, key=lambda x: -x)

   print("The kth largest element is:", data[k])

Testing
-------

You can run the automated tests using tox. The tests validate both correct partitioning and error cases.

   tox

This will run tests on Python versions 3.8 through 3.13, as well as linting and formatting checks.

Development & Continuous Integration
--------------------------------------

This project uses GitHub Actions for CI/CD. The following workflows are available:

• release.yml – Builds wheels for multiple platforms and publishes packages to PyPI
• test.yml – Runs tests and linting on multiple Python versions

Contributing
------------

Contributions are welcome! If you find any bugs, have feature suggestions, or want to contribute improvements, feel free to open an issue or pull request on GitHub.

Building Documentation
----------------------

Documentation is provided within the source code and inline comments. For additional usage examples or API details, please refer to the source and test files.

License
-------

selectlib is licensed under the Apache License, Version 2.0. See the LICENSE file for details.
