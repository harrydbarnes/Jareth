## 2026-01-20 - [DoS Prevention via Input Truncation]
**Vulnerability:** Lack of input length limits on email bodies allowed potentially massive strings (DoS risk) to be processed by regex engines.
**Learning:** Even local desktop apps need resource limits when processing external/untrusted data (emails) to prevent freezing or memory exhaustion.
**Prevention:** Enforce `MAX_BODY_LENGTH` truncation at the application entry point (before analysis) and log warnings when truncation occurs.
