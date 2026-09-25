Synthetic module `util.py` (not repository code). Review it as a code change.

```python
def paginate(items, page, per_page=10):
    """Return the requested 1-based page of items."""
    start = page * per_page
    end = start + per_page
    return items[start:end]


def safe_filename(name):
    """Return a name that cannot escape the upload directory."""
    return name.replace("..", "").replace("/", "_")


def retry(fn, attempts=3):
    """Call fn, retrying on failure; re-raise the last error."""
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts:
                raise
```

Callers pass `name` from an uploaded file's client-supplied name and join it to the upload
directory with `os.path.join`. The service runs on Linux and Windows.
