# component: markdown-source-boundaries
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: stdlib, supplied Unicode text only; no task semantics, normalization, files or execution
# last_intent_review: 2026-09-20
"""Static source facts, not a Markdown renderer or permission to normalize task content.

All spans are half-open Python Unicode-codepoint offsets into the unchanged input.
CRLF occupies two positions. Container IDs are local to one classification. Consumers
must classify the full source before choosing excerpts and retain unknown content.
"""
from bisect import bisect_right
from html.parser import HTMLParser
import re
import string
from typing import Literal, NamedTuple, Optional


class Span(NamedTuple):
    start: int
    end: int


class Container(NamedTuple):
    id: int
    parent_id: Optional[int]
    kind: Literal["quote", "list"]
    marker: Span
    content_column: int


class LineBoundary(NamedTuple):
    start: int
    end: int
    next_start: int
    body: Span
    content_start: int
    residual_indent: int
    container_ids: tuple[int, ...]
    kind: Literal["prose", "blank", "fenced_code", "indented_code", "raw_html", "opaque", "unknown"]


class Region(NamedTuple):
    span: Span
    kind: Literal["inline_code", "fenced_code", "indented_code", "quote", "html_tag",
                  "raw_html_body", "comment", "opaque", "unknown"]
    tag: Optional[str]


class ListItemOccurrence(NamedTuple):
    marker: Span
    content: Span
    line_index: int
    container_ids: tuple[int, ...]
    classification: Literal["prose", "quoted", "literal", "unknown"]


class MarkdownBoundaries(NamedTuple):
    original: str
    lines: tuple[LineBoundary, ...]
    containers: tuple[Container, ...]
    regions: tuple[Region, ...]
    list_items: tuple[ListItemOccurrence, ...]


class _Active(NamedTuple):
    id: int
    kind: str
    width: int
    style: str


class _PhysicalLine(NamedTuple):
    start: int
    end: int
    next_start: int
    visual: str
    positions: tuple[int, ...]


_RAW_TAGS = frozenset(("pre", "code", "script", "style"))
_BLOCK_TAGS = frozenset((
    "address", "article", "aside", "blockquote", "body", "caption", "center", "dd",
    "details", "dialog", "div", "dl", "dt", "fieldset", "figcaption", "figure",
    "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr",
    "html", "iframe", "legend", "li", "main", "nav", "ol", "p", "section", "summary",
    "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
))


def _columns(line: str) -> tuple[str, list[int]]:
    expanded, positions = [], []
    for position, char in enumerate(line):
        width = 4 - len(expanded) % 4 if char == "\t" else 1
        expanded.extend(" " * width if char == "\t" else char)
        positions.extend([position] * width)
    positions.append(len(line))
    return "".join(expanded), positions


def _container(line: str, start: int) -> tuple[str, int, int, int, int]:
    cursor = start
    while cursor < len(line) and line[cursor] == " ":
        cursor += 1
    if cursor - start > 3:
        return "", start, 0, start, start
    if line[cursor:cursor + 1] == ">":
        end = cursor + 1
        consumed = end + (line[end:end + 1] == " ")
        return "quote", consumed, consumed - start, cursor, end
    marker = re.match(r"(?:[-+*]|[0-9]{1,9}[.)])(?= |$)", line[cursor:])
    if marker:
        end = cursor + marker.end()
        padding_end = end
        while padding_end < len(line) and line[padding_end] == " ":
            padding_end += 1
        padding = padding_end - end
        padding = padding if 1 <= padding <= 4 else 1
        return "list", min(end + padding, len(line)), end + padding - start, cursor, end
    return "", start, 0, start, start


def _list_style(marker: str) -> str:
    return "ordered" + marker[-1] if marker[0] in string.digits else marker


def _container_interrupts(line: str, cursor: int) -> bool:
    kind, consumed, _, start, end = _container(line, cursor)
    if kind == "quote":
        return True
    if kind != "list" or not line[consumed:].strip():
        return False
    marker = line[start:end]
    return marker[0] not in string.digits or int(marker[:-1]) == 1


