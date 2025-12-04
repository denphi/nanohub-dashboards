# Analysis of Server-Side Rendering Logic

## Server Logic (`com_dashboards/helpers/renderer.php`)

1.  **Extract Placeholders**:
    ```php
    preg_match_all("#%([\w][\w\d\._]+)[\s]*#i", $g["plot"], $matches, PREG_SET_ORDER);
    ```
    It finds all placeholders like `%VAR` in the raw `plot` string.

2.  **Query Data**:
    It constructs a SQL query based on these placeholders.

3.  **Group Handling**:
    If grouping is enabled (`$g["group"]`), it iterates through groups.
    Inside the loop, it modifies the template string **before** `json_decode`:
    ```php
    $template = json_decode(preg_replace('/(: *)(%[\w][\w\d=\/]*)/', "$1\"$2%" . $rggrp . "%\"", $g["plot"]), true);
    ```
    It looks for `: %VAR` and replaces it with `: "%VAR%GROUP_VALUE%"`.
    **Crucially, it expects the placeholder to be unquoted in the source string.**

4.  **Final Replacement**:
    After processing, it encodes back to JSON and does a final replacement:
    ```php
    $plot = preg_replace('/"%([\w][\w\d_]*\.)?([\w][\w\d_]*)%([^%]+)%"/i', "%$3%$2", $plot);
    $plot = strtr($plot, $results);
    ```

## The Problem

My fix in the Python client converts `{"key": %VAR}` to `{"key": "%VAR"}` to make it valid JSON.

However, the server's regex `preg_replace('/(: *)(%[\w][\w\d=\/]*)/', ...)` specifically looks for a colon followed by an **unquoted** placeholder (ignoring whitespace).

If I send `{"key": "%VAR"}`, the server sees `: "%VAR"`.
The regex `(: *)(%[\w][\w\d=\/]*)` might NOT match because of the quote.
Wait, `%` matches `%`. But the regex expects `%` to be the *start* of the capture group 2.
If the input is `: "%VAR"`, the char after `:` (and space) is `"`.
The regex expects `%`.
So `preg_replace` fails to inject the group value.

## The Solution

The client needs to replicate the server's logic for *replacing* values, not just making it valid JSON.
But the client is running locally, not on the server. The client's `visualize` method fetches data and renders HTML locally.
The client implementation in `_process_graphs` tries to replicate the server's behavior.

Let's look at `client.py` again.
In `_process_graphs`:
```python
            # Get plot template
            # Check if the graph object has plots
            if hasattr(graph, 'plots') and graph.plots:
                 # ...
            else:
                # Fallback to raw graph data
                plot_template_str = raw_graph.get('plot', '[]')
                try:
                    fixed_template = self._fix_json_placeholders(plot_template_str)
                    plot_templates = json.loads(fixed_template)
```

The client parses the template into `plot_templates`.
Then it needs to substitute values.
I need to see how the client substitutes values. I suspect it iterates over `plot_templates` and does string replacement.

If `plot_templates` now contains `"%VAR"` strings, the substitution logic must match that.

Let's check `client.py` lines 800+ to see how it handles data substitution.
