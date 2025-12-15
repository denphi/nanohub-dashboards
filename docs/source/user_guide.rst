User Guide
==========

This guide provides comprehensive instructions for using the nanohub-dashboards library.

Authentication
--------------

The library uses ``nanohub-remote`` for authentication. You can authenticate using a personal access token or other supported methods.

Getting Your API Token
~~~~~~~~~~~~~~~~~~~~~~

1. Visit https://nanohub.org/developer/api/docs
2. Navigate to **Settings → Developer → Personal Access Tokens**
3. Generate a new personal access token
4. Copy the token for use in your code

Using the Token
~~~~~~~~~~~~~~~

.. code-block:: python

   import nanohubremote as nr

   # Using Personal Access Token
   auth_data = {
       "grant_type": "personal_token",
       "token": "your_token_here"
   }

   # Production environment
   session = nr.Session(auth_data, url="https://nanohub.org/api")

   # Development environment (for testing)
   # Use this to safely experiment without affecting production data
   # session = nr.Session(auth_data, url="https://dev.nanohub.org/api")

.. note::
   When testing or developing features, you can use the development environment
   (``url="https://dev.nanohub.org/api"``) to safely experiment without affecting
   production dashboards.

Working with Dashboards
-----------------------

The ``Dashboard`` class is the main entry point.

Loading Dashboards
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nanohubdashboard import Dashboard
   
   dashboard = Dashboard(session)
   dashboard.load(123)  # Load dashboard with ID 123

Listing Graphs
~~~~~~~~~~~~~~

You can inspect the graphs in a loaded dashboard:

.. code-block:: python

   # Print a summary
   dashboard.print_graphs()
   
   # Get list of summaries
   summaries = dashboard.list_graphs()

Manipulating Graphs and Plots
-----------------------------

Dashboards contain ``Graph`` objects, which contain ``Plot`` objects.

Accessing Graphs
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get graph by index
   graph = dashboard.get_graph(0)
   
   # Access properties
   print(f"Zone: {graph.zone}")
   print(f"Query: {graph.query}")

Accessing Plots
~~~~~~~~~~~~~~~

.. code-block:: python

   # Get first plot in graph
   plot = graph.plot
   
   # Or iterate through all plots
   for p in graph.plots:
       print(p.type)

Modifying Plot Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plots use Plotly configuration structure. You can modify any property:

.. code-block:: python

   # Change type
   plot.type = 'bar'
   
   # Change mode (for scatter)
   plot.mode = 'markers'
   
   # Set nested properties
   plot.set('marker', {'color': 'blue', 'size': 15})
   plot.set('line', {'width': 3, 'dash': 'dot'})
   
   # Method chaining is supported
   plot.set('opacity', 0.8).set('name', 'My Series')

Adding New Graphs
-----------------

You can add new graphs to a dashboard:

.. code-block:: python

   from nanohubdashboard import Graph, Plot
   
   # Create a plot
   plot_config = {
       'type': 'scatter',
       'x': '%X_DATA',  # Use placeholders for data
       'y': '%Y_DATA',
       'name': 'New Series'
   }
   plot = Plot(plot_config, index=0)
   
   # Create a graph
   graph = Graph(
       query='my_query',
       zone='main',
       priority=10
   )
   graph.plots = [plot]
   
   # Add to dashboard
   dashboard.add_graph(graph)

Visualization
-------------

You can visualize the dashboard locally to see your changes.

.. code-block:: python

   # Generate HTML file
   html_path = dashboard.visualize(output_file="dashboard.html")
   
   # Generate and open in browser
   dashboard.visualize(open_browser=True)

This generates a standalone HTML file with all the data and interactivity.

Previewing
----------

The ``preview()`` method asks the server to render the dashboard as it would appear on the site. This is useful for testing server-side rendering.

.. code-block:: python

   dashboard.preview(open_browser=True)

Saving Changes
--------------

To persist your changes to nanoHUB:

.. code-block:: python

   dashboard.save()

This updates the dashboard configuration on the server.

Standalone Plot Rendering
--------------------------

**NEW:** You can create and render individual plots and graphs without connecting to the nanoHUB API. This is useful for quick visualizations, testing plot configurations, or creating custom visualizations with your own data.

Simple Plots
~~~~~~~~~~~~

Create a basic plot with direct data:

