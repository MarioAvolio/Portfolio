"""SQLite persistence layer for completed competitive intelligence reports."""

import datetime
import json

from sqlalchemy import DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class _Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class _ReportRow(_Base):
    """ORM row representing one completed research report.

    Attributes:
        id: Auto-incremented primary key.
        job_id: UUID matching the in-memory JobStore entry.
        product: Product that was analysed.
        competitors: JSON-encoded list of competitor names.
        report: Full markdown report text.
        created_at: UTC timestamp of report completion.
    """

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    product: Mapped[str] = mapped_column(String(255), nullable=False)
    competitors: Mapped[str] = mapped_column(Text, nullable=False)
    report: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class ReportStore:
    """Async SQLAlchemy store for persisted SWOT reports."""

    def __init__(self, db_path: str = "market_sentinel.db") -> None:
        """Creates the async engine and session factory.

        Args:
            db_path: Filesystem path for the SQLite file.
        """
        url = f"sqlite+aiosqlite:///{db_path}"
        self._engine = create_async_engine(url, echo=False)
        self._session: async_sessionmaker[AsyncSession] = async_sessionmaker(self._engine, expire_on_commit=False)

    async def init(self) -> None:
        """Creates all tables if they do not already exist."""
        async with self._engine.begin() as conn:
            await conn.run_sync(_Base.metadata.create_all)

    async def save(self, job_id: str, product: str, competitors: list[str], report: str) -> None:
        """Persists a completed report to the database.

        Args:
            job_id: UUID of the completed job.
            product: Product that was analysed.
            competitors: List of competitor names.
            report: Markdown report text.
        """
        async with self._session() as session:
            row = _ReportRow(
                job_id=job_id,
                product=product,
                competitors=json.dumps(competitors),
                report=report,
                created_at=datetime.datetime.now(datetime.UTC),
            )
            session.add(row)
            await session.commit()

    async def list_recent(self, limit: int = 20) -> list[dict]:
        """Returns the most recently completed reports, newest first.

        Args:
            limit: Maximum number of rows to return.

        Returns:
            List of dicts with job_id, product, competitors, created_at.
        """
        async with self._session() as session:
            result = await session.execute(select(_ReportRow).order_by(_ReportRow.created_at.desc()).limit(limit))
            rows = result.scalars().all()
            return [
                {
                    "job_id": r.job_id,
                    "product": r.product,
                    "competitors": json.loads(r.competitors),
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
