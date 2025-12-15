Examples
========

The library comes with several examples in the ``examples/`` directory.

Basic API Usage
---------------

.. literalinclude:: ../../examples/demo_simple_api.py
   :language: python
   :caption: examples/demo_simple_api.py

Complete Workflow
-----------------

.. literalinclude:: ../../examples/demo_base.py
   :language: python
   :caption: examples/demo_base.py

Adding Plots
------------

.. literalinclude:: ../../examples/demo_add_plots.py
   :language: python
   :caption: examples/demo_add_plots.py

Standalone Plot Rendering
--------------------------

**NEW:** This example demonstrates how to create and render individual plots without connecting to the API.

.. literalinclude:: ../../examples/demo_single_plot_rendering.py
   :language: python
   :caption: examples/demo_single_plot_rendering.py
   :emphasize-lines: 1-20

This example includes:

* Simple scatter plot with hardcoded data
* Plot with placeholder data injection
* Bar chart with custom layout
* Multiple series in one graph
* Real-world temperature monitoring example
* 3D scatter plot

See also the Jupyter notebook version: ``examples/demo_single_plot_rendering.ipynb``