.. code-block:: python

   from nanohubdashboard.plot import Plot

   plot = Plot({
       'type': 'scatter',
       'mode': 'markers',
       'x': [1, 2, 3, 4, 5],
       'y': [2, 4, 6, 8, 10],
       'name': 'Linear Data',
       'marker': {'color': 'blue', 'size': 10}
   }, index=0)

   # Render to HTML file
   plot.visualize(output_file='my_plot.html')

Placeholder-Based Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create reusable plot templates with placeholders that can be filled with data at render time:

.. code-block:: python

   from nanohubdashboard.plot import Plot

   # Define template with placeholders (% prefix)
   plot_template = Plot({
       'type': 'scatter',
       'mode': 'lines+markers',
       'x': '%TIME',          # Placeholder
       'y': '%TEMPERATURE',   # Placeholder
       'name': '%SENSOR_ID'   # Placeholder
   }, index=0)

   # Inject data at render time (case-insensitive)
   data = {
       'time': [0, 1, 2, 3, 4, 5],
       'temperature': [20, 22, 21, 23, 25, 24],
       'sensor_id': 'Sensor A'
   }

   plot_template.visualize(data=data, output_file='temperature.html')

The placeholder system is case-insensitive - ``%TIME``, ``%time``, and ``%Time`` will all match the ``'time'`` key in your data dictionary.

Multiple Series Graphs
~~~~~~~~~~~~~~~~~~~~~~~

Combine multiple plot series in a single graph:

.. code-block:: python

   from nanohubdashboard.graph import Graph

   # Create a graph
   graph = Graph(index=0)

   # Add first series
   graph.add_plot({
       'type': 'scatter',
       'mode': 'lines',
       'x': [1, 2, 3, 4, 5],
       'y': [1, 4, 9, 16, 25],
       'name': 'y = x²',
       'line': {'color': 'blue', 'width': 2}
   })

   # Add second series
   graph.add_plot({
       'type': 'scatter',
       'mode': 'lines',
       'x': [1, 2, 3, 4, 5],
       'y': [1, 2, 3, 4, 5],
       'name': 'y = x',
       'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
   })

   # Customize layout
   graph.set_layout('title', 'Polynomial Functions')
   graph.set_layout('xaxis', {'title': 'x'})
   graph.set_layout('yaxis', {'title': 'y'})

   # Render
   graph.visualize(output_file='comparison.html')

Custom Layouts
~~~~~~~~~~~~~~

Override the default layout configuration:

.. code-block:: python

   custom_layout = {
       'title': 'Sales Report',
       'xaxis': {
           'title': 'Product',
           'showgrid': True
       },
       'yaxis': {
           'title': 'Revenue ($1000)',
           'range': [0, 30]
       },
       'showlegend': True,
       'template': 'plotly_white'
   }

   plot.visualize(layout=custom_layout, output_file='sales.html')

Jupyter Integration
~~~~~~~~~~~~~~~~~~~~

When running in Jupyter Notebook or JupyterLab, plots are automatically displayed inline:

.. code-block:: python

   # In Jupyter Notebook - displays inline using IFrame
   plot.visualize()

   # In JupyterLab - opens in new browser tab
   plot.visualize()

   # Disable automatic opening/display
   plot.visualize(open_browser=False)

Supported Plot Types
~~~~~~~~~~~~~~~~~~~~~

All Plotly plot types are supported, including:

* ``scatter`` - Scatter plots (2D and 3D)
* ``bar`` - Bar charts
* ``line`` - Line charts
* ``pie`` - Pie charts
* ``scatter3d`` - 3D scatter plots
* ``surface`` - 3D surface plots
* ``heatmap`` - Heatmaps
* ``box`` - Box plots
* ``violin`` - Violin plots
* ``histogram`` - Histograms
* And many more!

See the `Plotly documentation <https://plotly.com/python/>`_ for complete configuration options.

API Reference
~~~~~~~~~~~~~

**Plot.visualize()**

.. code-block:: python

   plot.visualize(
       data=None,           # Dict mapping placeholder names to data arrays
       layout=None,         # Custom layout configuration (dict)
       output_file=None,    # Output HTML file path (default: 'plot_{index}.html')
       open_browser=True    # Whether to open in browser/Jupyter
   )

Returns the absolute path to the generated HTML file.

**Graph.visualize()**

.. code-block:: python

   graph.visualize(
       data=None,           # Dict mapping placeholder names to data arrays
       layout=None,         # Custom layout (default: uses graph.layout_config)
       output_file=None,    # Output HTML file path (default: 'graph_{index}.html')
       open_browser=True    # Whether to open in browser/Jupyter
   )

Returns the absolute path to the generated HTML file.
