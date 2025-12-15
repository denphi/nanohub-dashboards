Quick Start
===========

This guide will help you get started with nanohub-dashboards quickly.

Prerequisites
-------------

Before you begin, make sure you have:

1. A nanoHUB account
2. A personal access token

   * Visit https://nanohub.org/developer/api/docs
   * Navigate to **Settings → Developer → Personal Access Tokens**
   * Generate a new personal access token

3. Installed the library: ``pip install nanohub-dashboards``

Basic Workflow
--------------

The typical workflow involves loading a dashboard, modifying it, and visualizing or saving the changes.

1. Authentication
~~~~~~~~~~~~~~~~~

First, create an authenticated session:

.. code-block:: python

   import nanohubremote as nr
   from nanohubdashboard import Dashboard

   auth_data = {
       "grant_type": "personal_token",
       "token": "YOUR_TOKEN_HERE"
   }

   # Production environment
   session = nr.Session(auth_data, url="https://nanohub.org/api")

   # Or use development environment for testing
   # This is useful for experimenting without affecting production data
   # session = nr.Session(auth_data, url="https://dev.nanohub.org/api")

2. Load a Dashboard
~~~~~~~~~~~~~~~~~~~

Load an existing dashboard by its ID:

.. code-block:: python

   dashboard = Dashboard(session)
   dashboard.load(dashboard_id=123)  # Replace with your dashboard ID

   # Print summary of graphs
   dashboard.print_graphs()

3. Modify Plots
~~~~~~~~~~~~~~~

You can modify plot properties programmatically:

.. code-block:: python

   # Swap all bar charts to scatter plots
   dashboard.swap_all_bar_scatter()

   # Or modify specific graphs
   graph = dashboard.get_graph(0)
   if graph.plots:
       plot = graph.plots[0]
       plot.type = 'scatter'
       plot.mode = 'lines+markers'
       plot.set('marker', {'size': 10, 'color': 'red'})

4. Visualize Locally
~~~~~~~~~~~~~~~~~~~~

Preview your changes locally without saving to the server:

.. code-block:: python

   # Generate HTML and open in browser
   dashboard.visualize(open_browser=True)

5. Save Changes
~~~~~~~~~~~~~~~

Once you're happy with the changes, save them back to nanoHUB:

.. code-block:: python

   dashboard.save()

Single Plot Rendering (No API Required)
----------------------------------------

**NEW:** You can create and render standalone plots without connecting to the API.

Simple Plot
~~~~~~~~~~~

Create a basic plot with direct data:

.. code-block:: python

   from nanohubdashboard.plot import Plot

   plot = Plot({
       'type': 'scatter',
       'mode': 'markers',
       'x': [1, 2, 3, 4, 5],
       'y': [2, 4, 6, 8, 10],
       'name': 'My Data'
   }, index=0)

   # Render to HTML (opens in browser automatically)
   plot.visualize(output_file='my_plot.html')

Using Placeholders
~~~~~~~~~~~~~~~~~~

Create reusable plot templates with dynamic data injection:

.. code-block:: python

   from nanohubdashboard.plot import Plot

   # Define template with placeholders
   plot = Plot({
       'type': 'scatter',
       'mode': 'lines+markers',
       'x': '%TIME',          # Placeholder
       'y': '%TEMPERATURE',   # Placeholder
       'name': '%SENSOR_ID'   # Placeholder
   }, index=0)

   # Inject data at render time
   data = {
       'time': [0, 1, 2, 3, 4],
       'temperature': [20, 22, 21, 23, 25],
       'sensor_id': 'Sensor A'
   }

   plot.visualize(data=data, output_file='temperature.html')

Multiple Series
~~~~~~~~~~~~~~~

Combine multiple plots in a single graph:

.. code-block:: python

   from nanohubdashboard.graph import Graph

   graph = Graph(index=0)

   # Add multiple series
   graph.add_plot({
       'type': 'scatter',
       'x': [1, 2, 3, 4, 5],
       'y': [1, 4, 9, 16, 25],
       'name': 'Series 1',
       'line': {'color': 'blue'}
   })

   graph.add_plot({
       'type': 'scatter',
       'x': [1, 2, 3, 4, 5],
       'y': [1, 2, 3, 4, 5],
       'name': 'Series 2',
       'line': {'color': 'red', 'dash': 'dash'}
   })

   # Customize layout
   graph.set_layout('title', 'Comparison')
   graph.set_layout('xaxis', {'title': 'X Axis'})
   graph.set_layout('yaxis', {'title': 'Y Axis'})

   # Render
   graph.visualize(output_file='comparison.html')

Next Steps
----------

* Check out the :doc:`user_guide` for more detailed instructions
* See the :doc:`api` for full class documentation
* Explore :doc:`examples` for more complex use cases