def _paragraph_block(line: str, cursor: int) -> bool:
    body = line[cursor:]
    indent = len(body) - len(body.lstrip(" "))
    if indent > 3:
        return False
    body = body[indent:]
    if re.match(r"(?:`{3,}|~{3,}|#{1,6}(?: |$))", body):
        return True
    if re.fullmatch(r"(?:=+|-+)[ \t]*", body) or any(
            re.fullmatch(r"(?:" + re.escape(marker) + r"[ \t]*){3,}", body) for marker in "-*_"):
        return True
    if body.startswith(("<!--", "<!", "<?")):
        return True
    _, tag, closing = _html_token(body, 0)
    return bool(tag in _BLOCK_TAGS or (tag in _RAW_TAGS and not closing))


def _continue_containers(visual: str, active: list[_Active], paragraph: bool) -> tuple[int, list[_Active], bool]:
    cursor, kept = 0, []
    for container in active:
        if container.kind == "quote":
            kind, consumed, _, _, _ = _container(visual, cursor)
            if kind != "quote":
                break
            cursor = consumed
        else:
            available = len(visual[cursor:]) - len(visual[cursor:].lstrip(" "))
            if available < container.width:
                if visual[cursor:].strip():
                    break
                cursor = len(visual)
            else:
                cursor += container.width
        kept.append(container)
    token_kind, _, _, marker_start, marker_end = _container(visual, cursor)
    sibling = (len(kept) < len(active) and token_kind == "list"
               and active[len(kept)].kind == "list"
               and active[len(kept)].style == _list_style(visual[marker_start:marker_end]))
    lazy = (len(kept) != len(active) and paragraph and bool(visual[cursor:].strip())
            and not sibling and not _container_interrupts(visual, cursor)
            and not _paragraph_block(visual, cursor))
    return cursor, active[:] if lazy else kept, lazy


def _physical_lines(text: str) -> list[_PhysicalLine]:
    result = []
    for match in re.finditer(r"[^\r\n]*(?:\r\n|\r|\n|$)", text):
        if not match[0]:
            continue
        body = match[0].rstrip("\r\n")
        visual, positions = _columns(body)
        result.append(_PhysicalLine(match.start(), match.start() + len(body), match.end(),
                                    visual, tuple(positions)))
    return result


def _paragraph_limit(physical: list[_PhysicalLine], index: int, active: list[_Active]) -> int:
    """Use the same container/interruption rules before looking for an inline closer."""
    limit = physical[index].end
    for following in physical[index + 1:]:
        cursor, kept, lazy = _continue_containers(following.visual, active, True)
        if kept != active or not following.visual[cursor:].strip():
            break
        if not lazy and (_container_interrupts(following.visual, cursor)
                         or _paragraph_block(following.visual, cursor)):
            break
        limit = following.end
    return limit


def _tag_end(text: str, start: int) -> int:
    cursor, quoted = start, ""
    while cursor < len(text):
        char = text[cursor]
        if quoted:
            if char == quoted:
                quoted = ""
        elif char in "\"'":
            quoted = char
        elif char == ">":
            return cursor + 1
        cursor += 1
    return -1


def _html_token(text: str, start: int) -> tuple[int, str, bool]:
    prefix = re.match(r"</?([A-Za-z][A-Za-z0-9:-]*)(?=[\s/>])", text[start:])
    if not prefix:
        return start, "", False
    end = _tag_end(text, start + prefix.end())
    return (end, prefix[1].lower(), text.startswith("</", start)) if end >= 0 else (start, "", False)


