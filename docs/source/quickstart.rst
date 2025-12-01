Quick Start
===========

This guide will help you get started with nanohub-dashboards quickly.

Prerequisites
-------------

Before you begin, make sure you have:

1. A nanoHUB account
2. A personal access token (Settings -> Developer -> Personal Access Tokens)
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
   session = nr.Session(auth_data, url="https://nanohub.org/api")

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

Next Steps
----------

* Check out the :doc:`user_guide` for more detailed instructions
* See the :doc:`api` for full class documentation
* Explore :doc:`examples` for more complex use cases
