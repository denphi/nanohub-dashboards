"""
Example: Rendering Single Plots Locally

This example demonstrates how to create and render individual plots and graphs
without needing to load a full dashboard from the API. This is useful for:
- Quick data visualization
- Creating standalone plots from custom data
- Testing plot configurations
- Building custom visualizations
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nanohubdashboard.plot import Plot
from nanohubdashboard.graph import Graph


def example1_simple_scatter():
    """Example 1: Create a simple scatter plot with hardcoded data."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Scatter Plot")
    print("="*70)

    # Create a plot configuration
    plot_config = {
        'type': 'scatter',
        'mode': 'markers',
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'name': 'Linear Data',
        'marker': {
            'color': 'blue',
            'size': 10
        }
    }

    # Create Plot object
    plot = Plot(plot_config, index=0)

    # Render to HTML
    output = plot.visualize(
        output_file='example1_scatter.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print("  Open this file in your browser to view the plot")


def example2_placeholder_data():
    """Example 2: Use placeholders to inject data at render time."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Plot with Placeholder Data")
    print("="*70)

    # Create plot config with placeholders
    plot_config = {
        'type': 'scatter',
        'mode': 'lines+markers',
        'x': '%X_VALUES',      # Placeholder
        'y': '%Y_VALUES',      # Placeholder
        'name': '%SERIES_NAME', # Placeholder
        'line': {
            'color': 'red',
            'width': 2
        },
        'marker': {
            'size': 8
        }
    }

    plot = Plot(plot_config, index=0)

    # Provide data at render time
    data = {
        'x_values': [0, 1, 2, 3, 4],
        'y_values': [0, 1, 4, 9, 16],
        'series_name': 'Quadratic Function'
    }

    output = plot.visualize(
        data=data,
        output_file='example2_placeholder.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print("  Placeholders replaced: %X_VALUES, %Y_VALUES, %SERIES_NAME")


def example3_bar_chart():
    """Example 3: Create a bar chart."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Bar Chart")
    print("="*70)

    plot_config = {
        'type': 'bar',
        'x': ['Product A', 'Product B', 'Product C', 'Product D'],
        'y': [20, 14, 23, 18],
        'name': 'Sales by Product',
        'marker': {
            'color': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        }
    }

    plot = Plot(plot_config, index=0)

    # Custom layout
    layout = {
        'title': 'Q4 Sales Report',
        'xaxis': {'title': 'Product'},
        'yaxis': {'title': 'Sales (thousands)'},
        'autosize': True
    }

    output = plot.visualize(
        layout=layout,
        output_file='example3_bar.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print("  Custom layout applied with title and axis labels")


def example4_multiple_series():
    """Example 4: Create a graph with multiple plot series."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Multiple Series in One Graph")
    print("="*70)

    # Create a Graph object
    graph = Graph(
        query='',
        plot_type='scatter',
        zone='main',
        index=0
    )

    # Add first plot series
    plot1_config = {
        'type': 'scatter',
        'mode': 'lines',
        'x': [1, 2, 3, 4, 5],
        'y': [1, 4, 9, 16, 25],
        'name': 'y = x²',
        'line': {'color': 'blue', 'width': 2}
    }
    graph.add_plot(plot1_config)

    # Add second plot series
    plot2_config = {
        'type': 'scatter',
        'mode': 'lines',
        'x': [1, 2, 3, 4, 5],
        'y': [1, 2, 3, 4, 5],
        'name': 'y = x',
        'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
    }
    graph.add_plot(plot2_config)

    # Add third plot series
    plot3_config = {
        'type': 'scatter',
        'mode': 'lines',
        'x': [1, 2, 3, 4, 5],
        'y': [1, 8, 27, 64, 125],
        'name': 'y = x³',
        'line': {'color': 'green', 'width': 2}
    }
    graph.add_plot(plot3_config)

    # Set custom layout
    graph.set_layout('title', 'Polynomial Functions Comparison')
    graph.set_layout('xaxis', {'title': 'x'})
    graph.set_layout('yaxis', {'title': 'y'})
    graph.set_layout('hovermode', 'x unified')

    output = graph.visualize(
        output_file='example4_multiple_series.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print(f"  Graph contains {len(graph.plots)} plot series")


def example5_real_world_temperature():
    """Example 5: Real-world example with temperature data."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Temperature Monitoring (Real-world Example)")
    print("="*70)

    # Create graph with placeholder-based configuration
    graph = Graph(index=0)

    # Sensor 1 configuration
    sensor1_config = {
        'type': 'scatter',
        'mode': 'lines+markers',
        'x': '%TIME',
        'y': '%SENSOR1_TEMP',
        'name': 'Sensor 1 (Room A)',
        'line': {'color': 'rgb(255, 127, 14)'},
        'marker': {'size': 6}
    }
    graph.add_plot(sensor1_config)

    # Sensor 2 configuration
    sensor2_config = {
        'type': 'scatter',
        'mode': 'lines+markers',
        'x': '%TIME',
        'y': '%SENSOR2_TEMP',
        'name': 'Sensor 2 (Room B)',
        'line': {'color': 'rgb(44, 160, 44)'},
        'marker': {'size': 6}
    }
    graph.add_plot(sensor2_config)

    # Simulated temperature data
    data = {
        'time': ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
        'sensor1_temp': [20.5, 21.2, 22.1, 23.5, 24.8, 24.2, 23.1],
        'sensor2_temp': [19.8, 20.5, 21.8, 22.9, 23.5, 23.8, 22.7]
    }

    # Custom layout for the temperature graph
    layout = {
        'title': 'Office Temperature Monitoring - Dec 15, 2025',
        'xaxis': {
            'title': 'Time',
            'showgrid': True
        },
        'yaxis': {
            'title': 'Temperature (°C)',
            'showgrid': True,
            'range': [18, 26]
        },
        'hovermode': 'x unified',
        'showlegend': True
    }

    output = graph.visualize(
        data=data,
        layout=layout,
        output_file='example5_temperature.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print("  Real-world scenario: Temperature monitoring with two sensors")


def example6_3d_scatter():
    """Example 6: 3D scatter plot."""
    print("\n" + "="*70)
    print("EXAMPLE 6: 3D Scatter Plot")
    print("="*70)

    import math

    # Generate spiral data
    t = [i * 0.1 for i in range(100)]
    x = [ti * math.cos(ti * 2) for ti in t]
    y = [ti * math.sin(ti * 2) for ti in t]
    z = t

    plot_config = {
        'type': 'scatter3d',
        'mode': 'markers+lines',
        'x': x,
        'y': y,
        'z': z,
        'marker': {
            'size': 4,
            'color': z,
            'colorscale': 'Viridis',
            'showscale': True
        },
        'line': {
            'color': 'darkblue',
            'width': 2
        }
    }

    plot = Plot(plot_config, index=0)

    layout = {
        'title': '3D Spiral',
        'scene': {
            'xaxis': {'title': 'X'},
            'yaxis': {'title': 'Y'},
            'zaxis': {'title': 'Z'}
        }
    }

    output = plot.visualize(
        layout=layout,
        output_file='example6_3d_spiral.html',
        open_browser=False
    )

    print(f"✓ Created: {output}")
    print("  Interactive 3D visualization")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("SINGLE PLOT RENDERING EXAMPLES")
    print("="*70)
    print("\nThis demo shows how to create standalone plots without")
    print("needing to load a dashboard from the API.")

    # Run all examples
    example1_simple_scatter()
    example2_placeholder_data()
    example3_bar_chart()
    example4_multiple_series()
    example5_real_world_temperature()
    example6_3d_scatter()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nGenerated files:")
    print("  1. example1_scatter.html           - Simple scatter plot")
    print("  2. example2_placeholder.html       - Plot with data injection")
    print("  3. example3_bar.html               - Bar chart with custom layout")
    print("  4. example4_multiple_series.html   - Multiple series in one graph")
    print("  5. example5_temperature.html       - Real-world temperature data")
    print("  6. example6_3d_spiral.html         - 3D visualization")
    print("\nOpen any of these files in your browser to view the interactive plots!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
