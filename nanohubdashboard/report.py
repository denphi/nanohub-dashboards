"""
Report generation for nanoHUB dashboards.

Builds shareable reports from a dashboard: executes its queries, processes
its plot templates, and renders the result as a standalone HTML report,
a Markdown document, or CSV data exports.

Example:
    from nanohubdashboard import connect

    client = connect()
    client.generate_report(19, "report.html")            # interactive HTML
    client.generate_report(19, "report.md", format="markdown")

    # Or with the generator directly:
    from nanohubdashboard.report import ReportGenerator
    gen = ReportGenerator(client)
    gen.generate(19, "report.html")
    gen.export_csv(19, "data/")
"""

import csv
import html as html_module
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import DashboardConfig
from .datasource import DataSource
from .exceptions import APIError

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def _numeric(values: List[Any]) -> List[float]:
    """Return the numeric subset of a list of values."""
    result = []
    for v in values:
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            result.append(float(v))
        else:
            try:
                result.append(float(v))
            except (TypeError, ValueError):
                continue
    return result


def _fmt(value: float) -> str:
    """Format a number compactly for report text."""
    if value == int(value) and abs(value) < 1e15:
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _escape_html(text: Any) -> str:
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def _escape_md(text: Any) -> str:
    return str(text).replace('|', '\\|').replace('\n', ' ')


