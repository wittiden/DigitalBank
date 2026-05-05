from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.wallet_enums import WalletTypesEnum
from app.database.models import UserModel, WalletModel
from app.modules.wallets.exceptions import InvalidFieldError


class WalletCommandsRepository:
    """Репозиторий для управления create, update, delete запросами для кошельков в бд"""

    def __init__(self, async_session: AsyncSession) -> None:
        self._async_session = async_session

    async def create_wallet(self, pin: str, wallet_type: WalletTypesEnum, user: 'UserModel') -> 'WalletModel':
        obj = WalletModel(pin_hash=pin, wallet_type=wallet_type, user_id=user.user_id)

        self._async_session.add(obj)
        await self._async_session.flush()

        return obj

    async def potion_update_wallet(self, wallet: 'WalletModel', data: dict[str, Any]) -> 'WalletModel':
        for key, value in data.items():
            if not hasattr(wallet, key):
                raise InvalidFieldError(f'Invalid field {key} error')

            setattr(wallet, key, value)

        await self._async_session.flush()

        return wallet

    async def delete_wallet(self, wallet: 'WalletModel') -> None:
        await self._async_session.delete(wallet)

        await self._async_session.flush()
