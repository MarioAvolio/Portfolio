"""Read-only access to the gateway's in-memory call audit trail."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from gateway.webserver.dependency.deps import get_audit_store, require_api_key
from gateway.webserver.models.gateway import AuditEntry, AuditKind
from gateway.webserver.stores.audit_store import AuditStore

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditEntry], dependencies=[Depends(require_api_key)])
async def get_audit(
    store: Annotated[AuditStore, Depends(get_audit_store)],
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    service: Annotated[str | None, Query()] = None,
    kind: Annotated[AuditKind | None, Query()] = None,
) -> list[AuditEntry]:
    """Returns the most recently routed calls, newest first.

    ``limit`` bounds how many entries are returned after ``service``/``kind``
    are applied, not how many are scanned. A filter that matches nothing
    returns an empty list, not a 404 -- it is a query over the trail, not a
    lookup of a specific resource.

    Args:
        store: Injected audit store.
        limit: Maximum number of entries to return.
        service: If given, only entries for this service name.
        kind: If given, only entries of this call kind.

    Returns:
        Up to ``limit`` recent matching :class:`AuditEntry` records.
    """
    return store.recent(limit, service=service, kind=kind)
