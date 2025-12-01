# Testing Guide for nanohub-dashboards

This directory contains the test suite for the nanohub-dashboards library.

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[test]"
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=nanohubdashboard --cov-report=html
```

Then open `htmlcov/index.html` to view the coverage report.

### Run Specific Test Files

```bash
pytest tests/test_plot.py
pytest tests/test_graph.py
pytest tests/test_dashboard.py
```

### Run Specific Test Classes or Methods

```bash
pytest tests/test_plot.py::TestPlot::test_plot_initialization
pytest tests/test_graph.py::TestGraph
```

### Skip Integration Tests

Integration tests require live API credentials and are marked with `@pytest.mark.integration`. To skip them:

```bash
pytest -m "not integration"
```

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_plot.py             # Tests for Plot class
├── test_graph.py            # Tests for Graph class
├── test_dashboard.py        # Tests for Dashboard class
├── test_client.py           # Tests for DashboardClient class
├── test_config.py           # Tests for DashboardConfig class
├── test_utils.py            # Tests for utility functions
└── README.md                # This file
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_session`: Mock nanohub-remote Session object
- `sample_plot_config`: Sample plot configuration dictionary
- `sample_bar_plot_config`: Sample bar plot configuration
- `sample_graph_config`: Sample graph configuration
- `sample_dashboard_config`: Sample dashboard configuration
- `mock_api_response`: Mock API response object
- `mock_requests`: Mocked requests library

## Writing Tests

### Example Test

```python
def test_plot_initialization(sample_plot_config):
    """Test Plot initialization with configuration."""
    plot = Plot(sample_plot_config, index=0)
    
    assert plot.index == 0
    assert plot.type == "scatter"
    assert plot.mode == "markers"
```

### Using Fixtures

```python
def test_with_mock_session(mock_session):
    """Test using the mock session fixture."""
    dashboard = Dashboard(mock_session)
    assert dashboard.session is mock_session
```

### Mocking API Calls

```python
from unittest.mock import patch

@patch('nanohubdashboard.client.DashboardClient._make_request')
def test_api_call(mock_request, mock_session):
    """Test with mocked API request."""
    mock_request.return_value = {"id": 1, "title": "Test"}
    
    client = DashboardClient(session=mock_session)
    result = client.get_dashboard(1)
    
    assert result.title == "Test"
```

## Test Markers

Tests can be marked with custom markers:

- `@pytest.mark.integration`: Integration tests (skipped by default)
- `@pytest.mark.slow`: Slow tests

## Coverage Goals

We aim for >80% code coverage across all modules:

- `plot.py`: 100% (simple class)
- `graph.py`: 100% (simple class)
- `dashboard.py`: >85%
- `client.py`: >80%
- `config.py`: >90%
- `utils.py`: >90%

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Release tags

## Troubleshooting

### Import Errors

If you get import errors, make sure you've installed the package in development mode:

```bash
pip install -e .
```

### Missing Dependencies

Install test dependencies:

```bash
pip install -e ".[test]"
```

### Coverage Not Working

Make sure pytest-cov is installed:

```bash
pip install pytest-cov
```

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if adding new test categories
