"""Helpers that defang user-controlled values before they hit `logger.*`.

`safe_log` strips CR / LF / TAB so a request body can't forge fake log
lines, then truncates so a giant blob can't drown the journal.

Use with parameterized logging:

    logger.info("user.action user=%s op=%s", safe_log(uid), safe_log(op))
"""

from __future__ import annotations


def safe_log(value: object, max_len: int = 80) -> str:
    return (
        str(value)
        .replace("\r", "")
        .replace("\n", "")
        .replace("\t", " ")[:max_len]
    )