class _ClosingTag(HTMLParser):
    def __init__(self, text: str, tag: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text, self.tag, self.depth = text, tag, 0
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", text)]
        self.closing: Optional[Span] = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if self.closing is None and tag == self.tag:
            self.depth += 1

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        pass

    def handle_endtag(self, tag: str) -> None:
        if self.closing is None and tag == self.tag:
            self.depth -= 1
            if self.depth == 0:
                line, column = self.getpos()
                start = self.line_offsets[line - 1] + column
                self.closing = Span(start, self.text.find(">", start) + 1)


def _literal(text: str, start: int) -> tuple[int, tuple[Region, ...]]:
    terminators = (("<!--", "-->", "comment"), ("<![CDATA[", "]]>", "opaque"), ("<?", "?>", "opaque"))
    for prefix, terminator, kind in terminators:
        if text.startswith(prefix, start):
            found = text.find(terminator, start + len(prefix))
            end = len(text) if found < 0 else found + len(terminator)
            regions = [Region(Span(start, end), kind, None)]
            if found < 0:
                regions.append(Region(Span(start, end), "unknown", None))
            return end, tuple(regions)
    if text.startswith("<!", start):
        found = _tag_end(text, start + 2)
        end = len(text) if found < 0 else found
        return end, (Region(Span(start, end), "unknown" if found < 0 else "opaque", None),)
    end, tag, closing = _html_token(text, start)
    if end == start:
        if re.match(r"</?[A-Za-z]", text[start:]):
            return len(text), (Region(Span(start, len(text)), "unknown", None),)
        return start, ()
    regions = [Region(Span(start, end), "html_tag", tag)]
    if closing or tag not in _RAW_TAGS or text[start:end].endswith("/>"):
        return end, tuple(regions)
    parser = _ClosingTag(text[start:], tag)
    for line in text[start:].splitlines(keepends=True):
        parser.feed(line)
        if parser.closing is not None:
            break
    if parser.closing is None:
        # Newer HTMLParser releases buffer incrementally fed script/style data until close().
        parser.close()
    if parser.closing is None:
        regions.extend((Region(Span(end, len(text)), "raw_html_body", tag),
                        Region(Span(start, len(text)), "unknown", tag)))
        return len(text), tuple(regions)
    closed = Span(start + parser.closing.start, start + parser.closing.end)
    regions.extend((Region(Span(end, closed.start), "raw_html_body", tag),
                    Region(closed, "html_tag", tag)))
    return closed.end, tuple(regions)


def _code_end(text: str, start: int, limit: int) -> int:
    run = re.match(r"`+", text[start:])[0]
    for match in re.finditer(r"`+", text[start + len(run):limit]):
        if match[0] == run:
            return start + len(run) + match.end()
    return start


def _projection(text: str, lines: list[LineBoundary]) -> str:
    characters = list(text)
    for line in lines:
        for position in range(line.start, line.end):
            if position < line.body.start or line.kind in ("fenced_code", "indented_code"):
                characters[position] = " "
        for position in range(line.end, line.next_start):
            if text[position] == "\r":
                characters[position] = " " if text[position:position + 2] == "\r\n" else "\n"
    return "".join(characters)


def classify_markdown(text: str) -> MarkdownBoundaries:
    """Classify the FULL exact source before a consumer selects an excerpt or a marker."""
    if not isinstance(text, str):
        raise TypeError("Markdown source must be a Unicode string")
    if not text:
        return MarkdownBoundaries(text, (), (), (), ())
    lines: list[LineBoundary] = []
    containers: list[Container] = []
    active: list[_Active] = []
    regions: list[Region] = []
    candidates: list[ListItemOccurrence] = []
    previous_context, paragraph = (), False
    fence, literal_until, inline_until, opaque_context = None, 0, 0, None
    physical = _physical_lines(text)
    for line_index, physical_line in enumerate(physical):
        start, end, next_start, visual, positions = physical_line
        cursor, active, lazy = _continue_containers(visual, active, paragraph)
        context = tuple(container.id for container in active)
        if fence and context != fence[2]:
            fence = None
        if opaque_context is not None and (context != opaque_context or not visual[cursor:].strip()):
            opaque_context = None
        if not fence and start >= max(literal_until, inline_until) and opaque_context is None and not lazy:
            while True:
                kind, consumed, width, marker_start, marker_end = _container(visual, cursor)
                if not kind:
                    break
                if paragraph and tuple(container.id for container in active) == previous_context \
                        and not _container_interrupts(visual, cursor):
                    break
                identity = len(containers) + 1
                marker = Span(start + positions[marker_start], start + positions[marker_end])
                containers.append(Container(identity, active[-1].id if active else None, kind, marker, consumed))
                active.append(_Active(identity, kind, width,
                                      _list_style(visual[marker_start:marker_end]) if kind == "list" else ">"))
                if kind == "list":
                    candidates.append(ListItemOccurrence(marker, Span(start + positions[consumed], end),
                                      len(lines), tuple(container.id for container in active), "unknown"))
                cursor = consumed
        context = tuple(container.id for container in active)
        content = cursor
        while content < len(visual) and visual[content] == " ":
            content += 1
        indent = content - cursor
        body_start, content_start = start + positions[cursor], start + positions[content]
        marker = re.match(r"(`{3,}|~{3,})(.*)", visual[content:]) if indent <= 3 else None
        if start < literal_until:
            kind = "raw_html"
        elif opaque_context is not None:
            kind = "opaque"
        elif fence:
            kind = "fenced_code"
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker and not (marker[1][0] == "`" and "`" in marker[2]):
            kind, fence = "fenced_code", (marker[1][0], len(marker[1]), context)
        elif not visual[content:]:
            kind = "blank"
        elif indent >= 4 and not (paragraph and context == previous_context):
            kind = "indented_code"
        else:
            kind = "prose"
        if kind == "prose" and content_start >= inline_until and text[content_start:content_start + 1] == "<":
            tag_end, tag, _ = _html_token(text, content_start)
            standalone = tag_end > content_start and not text[tag_end:end].strip()
            if tag not in _RAW_TAGS and (tag in _BLOCK_TAGS or (standalone and not paragraph)):
                kind, opaque_context = "opaque", context
        if kind in ("fenced_code", "indented_code", "opaque"):
            regions.append(Region(Span(body_start, end), kind, None))
        if any(containers[identity - 1].kind == "quote" for identity in context):
            regions.append(Region(Span(start, next_start), "quote", None))
        if kind in ("prose", "opaque"):
            probe = max(content_start, inline_until)
            while probe < end:
                if text[probe] == "\\" and probe + 1 < end and text[probe + 1] in string.punctuation:
                    probe += 2
                    continue
                if text[probe] == "`" and kind == "prose":
                    code_end = _code_end(text, probe, _paragraph_limit(physical, line_index, active))
                    if code_end != probe:
                        regions.append(Region(Span(probe, code_end), "inline_code", None))
                        inline_until = max(inline_until, code_end)
                        probe = code_end
                        continue
                if text[probe] == "<":
                    literal_end, found = _literal(text, probe)
                    if literal_end != probe:
                        regions.extend(found)
                        literal_until = max(literal_until, literal_end)
                        if probe == content_start and any(region.kind in ("comment", "raw_html_body", "unknown")
                                                         for region in found):
                            kind = "unknown" if any(region.kind == "unknown" for region in found) else "raw_html"
                        probe = literal_end
                        continue
                probe += 1
        lines.append(LineBoundary(start, end, next_start, Span(body_start, end), content_start,
                                  indent, context, kind))
        paragraph = kind == "prose" and literal_until <= next_start
        if re.match(r"#{1,6}(?: |$)", visual[content:]):
            paragraph = False
        previous_context = context

    projected = _projection(text, lines)
    starts = [line.start for line in lines]
    literal_spans = sorted((region.span for region in regions
                            if region.kind in ("inline_code", "raw_html_body", "comment", "unknown")),
                           key=lambda span: span.start)
    cursor, literal_index = 0, 0
    while cursor < len(projected):
        while literal_index < len(literal_spans) and literal_spans[literal_index].end <= cursor:
            literal_index += 1
        if literal_index < len(literal_spans) and literal_spans[literal_index].start <= cursor:
            cursor = literal_spans[literal_index].end
            continue
        index = max(0, bisect_right(starts, cursor) - 1)
        line = lines[index]
        if line.kind in ("fenced_code", "indented_code"):
            cursor = line.next_start
            continue
        if projected[cursor] == "\\" and cursor + 1 < len(projected) and projected[cursor + 1] in string.punctuation:
            regions.append(Region(Span(cursor, cursor + 2), "opaque", None))
            cursor += 2
            continue
        if projected[cursor] == "<":
            literal_end, found = _literal(projected, cursor)
            if literal_end != cursor:
                regions.extend(found)
                cursor = literal_end
                continue
        cursor += 1

    ordered = tuple(sorted(set(regions), key=lambda region:
                           (region.span.start, region.span.end, region.kind, region.tag or "")))
    exclusions = [region for region in ordered if region.kind != "quote"]
    items = []
    for item in candidates:
        if any(region.kind in ("inline_code", "raw_html_body", "comment", "unknown", "opaque")
               and region.span.start <= item.marker.start < region.span.end for region in exclusions):
            continue
        first = item.content.start
        while first < item.content.end and text[first] in " \t":
            first += 1
        at_content = [region.kind for region in exclusions if region.span.start <= first < region.span.end]
        line = lines[item.line_index]
        if "unknown" in at_content or line.kind == "unknown":
            classification = "unknown"
        elif at_content or line.kind in ("fenced_code", "indented_code", "raw_html", "opaque"):
            classification = "literal"
        elif any(containers[identity - 1].kind == "quote" for identity in item.container_ids):
            classification = "quoted"
        else:
            classification = "prose"
        items.append(item._replace(classification=classification))
    return MarkdownBoundaries(text, tuple(lines), tuple(containers), ordered, tuple(items))
