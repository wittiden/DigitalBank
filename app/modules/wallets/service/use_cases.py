from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError
from typing import TYPE_CHECKING, Any

from app.common.decorators import debug_log
from app.common.enums.wallet_enums import WalletTypesEnum
from app.modules.users.service.guards import UserGuards
from app.modules.wallets.contracts.dtos import FullWalletInfoDTO
from app.modules.wallets.contracts.dtos import SecurityWalletInfoDTO
from app.modules.wallets.exceptions import WalletCreateError, WalletPinsIsTheSame
from app.modules.wallets.service.guards import WalletGuards
from app.modules.wallets.service.utils import hash_pin, verify_pin

if TYPE_CHECKING:
    from app.database.models import WalletModel
    from app.database.models import UserModel
    from app.modules.wallets.repository.commands import WalletCommandsRepository
    from app.modules.wallets.repository.queries import WalletQueriesRepository


class CreateWalletService:
    """Сервис по созданию кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries

    async def _create_wallet(self, current_user: 'UserModel', pin: str, wallet_type: WalletTypesEnum) -> 'SecurityWalletInfoDTO':
        UserGuards.require_user_exists(current_user)

        wallets_count = await self._wallet_queries.select_wallets_count_by_user_id(current_user.user_id)
        WalletGuards.require_wallet_limit(wallets_count)

        pin_hash = hash_pin(pin)

        try:
            wallet = await self._wallet_commands.create_wallet(pin_hash, wallet_type, current_user.user_id)
        except IntegrityError:
            raise WalletCreateError('Error while wallet creating')

        logger.info(f'Кошелек {wallet.address} создан')
        return SecurityWalletInfoDTO.model_validate(wallet)

    @debug_log
    async def create_credit_wallet(self, current_user: 'UserModel', pin: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(current_user, pin, WalletTypesEnum.CREDIT)

    @debug_log
    async def create_debit_wallet(self, current_user: 'UserModel', pin: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(current_user, pin, WalletTypesEnum.DEBIT)


class UpdateWalletService:
    """Сервис по обновлению информации кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries

    @debug_log
    async def partial_update_my_wallet(self, current_user: 'UserModel', address: str, pin: str, data: dict[str, Any]) -> 'SecurityWalletInfoDTO':
        UserGuards.require_user_exists(current_user)

        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)
        WalletGuards.require_wallet_not_blocked(obj)

        if 'pin' in data.keys():
            pin_hash = hash_pin(data['pin'])

            if verify_pin(pin, pin_hash):
                raise WalletPinsIsTheSame('Wallet old_pin == new_pin')

            data.pop('pin')
            data['pin_hash'] = pin_hash

        for key, value in data.items():

            await self._wallet_commands.partial_update_wallet(obj, {key: value})

        logger.info(f'Информация кошелька {address} обновлена')
        return SecurityWalletInfoDTO.model_validate(obj)


class DeleteWalletService:
    """Сервис по удалению кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries

    @debug_log
    async def delete_wallet(self, current_user: 'UserModel', wallet_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)

        await self._wallet_commands.delete_wallet(obj)

        logger.info(f'Кошелек #{wallet_id} удален')

    @debug_log
    async def close_my_wallet(self, current_user: 'UserModel', address: str, pin: str) -> None:
        UserGuards.require_user_exists(current_user)

        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)

        await self._wallet_commands.delete_wallet(obj)

        logger.info(f'Кошелек {address} закрыт')


class ManageWalletService:
    """Сервис по менедженгу кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries

    @debug_log
    async def block_wallet(self, current_user: 'UserModel', wallet_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_wallet_not_already_blocked(obj)

        await self._wallet_commands.partial_update_wallet(obj, {'is_blocked': True})

        logger.info(f'Кошелек #{wallet_id} заблокирован')

    @debug_log
    async def unblock_wallet(self, current_user: 'UserModel', wallet_id: UUID) -> None:
        UserGuards.require_admin(current_user)

        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_wallet_not_already_unblocked(obj)

        await self._wallet_commands.partial_update_wallet(obj, {'is_blocked': False})

        logger.info(f'Кошелек #{wallet_id} разблокирован')


class ShowWalletService:
    """Сервис по показу кошельков"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_queries = wallet_queries

    @debug_log
    async def show_wallet_by_id(self, current_user: 'UserModel', wallet_id: UUID) -> 'FullWalletInfoDTO':
        UserGuards.require_admin(current_user)

        obj = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)

        return FullWalletInfoDTO.model_validate(obj)

    @debug_log
    async def show_wallets_by_user_id(self, current_user: 'UserModel', user_id: UUID) -> list['FullWalletInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._wallet_queries.select_wallets_by_user_id(user_id)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_wallets(self, current_user: 'UserModel', offset: int = 0, limit: int = 0) -> list['FullWalletInfoDTO']:
        UserGuards.require_admin(current_user)

        objs = await self._wallet_queries.select_wallets(offset, limit)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_my_wallets(self, current_user: 'UserModel',) -> list['SecurityWalletInfoDTO']:
        UserGuards.require_user_exists(current_user)

        objs = await self._wallet_queries.select_wallets_by_user_id(current_user.user_id)

        return [SecurityWalletInfoDTO.model_validate(obj) for obj in objs]
