"""
Unit tests for the report generation module.
"""
import json
import pytest
from unittest.mock import MagicMock

from nanohubdashboard.report import ReportGenerator, _numeric, _fmt
from nanohubdashboard.config import DashboardConfig


@pytest.fixture
def client():
    client = MagicMock()
    client.base_url = "https://nanohub.org"
    return client


@pytest.fixture
def generator(client):
    return ReportGenerator(client)


@pytest.fixture
def sample_plots():
    return {
        "_plot_0": {
            "plot": json.dumps([
                {"type": "bar", "name": "Users",
                 "x": ["a", "b", "c"], "y": [1, 2, 3]}
            ]),
            "layout": json.dumps({"title": {"text": "Usage"}}),
            "zone": "main",
        },
        "_plot_1": {
            "plot": json.dumps([
                {"type": "pie", "labels": ["x", "y"], "values": [10, 20]}
            ]),
            "layout": json.dumps({"title": "Distribution"}),
            "zone": "main",
        },
        "_html_2": {"html": "<p>hello</p>", "zone": "main"},
    }


@pytest.fixture
def config():
    return DashboardConfig(title="Test Dash", description="A test", id=42)


class TestHelpers:
    def test_numeric_filters_non_numbers(self):
        assert _numeric([1, "2", None, "x", 3.5, True]) == [1.0, 2.0, 3.5]

    def test_fmt(self):
        assert _fmt(1234.0) == "1,234"
        assert _fmt(12.345) == "12.35"


class TestFigureExtraction:
    def test_figures_normalizes_plots(self, generator, sample_plots):
        figures = generator._figures(sample_plots)
        assert len(figures) == 3
        plotted = [f for f in figures if "traces" in f]
        assert len(plotted) == 2

    def test_figure_title_variants(self, generator):
        assert generator._figure_title({"title": {"text": "T"}}, 0) == "T"
        assert generator._figure_title({"title": "S"}, 0) == "S"
        assert generator._figure_title({}, 2) == "Figure 3"

    def test_trace_table_xy(self, generator):
        headers, rows = generator._trace_table(
            {"x": [1, 2], "y": [3, 4], "name": "N"})
        assert headers == ["X", "N"]
        assert rows == [[1, 3], [2, 4]]

    def test_trace_table_labels_values(self, generator):
        headers, rows = generator._trace_table(
            {"labels": ["a"], "values": [5]})
        assert headers == ["Category", "Value"]
        assert rows == [["a", 5]]

    def test_trace_table_indicator(self, generator):
        headers, rows = generator._trace_table(
            {"type": "indicator", "value": 7, "title": {"text": "Total"}})
        assert rows == [["Total", 7]]

    def test_trace_table_untabular(self, generator):
        assert generator._trace_table({"type": "sankey"}) is None

    def test_trace_stats(self, generator):
        stats = generator._trace_stats(
            {"name": "Users", "y": [1, 2, 3], "type": "bar"})
        assert "Users" in stats
        assert "min 1" in stats
        assert "max 3" in stats
        assert "total 6" in stats


class TestRendering:
    def test_html_report(self, generator, config, sample_plots):
        html = generator._render_html(config, sample_plots, True, 50)
        assert "Test Dash" in html
        assert "Usage" in html
        assert "Distribution" in html
        assert "<p>hello</p>" in html
        assert "Plotly.newPlot" in html
        assert "dashboards/42" in html

    def test_html_report_escapes_titles(self, generator, sample_plots):
        cfg = DashboardConfig(title="<script>x</script>")
        html = generator._render_html(cfg, sample_plots, True, 50)
        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html

    def test_markdown_report(self, generator, config, sample_plots):
        md = generator._render_markdown(config, sample_plots, True, 50)
        assert md.startswith("# Test Dash")
        assert "## Usage" in md
        assert "| Category | Value |" in md

    def test_markdown_table_truncation(self, generator, config):
        plots = {
            "_plot_0": {
                "plot": json.dumps([
                    {"type": "bar", "x": list(range(100)),
                     "y": list(range(100))}
                ]),
                "layout": "{}",
                "zone": "main",
            }
        }
        md = generator._render_markdown(config, plots, True, 10)
        assert "Showing first 10 rows" in md

    def test_generate_rejects_bad_format(self, generator):
        with pytest.raises(ValueError):
            generator.generate(1, format="pdf")


class TestCollect:
    def test_collect_empty_datasource(self, generator, client):
        client.get_dashboard.return_value = DashboardConfig(
            title="NoDS", datasource_id=None)
        response = MagicMock()
        response.json.return_value = {"dashboard": {"graphs": "[]"}}
        client.session.requestGet.return_value = response

        cfg, plots = generator.collect(1)
        assert cfg.title == "NoDS"
        assert plots == {}
