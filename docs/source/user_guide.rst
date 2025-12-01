User Guide
==========

This guide provides comprehensive instructions for using the nanohub-dashboards library.

Authentication
--------------

The library uses ``nanohub-remote`` for authentication. You can authenticate using a personal access token or other supported methods.

.. code-block:: python

   import nanohubremote as nr
   
   # Using Personal Access Token
   auth_data = {
       "grant_type": "personal_token",
       "token": "your_token_here"
   }
   session = nr.Session(auth_data, url="https://nanohub.org/api")

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
