# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Created journal file.
**Action:** Use this file to record critical performance learnings.

## 2024-05-22 - Regex Optimization & Word Boundaries
**Learning:** Re-compiling regexes in nested loops (keywords inside sentences) is a major bottleneck (O(N*M)). Pre-compiling to a single `(?:A|B|C)` regex (O(N)) yielded ~20x speedup. However, `\b` word boundaries behave unintuitively with symbols like `task:`. `\btask:\b` requires a boundary after `:`, which fails if followed by space.
**Action:** When converting keyword lists to regex, verify behavior of `\b` with non-alphanumeric characters. Use unit tests to ensure "bug-for-bug" compatibility if strict logic preservation is required.

## 2024-05-22 - Regex Compilation & String Ops
**Learning:** Recompiling regexes for dynamic inputs (like user names) inside loops causes significant overhead. Using `functools.lru_cache` to cache compiled regexes gives ~2x speedup. Also, `regex.search` naturally fails on empty strings, making `if not s.strip():` checks redundant and costly (O(N) scan).
**Action:** Use `lru_cache` for dynamic regex factories. Trust regex to handle empty/whitespace strings instead of pre-stripping.
