nanohub-dashboards Documentation
==================================

Welcome to the **nanohub-dashboards** documentation! This Python library provides a powerful client for interacting with the nanoHUB Dashboard API, allowing you to programmatically load, manipulate, visualize, and save dashboards.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide
   api
   examples
   contributing

Features
--------

* **Load dashboards** from nanoHUB with full configuration
* **Manipulate plots** - change types, properties, and styling
* **Add new visualizations** - create custom graphs and plots
* **Preview locally** - test changes before saving
* **Save changes** - update dashboards on the server
* **Export to HTML** - generate standalone visualization files
* **Full Plotly support** - leverage Plotly's powerful visualization capabilities

Quick Example
-------------

.. code-block:: python

   import nanohubremote as nr
   from nanohubdashboard import Dashboard

   # Authenticate
   auth_data = {
       "grant_type": "personal_token",
       "token": "your_token_here"
   }
   session = nr.Session(auth_data, url="https://nanohub.org/api")

   # Load and manipulate dashboard
   dashboard = Dashboard(session)
   dashboard.load(dashboard_id=8)
   dashboard.swap_all_bar_scatter()

   # Visualize
   dashboard.visualize(output_file="my_dashboard.html", open_browser=True)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
