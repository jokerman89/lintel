"""Public navigation parsing, closure and explicit source-only/privacy boundaries."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("adapter", ROOT / "bin/li-copilot.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class AdapterNavigation(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix="lintel-nav-")
        self.root = Path(self.sandbox.name).resolve()
        for relative in adapter.DOCS:
            self.write(relative, "# Public guide\n")
        self.write(".claude-plugin/plugin.json", json.dumps({"repository": "https://github.com/jokerman89/lintel"}))

    def tearDown(self):
        self.sandbox.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_literal_inline_reference_and_html_links(self):
        content = b"""[Guide](docs/guide.md#intro "title")
![Image](docs/chart.svg)
[A spaced guide](<docs/guide one.md>)
[Parentheses](docs/guide(v2).md)
[Reference][ref]

[ref]: docs/reference.md "title"
<a href="docs/html-guide.md">Guide</a><img src=docs/image.png>
"""
        self.assertEqual([url for _, _, url in adapter.document_links(content)], [
            "docs/guide.md#intro", "docs/chart.svg", "docs/guide one.md",
            "docs/guide(v2).md", "docs/reference.md", "docs/html-guide.md", "docs/image.png",
        ])

    def test_code_comments_and_placeholders_are_not_bundle_resources(self):
        content = b"""`[Inline example](docs/no-inline.md)`
``[Backtick ` example](docs/no-backtick.md)``
<!-- [Comment](docs/no-comment.md) -->

```markdown
[Fenced example](docs/no-fence.md)
```

~~~text
[Tilde example](docs/no-tilde.md)
~~~

    [Indented example](docs/no-indent.md)

<pre><a href="docs/no-pre.md">Example</a></pre>
<script>const sample = '<a href="docs/no-script.md">';</script>
[Template](docs/<name>.md)
[Template](docs/%3Cname%3E.md)
[Template](docs/{name}.md)
[Template](docs/*.md)
The attribute example href="docs/no-prose.md" is not a tag.

- A list item

    [Real continuation](docs/list.md)

[actual]: docs/actual.md
"""
        self.assertEqual([url for _, _, url in adapter.document_links(content)],
                         ["docs/list.md", "docs/actual.md"])

    def test_public_links_close_transitively_without_glob_copy(self):
        self.write("README.md", "[First](docs/one.md)\n")
        self.write("docs/one.md", "[Second][two]\n\n[two]: nested/two.md\n")
        self.write("docs/nested/two.md", '[Asset](../asset.svg)\n[Public folder](./)\n')
        self.write("docs/asset.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>\n')
        self.write("docs/not-linked.md", "Not selected merely because it exists.\n")
        files = {}
        adapter.bundle_documentation(self.root, files)
        for relative in ("docs/one.md", "docs/nested/two.md", "docs/asset.svg"):
            self.assertIn(f"{adapter.BUNDLE}/{relative}", files)
        self.assertNotIn(f"{adapter.BUNDLE}/docs/not-linked.md", files)
        self.assertEqual(adapter.verify_links(files, self.root), [])

    def test_excluded_source_links_preserve_navigation_without_reading_private_content(self):
        excluded = (".claude/memory/lessons.md", ".claude/runtime/private.md",
                    "packs/company/pack.yaml", "docs/.private/notes.md", "docs/.private/")
        self.write("README.md", "\n".join(f"[Source]({path})" for path in excluded) + "\n")
        for relative in excluded:
            self.write(relative + "README.md" if relative.endswith("/") else relative,
                       "SYNTHETIC-PRIVATE-BYTES-MUST-NOT-BUNDLE")
        files = {}
        with patch.object(adapter, "read_file", wraps=adapter.read_file) as reads:
            adapter.bundle_documentation(self.root, files)
        actual_reads = {call.args[1] for call in reads.call_args_list}
        self.assertFalse(any(path == relative or (relative.endswith("/") and path.startswith(relative))
                             for relative in excluded for path in actual_reads))
        readme = files[f"{adapter.BUNDLE}/README.md"].decode()
        self.assertIn("outside this portable bundle", readme)
        self.assertIn("not fetched or live-verified", readme)
        for relative in excluded:
            self.assertNotIn(f"{adapter.BUNDLE}/{relative}", files)
            kind = "tree" if relative.endswith("/") else "blob"
            self.assertIn(f"https://github.com/jokerman89/lintel/{kind}/main/{relative.rstrip('/')}", readme)
        self.assertNotIn(b"SYNTHETIC-PRIVATE", b"".join(files.values()))
        self.assertEqual(adapter.verify_links(files, self.root), [])

    def test_missing_public_target_fails_instead_of_becoming_source_only(self):
        self.write("README.md", "[Required public target](docs/missing.md)\n")
        with self.assertRaisesRegex(ValueError, "Required source file is missing"):
            adapter.bundle_documentation(self.root, {})

    def test_missing_bundled_method_does_not_silently_become_an_upstream_link(self):
        self.write("README.md", "[A promised bundled method](skills/missing/SKILL.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing bundled source target"):
            adapter.bundle_documentation(self.root, {})

    def test_bundled_target_must_be_in_inventory_not_an_existing_unmanaged_file(self):
        self.write(f"{adapter.BUNDLE}/docs/forgotten.md", "# Existing but not managed\n")
        files = {f"{adapter.BUNDLE}/README.md": b"[Forgotten](docs/forgotten.md)\n"}
        self.assertIn("Missing bundled documentation target", "\n".join(adapter.verify_links(files, self.root)))
        files[f"{adapter.BUNDLE}/README.md"] = b"[Project file](../../private.md)\n"
        self.write("private.md", "Must not be used as a bundled source target.\n")
        self.assertIn("escapes source", "\n".join(adapter.verify_links(files, self.root)))

    def test_absolute_and_escaping_links_are_rejected_without_reading_targets(self):
        for link in ("../../../escape.md", "file:///private.md", "C:\\private.md",
                     "/absolute.md", "~/.private.md", "%2e%2e/%2e%2e/escape.md"):
            with self.subTest(link=link), self.assertRaises(ValueError):
                adapter.local_link("docs/guide.md", link)
        for link in ("#heading", "https://example.invalid/guide.md", "mailto:docs@example.invalid"):
            self.assertEqual(adapter.local_link("README.md", link), "")
        self.assertEqual(adapter.local_link("docs/guide.md", "guide%20two.md#intro"), "docs/guide two.md")

    def test_symlinked_public_document_is_refused(self):
        self.write("private.md", "SYNTHETIC-PRIVATE-NOT-A-DOC")
        self.write("README.md", "[Public alias](docs/alias.md)\n")
        try:
            (self.root / "docs/alias.md").symlink_to(self.root / "private.md")
        except OSError as error:
            self.skipTest(f"Host does not permit symlink fixtures: {error}")
        with self.assertRaisesRegex(ValueError, "Symlink/reparse"):
            adapter.bundle_documentation(self.root, {})

    def test_public_text_assets_normalize_line_endings_without_touching_binary_bytes(self):
        for suffix in (".md", ".html", ".htm", ".css", ".js", ".svg"):
            path = self.root / ("asset" + suffix)
            path.write_bytes(b"first\r\nsecond\r\n")
            self.assertEqual(adapter.source_bytes(path), b"first\nsecond\n", suffix)
        image = self.root / "image.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\n\x00")
        self.assertEqual(adapter.source_bytes(image), b"\x89PNG\r\n\x1a\n\x00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
