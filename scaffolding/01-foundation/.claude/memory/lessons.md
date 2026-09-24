# Lessons Learned

Living document. Updated after ANY correction. Review at session start.

**Supersede, don't delete.** Entries are never edited away. When a newer lesson contradicts an older one, the old entry gains a `superseded_by: L-NNN (YYYY-MM-DD)` marker as its first body line and the new entry carries `supersedes: L-NNN` — surfacing (`lib/memory.sh`) then skips the old one.

Each lesson is one level-two Markdown heading made of its ID, an em dash and a short title (for example L-001 followed by the title), and then its body:

- **Context:** what was happening.
- **What I did wrong:** the concrete action or assumption.
- **What I should have done:** the correct alternative.
- **Rule:** the generalized lesson that applies in the future.

Write the rule so it works outside the specific incident. "Never do X against live without Y" is better than "at Task 0 I ran the wrong command".

IDs are allocated as one more than the highest existing ID (L-001 for an empty file), compared numerically and never reused. New lessons are appended at the end, oldest first. Record them with `/li:learn` (`bin/li-lessons.py`) so allocation and the conditional write stay mechanical.

---

<!-- New lessons are appended below this line, oldest first. -->