def _strip_html(text: Any) -> str:
    """Reduce an HTML fragment to readable plain text (labels, descriptions)."""
    text = str(text)
    text = re.sub(r'<(style|script)[^>]*>.*?</\1>', ' ', text,
                  flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<br\s*/?>', ' — ', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = html_module.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


class ReportGenerator:
    """
    Generates reports from nanoHUB dashboards.

    Args:
        client: An authenticated DashboardClient.
    """

    def __init__(self, client):
        self.client = client

    # ------------------------------------------------------------------ #
    # Data collection
    # ------------------------------------------------------------------ #

    def collect(self, dashboard_id: int) -> Tuple[DashboardConfig, Dict[str, Dict]]:
        """
        Fetch a dashboard, run its queries, and process its plot templates.

        Returns:
            Tuple of (DashboardConfig, plots) where plots maps plot ids to
            {'plot': <json str of traces>, 'layout': <json str>, 'zone': ...}
            or {'html': ..., 'zone': ...} entries.
        """
        dashboard_config = self.client.get_dashboard(dashboard_id)

        # Raw graphs are needed for plot templates with placeholders
        try:
            response = self.client.session.requestGet(
                f'dashboards/dashboard/read/{dashboard_id}')
            dashboard_data = response.json().get('dashboard', {})
            raw_graphs = json.loads(dashboard_data.get('graphs', '[]') or '[]')
        except Exception as e:
            raise APIError(f"Error fetching dashboard {dashboard_id}: {e}")

        if not dashboard_config.datasource_id:
            return dashboard_config, {}

        ds = DataSource(
            datasource_id=dashboard_config.datasource_id,
            session=self.client.session,
            base_url=self.client.base_url
        )

        query_results: Dict[str, Any] = {}
        for query in dashboard_config.queries:
            name = query.name if hasattr(query, 'name') else str(query)
            sql = query.sql if hasattr(query, 'sql') else str(query)
            try:
                query_results[name] = ds.query(sql, format="columns")
            except Exception as e:
                print(f"  ✗ Query '{name}' failed: {e}")
                query_results[name] = {}

        # Raw tables referenced as _tbl.<table>
        for graph in dashboard_config.graphs:
            if graph.query.startswith('_tbl.'):
                table_name = graph.query.replace('_tbl.', '')
                table_key = f"_TABLE_{table_name.upper()}"
                if table_name and table_key not in query_results:
                    try:
                        query_results[table_key] = ds.query(
                            f"SELECT * FROM `{table_name}`", format="columns")
                    except Exception as e:
                        print(f"  ✗ Table '{table_name}' failed: {e}")
                        query_results[table_key] = {}

        sorted_graphs = sorted(
            dashboard_config.graphs,
            key=lambda g: g.priority if hasattr(g, 'priority') else 0)

        plots, _ = self.client._process_graphs(
            sorted_graphs, raw_graphs, query_results, {'main': None}, None)

        return dashboard_config, plots

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def generate(self, dashboard_id: int, output_file: Optional[str] = None,
                 format: str = "html", include_tables: bool = True,
                 max_table_rows: int = 50) -> str:
        """
        Generate a report for a dashboard.

        Args:
            dashboard_id: Dashboard ID.
            output_file: Output path. Defaults to
                         dashboard_{id}_report.{html|md}.
            format: "html" (interactive figures + tables) or
                    "markdown" (summary statistics + tables).
            include_tables: Include per-figure data tables.
            max_table_rows: Maximum rows per data table.

        Returns:
            Path to the generated report file.
        """
        if format not in ("html", "markdown", "md"):
            raise ValueError("format must be 'html' or 'markdown'")

        dashboard_config, plots = self.collect(dashboard_id)

        if format == "html":
            content = self._render_html(dashboard_config, plots,
                                        include_tables, max_table_rows)
            default_name = f"dashboard_{dashboard_id}_report.html"
        else:
            content = self._render_markdown(dashboard_config, plots,
                                            include_tables, max_table_rows)
            default_name = f"dashboard_{dashboard_id}_report.md"

        output_file = output_file or default_name
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Report saved to {output_file}")
        return output_file

    def export_csv(self, dashboard_id: int, output_dir: str = ".") -> List[str]:
        """
        Export each dashboard query's results as a CSV file.

        Args:
            dashboard_id: Dashboard ID.
            output_dir: Directory to write CSV files into.

        Returns:
            List of written file paths.
        """
        dashboard_config = self.client.get_dashboard(dashboard_id)
        if not dashboard_config.datasource_id:
            return []

        ds = DataSource(
            datasource_id=dashboard_config.datasource_id,
            session=self.client.session,
            base_url=self.client.base_url
        )

        os.makedirs(output_dir, exist_ok=True)
        written = []
        for query in dashboard_config.queries:
            name = query.name if hasattr(query, 'name') else str(query)
            sql = query.sql if hasattr(query, 'sql') else str(query)
            try:
                results = ds.query(sql, format="columns")
            except Exception as e:
                print(f"  ✗ Query '{name}' failed: {e}")
                continue
            if not results:
                continue
            path = os.path.join(
                output_dir, f"dashboard_{dashboard_id}_{name.lower()}.csv")
            columns = list(results.keys())
            length = max((len(v) for v in results.values()
                          if isinstance(v, list)), default=0)
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for i in range(length):
                    writer.writerow([
                        results[c][i] if isinstance(results[c], list) and i < len(results[c])
                        else '' for c in columns])
            written.append(path)
            print(f"✓ Wrote {path} ({length} rows)")
        return written

    # ------------------------------------------------------------------ #
    # Figure summarization
    # ------------------------------------------------------------------ #

    @staticmethod
    def _figure_title(layout: Dict[str, Any], index: int) -> str:
        title = layout.get('title', '')
        if isinstance(title, dict):
            title = title.get('text', '')
        title = _strip_html(title) if title else ''
        return title if title else f"Figure {index + 1}"

    @staticmethod
    def _trace_table(trace: Dict[str, Any]) -> Optional[Tuple[List[str], List[List[Any]]]]:
        """Extract (headers, rows) from a Plotly trace, if tabular."""
        if isinstance(trace.get('labels'), list) and isinstance(trace.get('values'), list):
            rows = list(zip(trace['labels'], trace['values']))
            return ['Category', 'Value'], [list(r) for r in rows]
        if isinstance(trace.get('locations'), list) and isinstance(trace.get('z'), list):
            rows = list(zip(trace['locations'], trace['z']))
            return ['Location', 'Value'], [list(r) for r in rows]
        if isinstance(trace.get('x'), list) and isinstance(trace.get('y'), list):
            name = _strip_html(trace.get('name', 'Value') or 'Value')
            rows = list(zip(trace['x'], trace['y']))
            return ['X', str(name)], [list(r) for r in rows]
        if trace.get('value') is not None:
            label = trace.get('title', {})
            if isinstance(label, dict):
                label = label.get('text', 'Value')
            return ['Label', 'Value'], [[_strip_html(label), trace['value']]]
        return None

    @staticmethod
    def _trace_stats(trace: Dict[str, Any]) -> Optional[str]:
        """One-line summary statistics for a trace."""
        name = _strip_html(trace.get('name') or trace.get('type', 'series'))
        values = None
        if isinstance(trace.get('y'), list):
            values = _numeric(trace['y'])
        elif isinstance(trace.get('values'), list):
            values = _numeric(trace['values'])
        elif isinstance(trace.get('z'), list):
            flat = []
            for v in trace['z']:
                flat.extend(v if isinstance(v, list) else [v])
            values = _numeric(flat)
        elif trace.get('value') is not None:
            nums = _numeric([trace['value']])
            if nums:
                return f"{name}: value {_fmt(nums[0])}"
            return None

        if not values:
            return None
        return (f"{name}: {len(values)} points, "
                f"min {_fmt(min(values))}, max {_fmt(max(values))}, "
                f"mean {_fmt(sum(values) / len(values))}, "
                f"total {_fmt(sum(values))}")

    def _figures(self, plots: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Normalize the plots dict into an ordered list of figure entries."""
        figures = []
        for plot_id, entry in plots.items():
            if entry.get('html'):
                figures.append({'id': plot_id, 'html': entry['html']})
                continue
            try:
                traces = json.loads(entry.get('plot', '[]'))
                layout = json.loads(entry.get('layout', '{}'))
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(traces, list) or not traces:
                continue
            figures.append({
                'id': plot_id,
                'traces': traces,
                'layout': layout if isinstance(layout, dict) else {},
            })
        return figures

    # ------------------------------------------------------------------ #
    # HTML rendering
    # ------------------------------------------------------------------ #

    def _render_html(self, config: DashboardConfig, plots: Dict[str, Dict],
                     include_tables: bool, max_table_rows: int) -> str:
        generated = datetime.now().strftime('%Y-%m-%d %H:%M')
        figures = self._figures(plots)

        sections = []
        figure_scripts = []
        fig_index = 0
        for fig in figures:
            if 'html' in fig:
                sections.append(
                    f'<section class="nhr-section"><div class="nhr-html">{fig["html"]}</div></section>')
                continue

            title = self._figure_title(fig['layout'], fig_index)
            stats_lines = [s for s in (self._trace_stats(t) for t in fig['traces']) if s]
            stats_html = ''
            if stats_lines:
                items = ''.join(f'<li>{_escape_html(s)}</li>' for s in stats_lines)
                stats_html = f'<ul class="nhr-stats">{items}</ul>'

            table_html = ''
            if include_tables:
                table_html = self._tables_html(fig['traces'], max_table_rows)

            div_id = f'nhr-fig-{fig_index}'
            sections.append(f"""
    <section class="nhr-section">
        <h2>{_escape_html(title)}</h2>
        <div id="{div_id}" class="nhr-figure"></div>
        {stats_html}
        {table_html}
    </section>""")
            layout = dict(fig['layout'])
            layout['autosize'] = True
            figure_scripts.append(
                f"Plotly.newPlot({json.dumps(div_id)}, "
                f"{json.dumps(fig['traces'])}, {json.dumps(layout)}, "
                "{responsive: true, displaylogo: false});")
            fig_index += 1

        description = (f'<div class="nhr-description">{config.description}</div>'
                       if config.description else '')
        dashboard_link = ''
        if config.id:
            url = f"{self.client.base_url}/dashboards/{config.id}"
            dashboard_link = f' &middot; <a href="{url}">View dashboard on nanoHUB</a>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_escape_html(config.title)} — Report</title>
    <script src="{PLOTLY_CDN}"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         Helvetica, Arial, sans-serif;
            margin: 0; background: #f6f7f9; color: #1f2937; line-height: 1.5;
        }}
        .nhr-page {{ max-width: 960px; margin: 0 auto; padding: 32px 20px 64px; }}
        header h1 {{ font-size: 1.6rem; margin: 0 0 4px; }}
        .nhr-description {{ color: #4b5563; margin: 0 0 4px; }}
        .nhr-meta {{ color: #6b7280; font-size: 0.8rem; margin-bottom: 24px; }}
        .nhr-meta a {{ color: inherit; }}
        .nhr-section {{
            background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 20px 24px; margin-bottom: 20px;
        }}
        .nhr-section h2 {{ font-size: 1.1rem; margin: 0 0 12px; font-weight: 600; }}
        .nhr-figure {{ min-height: 320px; }}
        .nhr-stats {{ color: #4b5563; font-size: 0.85rem; padding-left: 20px; }}
        details {{ margin-top: 12px; }}
        summary {{ cursor: pointer; color: #4b5563; font-size: 0.85rem; }}
        .nhr-table-wrap {{ overflow-x: auto; margin-top: 8px; }}
        table {{ border-collapse: collapse; font-size: 0.85rem; width: 100%; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 4px 10px; text-align: left; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        .nhr-truncated {{ color: #6b7280; font-size: 0.8rem; }}
        @media print {{
            body {{ background: #fff; }}
            .nhr-section {{ border: none; break-inside: avoid; padding: 8px 0; }}
            details {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="nhr-page">
        <header>
            <h1>{_escape_html(config.title)}</h1>
            {description}
            <div class="nhr-meta">Report generated {generated} by nanohub-dashboards{dashboard_link}</div>
        </header>
        {''.join(sections)}
    </div>
    <script>
        {chr(10).join(figure_scripts)}
    </script>
</body>
</html>
"""

    def _tables_html(self, traces: List[Dict], max_rows: int) -> str:
        blocks = []
        for trace in traces:
            table = self._trace_table(trace)
            if not table:
                continue
            headers, rows = table
            truncated = len(rows) > max_rows
            rows = rows[:max_rows]
            head = ''.join(f'<th scope="col">{_escape_html(h)}</th>' for h in headers)
            body = ''.join(
                '<tr>' + ''.join(f'<td>{_escape_html(c)}</td>' for c in row) + '</tr>'
                for row in rows)
            note = (f'<p class="nhr-truncated">Showing first {max_rows} rows.</p>'
                    if truncated else '')
            name = _strip_html(trace.get('name', '') or '')
            label = f'Data table{f" — {_escape_html(name)}" if name else ""}'
            blocks.append(f"""
        <details>
            <summary>{label}</summary>
            <div class="nhr-table-wrap">
            <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
            </div>
            {note}
        </details>""")
        return ''.join(blocks)

    # ------------------------------------------------------------------ #
    # Markdown rendering
    # ------------------------------------------------------------------ #

    def _render_markdown(self, config: DashboardConfig, plots: Dict[str, Dict],
                         include_tables: bool, max_table_rows: int) -> str:
        generated = datetime.now().strftime('%Y-%m-%d %H:%M')
        figures = self._figures(plots)

        lines = [f"# {_strip_html(config.title)}", ""]
        if config.description:
            description = _strip_html(config.description)
            if description:
                lines += [description, ""]
        lines.append(f"*Report generated {generated} by nanohub-dashboards*")
        if config.id:
            lines.append(
                f"*Dashboard: {self.client.base_url}/dashboards/{config.id}*")
        lines.append("")

        fig_index = 0
        for fig in figures:
            if 'html' in fig:
                continue
            title = self._figure_title(fig['layout'], fig_index)
            lines += [f"## {title}", ""]

            stats_lines = [s for s in (self._trace_stats(t) for t in fig['traces']) if s]
            for s in stats_lines:
                lines.append(f"- {s}")
            if stats_lines:
                lines.append("")

            if include_tables:
                for trace in fig['traces']:
                    table = self._trace_table(trace)
                    if not table:
                        continue
                    headers, rows = table
                    truncated = len(rows) > max_table_rows
                    rows = rows[:max_table_rows]
                    lines.append('| ' + ' | '.join(_escape_md(h) for h in headers) + ' |')
                    lines.append('|' + '---|' * len(headers))
                    for row in rows:
                        lines.append('| ' + ' | '.join(_escape_md(c) for c in row) + ' |')
                    if truncated:
                        lines.append(f"\n*Showing first {max_table_rows} rows.*")
                    lines.append("")
            fig_index += 1

        return '\n'.join(lines) + '\n'
