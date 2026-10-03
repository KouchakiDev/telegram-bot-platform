from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import UserIdentity
from app.infrastructure.db.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, identity: UserIdentity) -> UserModel:
        result = await self.session.execute(select(UserModel).where(UserModel.telegram_id == identity.telegram_id))
        model = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if model is None:
            model = UserModel(
                telegram_id=identity.telegram_id,
                username=identity.username,
                first_name=identity.first_name,
                last_name=identity.last_name,
                language_code=identity.language_code,
                is_bot=identity.is_bot,
                last_seen_at=now,
            )
            self.session.add(model)
        else:
            model.username = identity.username
            model.first_name = identity.first_name
            model.last_name = identity.last_name
            model.language_code = identity.language_code
            model.is_bot = identity.is_bot
            model.last_seen_at = now
        await self.session.flush()
        return model

    async def get_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def active_telegram_ids(self, limit: int | None = None) -> list[int]:
        stmt = select(UserModel.telegram_id).where(UserModel.is_blocked.is_(False)).order_by(UserModel.id)
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars())
