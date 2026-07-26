"""In-memory ring buffer of recently routed calls.

A record here costs nothing to lose and nothing to regenerate, unlike a paid
LLM report, so a bounded in-memory deque is preferred over a durable store at
this stage -- the gateway is deliberately stateless and the only consumer is
the console showing what the currently running hub has been doing.
"""

from collections import deque
from datetime import UTC, datetime
from itertools import islice

from gateway.webserver import request_id_ctx
from gateway.webserver.models.gateway import AuditEntry, AuditKind


class AuditStore:
    """Bounded, in-memory record of the gateway's recently routed calls."""

    def __init__(self, capacity: int) -> None:
        """Creates an empty store bounded to ``capacity`` entries.

        Args:
            capacity: Maximum number of entries kept; oldest are dropped first.
        """
        # Bounded in-memory only: history is lost on restart. Fine for now --
        # see the module docstring for why this isn't backed by SQLite yet.
        self._entries: deque[AuditEntry] = deque(maxlen=capacity)

    def record(self, service: str, kind: AuditKind, status_code: int, latency_ms: float) -> None:
        """Appends one entry. Synchronous: nothing here ever awaits or raises.

        Args:
            service: Name of the routed service.
            kind: Which routed call site produced this entry.
            status_code: HTTP status code returned by (or assumed for) the call.
            latency_ms: Wall-clock time spent waiting on the downstream call.
        """
        self._entries.append(
            AuditEntry(
                service=service,
                kind=kind,
                status_code=status_code,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
                request_id=request_id_ctx.get(),
            )
        )

    def recent(
        self, limit: int, service: str | None = None, kind: AuditKind | None = None
    ) -> list[AuditEntry]:
        """Returns up to ``limit`` matching entries, newest first.

        ``limit`` bounds the number of entries returned *after* filtering, not
        the number scanned -- ``recent(5, service="x")`` returns the 5 most
        recent entries for ``x``, however far back it has to look.

        Args:
            limit: Maximum number of entries to return.
            service: If given, only entries for this service name.
            kind: If given, only entries of this call kind.

        Returns:
            The most recently recorded matching entries, newest first.
        """
        matches = (
            entry
            for entry in reversed(self._entries)
            if (service is None or entry.service == service)
            and (kind is None or entry.kind == kind)
        )
        return list(islice(matches, limit))
