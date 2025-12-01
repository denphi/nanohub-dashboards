Contributing
============

We welcome contributions to nanohub-dashboards!

Development Setup
-----------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/denphi/nanohub-dashboards.git
      cd nanohub-dashboards

2. Install in development mode with test dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

Running Tests
-------------

We use ``pytest`` for testing. Run the full test suite:

.. code-block:: bash

   pytest

Run with coverage report:

.. code-block:: bash

   pytest --cov=nanohubdashboard --cov-report=html

Building Documentation
----------------------

To build the documentation locally:

.. code-block:: bash

   cd docs
   make html

The built documentation will be in ``docs/build/html/index.html``.

Code Style
----------

* Follow PEP 8 guidelines
* Add docstrings to all public classes and methods
* Add type hints to function signatures

Pull Requests
-------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a Pull Request
