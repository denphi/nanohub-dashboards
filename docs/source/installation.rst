Installation
============

Requirements
------------

* Python >= 3.6
* requests
* plotly
* pandas
* nanohub-remote

Installing from PyPI
--------------------

The easiest way to install nanohub-dashboards is using pip:

.. code-block:: bash

   pip install nanohub-dashboards

.. note::
   The package is published as ``nanohub-dashboards`` on PyPI but imported as ``nanohubdashboard`` (no hyphen).

Installing from Source
----------------------

To install from source for development:

.. code-block:: bash

   git clone https://github.com/denphi/nanohub-dashboards.git
   cd nanohub-dashboards
   pip install -e .

Development Installation
------------------------

To install with development dependencies (tests and documentation):

.. code-block:: bash

   pip install -e ".[dev]"

Or install specific dependency groups:

.. code-block:: bash

   # For testing only
   pip install -e ".[test]"

   # For documentation only
   pip install -e ".[docs]"

Verifying Installation
----------------------

To verify the installation, try importing the package:

.. code-block:: python

   import nanohubdashboard
   from nanohubdashboard import Dashboard, Graph, Plot

   print(nanohubdashboard.__name__)

Troubleshooting
---------------

Import Error: No module named 'nanohubremote'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you get an import error for ``nanohubremote``, install the nanohub-remote package:

.. code-block:: bash

   pip install nanohub-remote

Import Error: No module named 'plotly'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the required visualization library:

.. code-block:: bash

   pip install plotly

Python Version Issues
~~~~~~~~~~~~~~~~~~~~~

Make sure you're using Python 3.6 or higher:

.. code-block:: bash

   python --version

If you have multiple Python versions, you may need to use ``pip3`` instead of ``pip``.
