# component: presentation-guide-generator
# implements: none (bounded presentation maintenance)
# intent: ../README.md
# constraints: public content only; no external dependencies
# last_intent_review: 2026-09-28
"""Keep presenter guides synchronized with the canonical slide content."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8-sig")


def write(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8")


def clock(minutes: float) -> str:
    seconds = round(minutes * 60)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def main() -> None:
    source = read("show/content.js")
    slides = json.loads(source[source.index("["):source.rindex("]") + 1])
    # Reuse the public guide's theme assets so notes and runbooks stay consistent.
    head = read("presenter/demo-runbook.html").split("</head>")[0] + "</head>"
    head = re.sub("<title>.*?</title>", "<title>{title} · Lintel</title>", head)
    escape = html.escape

    def page(title: str, body: str) -> str:
        return (
            head.replace("{title}", escape(title))
            + '<body><header><a href="../index.html">LINTEL / FIELD GUIDE</a>'
            + '<nav class="local-nav"><a href="../show/index.html">Slides</a>'
            + '<a href="run-of-show.html">Timing</a>'
            + '<a href="demo-runbook.html">Demo runbook</a></nav></header>'
            + "<main><h1>" + escape(title) + "</h1>" + body + "</main>"
            + "<footer>Built with 💜 By Johannes Åkerman<br>"
            + "Independent open-source project</footer></body></html>"
        )

    groups = [
        ("Main story", lambda s: not s.get("optional"), "presenter/speaker-script.html"),
        ("Products", lambda s: s.get("track") == "products", "presenter/product-launch.html"),
        ("Technical", lambda s: s.get("track") == "technical", "presenter/technical-section.html"),
    ]
    overview = (
        f"<p>{len(slides)} slides: an untimed welcome, a 50-minute main story, "
        "a separate 6-minute product section and an 18-minute technical module. "
        "Use Overview to choose a section.</p><p>Story: meet the system → learn "
        "the method → make context durable → scale responsibly → test value → "
        "adopt selectively.</p>"
    )
    for title, select, output in groups:
        elapsed = 0
        script = ""
        table = (
            "<h2>" + title + "</h2><table><tr><th>Time</th><th>Slide</th>"
            "<th>Delivery action</th></tr>"
        )
        for number, slide in enumerate(slides, 1):
            if not select(slide):
                continue
            end = elapsed + slide["minutes"]
            stamp = "Untimed" if slide.get("holding") else clock(elapsed) + "–" + clock(end)
            elapsed = end
            link = "../show/index.html#" + slide["id"]
            name = escape(slide["title"].replace("\n", " "))
            script += (
                '<section id="' + slide["id"] + '"><p class="time">' + stamp
                + " · SLIDE " + str(number) + '</p><h2><a href="' + link + '">'
                + name + "</a></h2>"
            )
            for key, label in [("cue", "SAY"), ("stageAction", "DO"), ("bridge", "THEN")]:
                if slide.get(key):
                    script += '<p class="cue"><strong>' + label + "</strong> " + escape(slide[key]) + "</p>"
            script += "".join("<p>" + escape(part) + "</p>" for part in slide.get("notes", "").split("\n\n"))
            if slide.get("sources"):
                links = [
                    '<a href="' + escape(url) + '">Source ' + str(index + 1) + "</a>"
                    for index, url in enumerate(slide["sources"])
                ]
                script += '<p class="source">' + " · ".join(links) + "</p>"
            script += "</section>"
            table += (
                "<tr><td>" + stamp + '</td><td><a href="' + link + '">'
                + str(number) + " · " + name + "</a></td><td>"
                + escape(slide.get("stageAction", "")) + "</td></tr>"
            )
        write(output, page(title + " · speaker script", script))
        overview += table + "</table>"
    write("presenter/run-of-show.html", page("Run of show", overview))
    print("Synchronized four presenter guides from show/content.js.")


if __name__ == "__main__":
    main()
