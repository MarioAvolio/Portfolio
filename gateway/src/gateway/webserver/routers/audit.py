"""Read-only access to the gateway's in-memory call audit trail."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from gateway.webserver.dependency.deps import get_audit_store, require_api_key
from gateway.webserver.models.gateway import AuditEntry
from gateway.webserver.stores.audit_store import AuditStore

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditEntry], dependencies=[Depends(require_api_key)])
async def get_audit(
    store: Annotated[AuditStore, Depends(get_audit_store)],
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
) -> list[AuditEntry]:
    """Returns the most recently routed calls, newest first.

    Args:
        store: Injected audit store.
        limit: Maximum number of entries to return.

    Returns:
        Up to ``limit`` recent :class:`AuditEntry` records.
    """
    return store.recent(limit)
