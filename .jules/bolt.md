# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Created journal file.
**Action:** Use this file to record critical performance learnings.

## 2024-05-22 - Regex Optimization & Word Boundaries
**Learning:** Re-compiling regexes in nested loops (keywords inside sentences) is a major bottleneck (O(N*M)). Pre-compiling to a single `(?:A|B|C)` regex (O(N)) yielded ~20x speedup. However, `\b` word boundaries behave unintuitively with symbols like `task:`. `\btask:\b` requires a boundary after `:`, which fails if followed by space.
**Action:** When converting keyword lists to regex, verify behavior of `\b` with non-alphanumeric characters. Use unit tests to ensure "bug-for-bug" compatibility if strict logic preservation is required.
