"""Independent source-span expectations for the shared, task-agnostic boundary API."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from markdown_source import (Container, LineBoundary, ListItemOccurrence, MarkdownBoundaries,
                             Region, Span, classify_markdown)


class MarkdownSourceContract(unittest.TestCase):
    def test_exact_unicode_crlf_original_coordinates_and_structural_occurrences(self):
        text = "\u03bb\n- [ ] A\r\n  continuation\r\n> - [x] Q"
        result = classify_markdown(text)
        self.assertIs(result.original, text)
        self.assertEqual([(line.start, line.end, line.next_start) for line in result.lines],
                         [(0, 1, 2), (2, 9, 11), (11, 25, 27), (27, 36, 36)])
        self.assertEqual(result.containers, (
            Container(1, None, "list", Span(2, 3), 2),
            Container(2, None, "quote", Span(27, 28), 2),
            Container(3, 2, "list", Span(29, 30), 4),
        ))
        self.assertEqual(result.list_items, (
            ListItemOccurrence(Span(2, 3), Span(4, 9), 1, (1,), "prose"),
            ListItemOccurrence(Span(29, 30), Span(31, 36), 3, (2, 3), "quoted"),
        ))
        self.assertEqual(text[result.list_items[0].content.start:result.list_items[0].content.end], "[ ] A")
        self.assertNotEqual(result.list_items[0].marker.start, len(text[:2].encode("utf-8")))
        self.assertIn(Region(Span(27, 36), "quote", None), result.regions)

    def test_declared_types_are_immutable_and_invalid_inputs_fail_explicitly(self):
        result = classify_markdown("- [ ] task")
        self.assertIsInstance(result, MarkdownBoundaries)
        self.assertIsInstance(result.lines[0], LineBoundary)
        for value, field in ((result, "original"), (result.lines[0], "kind"),
                             (result.containers[0], "kind"), (result.list_items[0], "classification")):
            with self.assertRaises(AttributeError):
                setattr(value, field, "changed")
        self.assertTrue(all(isinstance(getattr(result, field), tuple)
                            for field in ("lines", "containers", "regions", "list_items")))
        for invalid in (None, b"- [ ] bytes", 12, []):
            with self.subTest(invalid=type(invalid).__name__), self.assertRaises(TypeError):
                classify_markdown(invalid)
        self.assertEqual(classify_markdown(""), MarkdownBoundaries("", (), (), (), ()))
        for record, fields in (
            (Span, ("start", "end")),
            (Container, ("id", "parent_id", "kind", "marker", "content_column")),
            (LineBoundary, ("start", "end", "next_start", "body", "content_start", "residual_indent", "container_ids", "kind")),
            (Region, ("span", "kind", "tag")),
            (ListItemOccurrence, ("marker", "content", "line_index", "container_ids", "classification")),
            (MarkdownBoundaries, ("original", "lines", "containers", "regions", "list_items")),
        ):
            self.assertEqual(record._fields, fields)

    def test_compound_list_fence_is_literal_before_any_checkbox_interpretation(self):
        text = "- - ```markdown\n    - [x] literal\n    ```\n\n- [ ] actual\n"
        result = classify_markdown(text)
        self.assertEqual([line.kind for line in result.lines],
                         ["fenced_code", "fenced_code", "fenced_code", "blank", "prose"])
        self.assertEqual([(item.marker, item.content, item.classification) for item in result.list_items], [
            (Span(0, 1), Span(2, 15), "literal"),
            (Span(2, 3), Span(4, 15), "literal"),
            (Span(43, 44), Span(45, 55), "prose"),
        ])
        self.assertFalse(any(item.marker.start == text.index("- [x]") for item in result.list_items))
        self.assertTrue(any(region.kind == "fenced_code" and region.span.start <= text.index("[x]") < region.span.end
                            for region in result.regions))

    def test_raw_elements_and_comments_cover_same_line_and_full_body(self):
        for tag in ("pre", "code", "script", "style", "PRE", "CODE", "SCRIPT", "STYLE"):
            for separator in ("", "\n", "\r\n"):
                text = f'<{tag} data-note=">">- [x] first{separator}- [x] second</{tag}>\n- [ ] real'
                with self.subTest(tag=tag, separator=repr(separator)):
                    result = classify_markdown(text)
                    self.assertEqual([text[item.content.start:item.content.end] for item in result.list_items
                                      if item.classification == "prose"], ["[ ] real"])
                    raw = [region for region in result.regions if region.kind == "raw_html_body"]
                    self.assertTrue(any(region.span.start == text.index("- [x]")
                                        and region.span.end == text.index(f"</{tag}>") for region in raw))
                    self.assertTrue(any(region.kind == "html_tag" and region.span.start == 0
                                        and region.tag == tag.lower() for region in result.regions))
        text = "<!-- - [x] same line\n- [x] next line -->\n- [ ] real"
        result = classify_markdown(text)
        self.assertIn(Region(Span(0, text.index("-->") + 3), "comment", None), result.regions)
        self.assertEqual([text[item.content.start:item.content.end] for item in result.list_items], ["[ ] real"])

    def test_actual_markers_are_not_continuations_inline_examples_or_quote_permission(self):
        text = (
            "- [ ] real `inline example`\n"
            "  [x] continuation without marker\n"
            "- `[x] inline-only`\n"
            "- <pre>[x] raw-only</pre>\n"
            "- <!-- [x] comment-only -->\n"
            "> - [x] quoted\n"
            "\n"
            "- - [ ] nested real\n"
        )
        result = classify_markdown(text)
        slices = [(text[item.content.start:item.content.end], item.classification) for item in result.list_items]
        self.assertIn(("[ ] real `inline example`", "prose"), slices)
        self.assertIn(("`[x] inline-only`", "literal"), slices)
        self.assertIn(("<pre>[x] raw-only</pre>", "literal"), slices)
        self.assertIn(("<!-- [x] comment-only -->", "literal"), slices)
        self.assertIn(("[x] quoted", "quoted"), slices)
        self.assertIn(("[ ] nested real", "prose"), slices)
        self.assertFalse(any("continuation" in content for content, _ in slices))

    def test_quote_indentation_tabs_and_nested_container_evidence(self):
        fixtures = (
            ">     - [x] code\n>\n> - [ ] quoted",
            "> \t  - [x] code\n>\n> - [ ] quoted",
            "- Parent\n\n      - [x] code\n\n  - [ ] real",
            "10. Parent\n\n        - [x] code\n\n    - [ ] real",
            "- > Parent\n  >\n  >     - [x] code\n  >\n  > - [ ] quoted",
        )
        for text in fixtures:
            with self.subTest(text=text):
                result = classify_markdown(text)
                code_position = text.index("[x]")
                self.assertTrue(any(region.kind == "indented_code"
                                    and region.span.start <= code_position < region.span.end
                                    for region in result.regions))
                self.assertFalse(any(item.marker.start == text.index("- [x]") for item in result.list_items))
                self.assertTrue(any(text[item.content.start:item.content.end] in ("[ ] real", "[ ] quoted")
                                    for item in result.list_items))

    def test_unknown_and_opaque_are_explicit_not_prose_eligibility(self):
        for text in ('<script src="app.js">\n- [x] unclosed',
                     '<pre>\n- [x] unclosed', '<a href="unfinished\n- [x] uncertain'):
            with self.subTest(text=text):
                result = classify_markdown(text)
                self.assertTrue(any(region.kind == "unknown" for region in result.regions))
                self.assertFalse(any(item.classification == "prose" for item in result.list_items))
        text = "<![CDATA[\n- [x] opaque\n]]>\n- [ ] real"
        result = classify_markdown(text)
        self.assertTrue(any(region.kind == "opaque" and region.span.start == 0
                            and region.span.end == text.index("]]>") + 3 for region in result.regions))
        self.assertEqual([text[item.content.start:item.content.end] for item in result.list_items], ["[ ] real"])
        text = '<!DOCTYPE html SYSTEM "quoted >\n- [x] declaration">\n- [ ] real'
        result = classify_markdown(text)
        self.assertTrue(any(region.kind == "opaque" and region.span.start == 0
                            and region.span.end == text.index('">') + 2 for region in result.regions))
        self.assertEqual([text[item.content.start:item.content.end] for item in result.list_items], ["[ ] real"])

    def test_classify_full_source_before_excerpt_keeps_surrounding_literal_context(self):
        text = "```markdown\n- [x] example\n```\n- [ ] real"
        result = classify_markdown(text)
        start, end = text.index("- [x]"), text.index("\n```")
        self.assertFalse(any(start <= item.marker.start < end for item in result.list_items))
        isolated_excerpt = classify_markdown(text[start:end])
        self.assertEqual(isolated_excerpt.list_items[0].classification, "prose")
        self.assertEqual(result.original, text)

    def test_regions_are_deterministic_in_bounds_and_do_not_mutate_newlines(self):
        for text in ("- [ ] root", "> - [x] quote\n", ">     code\r\n\r\n- [ ] item\r\n",
                     '<script src="x.js">body</script>', "\u03bb\n- [ ] \u03c9"):
            with self.subTest(text=text):
                result = classify_markdown(text)
                self.assertEqual(result, classify_markdown(text))
                self.assertIs(result.original, text)
                self.assertEqual(result.regions, tuple(sorted(result.regions,
                                 key=lambda region: (region.span.start, region.span.end, region.kind, region.tag or ""))))
                for region in result.regions:
                    self.assertLessEqual(0, region.span.start)
                    self.assertLessEqual(region.span.start, region.span.end)
                    self.assertLessEqual(region.span.end, len(text))

    def test_html_block_regions_keep_attributes_but_not_literal_item_occurrences(self):
        text = '<div>\n- [x] HTML body\n<a href="guide.md">Guide</a>\n</div>\n\n- [ ] real'
        result = classify_markdown(text)
        self.assertEqual([text[item.content.start:item.content.end] for item in result.list_items], ["[ ] real"])
        self.assertTrue(any(region.kind == "opaque" and region.span.start <= text.index("[x]") < region.span.end
                            for region in result.regions))
        self.assertTrue(any(region.kind == "html_tag" and text[region.span.start:region.span.end]
                            == '<a href="guide.md">' for region in result.regions))
        self.assertEqual(result.original, text)

    def test_nested_real_and_literal_markers_have_independently_expected_first_line_spans(self):
        text = "- Outer\n  1. [ ] nested\n     continuation\n  - > - [x] quoted\n-     code-only"
        result = classify_markdown(text)
        actual = [(text[item.marker.start:item.marker.end], text[item.content.start:item.content.end],
                   item.classification) for item in result.list_items]
        self.assertEqual(actual, [
            ("-", "Outer", "prose"), ("1.", "[ ] nested", "prose"),
            ("-", "> - [x] quoted", "prose"), ("-", "[x] quoted", "quoted"),
            ("-", "    code-only", "literal"),
        ])
        self.assertFalse(any("continuation" in content for _, content, _ in actual))
        self.assertEqual(result.lines[-1].residual_indent, 4)

    def test_ordered_marker_cannot_claim_a_noninterrupting_paragraph_continuation(self):
        text = "Paragraph\n2. [ ] A05.2 ordinary continuation\n"
        self.assertEqual(classify_markdown(text).list_items, ())
        for control, marker in (
                ("Paragraph\n\n2. [ ] A05.2 real item\n", Span(11, 13)),
                ("Paragraph\n1. [ ] A05.2 real item\n", Span(10, 12))):
            with self.subTest(control=control):
                items = classify_markdown(control).list_items
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0].marker, marker)
                self.assertEqual(items[0].classification, "prose")
        siblings = classify_markdown("1. First item\n2. [ ] genuine second item\n")
        self.assertEqual(len(siblings.list_items), 2)
        self.assertEqual([item.classification for item in siblings.list_items], ["prose", "prose"])

    def test_multiline_inline_code_precedes_html_body_discovery(self):
        text = '`<script src="review-fixture/code-only.js">\n</script>`\n\n[Real](review-fixture/guide.md)\n'
        end = text.index("`\n\n") + 1
        result = classify_markdown(text)
        self.assertIn(Region(Span(0, end), "inline_code", None), result.regions)
        self.assertFalse(any(region.kind in ("html_tag", "raw_html_body") and region.span.start < end
                             for region in result.regions))
        one_line = text.replace(">\n</script>", "></script>")
        self.assertIn("inline_code", [region.kind for region in classify_markdown(one_line).regions])
        self.assertEqual(result.original, text)

    def test_paragraph_interruption_grid_preserves_real_siblings_and_blank_line_starts(self):
        contexts = (
            ("Paragraph", "", ""),
            ("> Paragraph", "> ", ">"),
            ("- Paragraph", "  ", ""),
        )
        for paragraph, prefix, blank in contexts:
            for number in ("0", "1", "2", "01", "10", "999999999"):
                for delimiter in (".", ")"):
                    for eol in ("\n", "\r\n"):
                        content = "[ ] selected continuation"
                        direct = f"{paragraph}{eol}{prefix}{number}{delimiter} {content}"
                        separated = f"{paragraph}{eol}{blank}{eol}{prefix}{number}{delimiter} {content}"
                        with self.subTest(paragraph=paragraph, number=number, delimiter=delimiter, eol=repr(eol)):
                            direct_items = [item for item in classify_markdown(direct).list_items
                                            if direct[item.content.start:item.content.end] == content]
                            blank_items = [item for item in classify_markdown(separated).list_items
                                           if separated[item.content.start:item.content.end] == content]
                            self.assertEqual(bool(direct_items), int(number) == 1)
                            self.assertEqual(len(blank_items), 1)
        for text in ("1. First\n2. [ ] sibling", "3) First\n4) [ ] sibling",
                     "- Outer\n  1. First\n  2. [ ] sibling", "> 1. First\n> 2. [ ] sibling"):
            with self.subTest(siblings=text):
                self.assertTrue(any(text[item.content.start:item.content.end] == "[ ] sibling"
                                    for item in classify_markdown(text).list_items))
        for text in ("Paragraph\n-\ntext", "Paragraph\n2.\ntext", "\u0661. [ ] not ASCII digits",
                     "1000000000. [ ] not a valid marker"):
            with self.subTest(non_marker=text):
                self.assertEqual(classify_markdown(text).list_items, ())

    def test_multiline_code_uses_paragraph_boundaries_before_literal_html_rules(self):
        for prefix in ("", "> ", "> > ", "  "):
            for ticks in ("`", "``"):
                for eol in ("\n", "\r\n"):
                    opening = "- Item\n" if prefix == "  " else ""
                    text = (opening + f'{prefix}{ticks}<script src="code-only.js">{eol}'
                            f'{prefix}</script>{ticks}{eol}{prefix}{eol}'
                            f'{prefix}[Real](guide.md)')
                    with self.subTest(prefix=prefix, ticks=ticks, eol=repr(eol)):
                        facts = classify_markdown(text)
                        start = text.index(ticks + "<script")
                        end = text.index("</script>" + ticks) + len("</script>" + ticks)
                        self.assertIn(Region(Span(start, end), "inline_code", None), facts.regions)
                        self.assertFalse(any(region.kind == "html_tag" and start <= region.span.start < end
                                             for region in facts.regions))
        for interrupt in ("1. [ ] actual", "> Quote", "# Heading", "```markdown\nliteral\n```"):
            text = f"`unclosed paragraph\n{interrupt}\nclosing`"
            with self.subTest(interrupt=interrupt):
                self.assertFalse(any(region.kind == "inline_code" and region.span.start == 0
                                     for region in classify_markdown(text).regions))
        text = '`unclosed paragraph\n\n<script src="actual.js"></script>`'
        self.assertTrue(any(region.kind == "html_tag" and region.tag == "script"
                            for region in classify_markdown(text).regions))


if __name__ == "__main__":
    unittest.main(verbosity=2)
