from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError
from typing import TYPE_CHECKING, Any

from app.common.decorators import debug_log
from app.common.enums.wallet_enums import WalletTypesEnum
from app.modules.users.service.guards import UserGuards
from app.modules.wallets.contracts.dtos import FullWalletInfoDTO
from app.modules.wallets.contracts.dtos import SecurityWalletInfoDTO
from app.modules.wallets.exceptions import WalletCreateError, InvalidFieldError, WalletPinsIsTheSame
from app.modules.wallets.service.guards import WalletGuards
from app.modules.wallets.service.utils import hash_pin, verify_pin

if TYPE_CHECKING:
    from app.database.models import WalletModel
    from app.database.models import UserModel
    from app.modules.users.repository.queries import UserQueriesRepository
    from app.modules.wallets.repository.commands import WalletCommandsRepository
    from app.modules.wallets.repository.queries import WalletQueriesRepository


class CreateWalletService:
    """Сервис по созданию кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository', user_queries: 'UserQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries
        self._user_queries = user_queries

    async def _create_wallet(self, pin: str, wallet_type: WalletTypesEnum, email: str, password: str) -> 'SecurityWalletInfoDTO':
        user: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(user)
        UserGuards.require_user_not_blocked(user)
        UserGuards.require_verify_pass(password, user.password_hash)

        wallets_count = await self._wallet_queries.select_wallets_count_by_user_id(user.user_id)
        WalletGuards.require_wallet_limit(wallets_count)

        pin_hash = hash_pin(pin)

        try:
            wallet = await self._wallet_commands.create_wallet(pin_hash, wallet_type, user.user_id)
        except IntegrityError:
            raise WalletCreateError('Error while wallet creating')

        logger.info(f'Кошелек {wallet.address} создан')
        return SecurityWalletInfoDTO.model_validate(wallet)

    @debug_log
    async def create_credit_wallet(self, pin: str, email: str, password: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.CREDIT, email, password)

    @debug_log
    async def create_debit_wallet(self, pin: str, email: str, password: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.DEBIT, email, password)


class UpdateWalletService:
    """Сервис по обновлению информации кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository', user_queries: 'UserQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries
        self._user_queries = user_queries

    @debug_log
    async def partial_update_wallet(self, address: str, pin: str, data: dict[str, Any]) -> 'SecurityWalletInfoDTO':
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

        whitelist = ['pin_hash']

        for key, value in data.items():
            if key not in whitelist:
                raise InvalidFieldError(f'Invalid field {key} error')

            await self._wallet_commands.partial_update_wallet(obj, {key: value})

        logger.info(f'Информация кошелька {address} обновлена')
        return SecurityWalletInfoDTO.model_validate(obj)

    async def update_wallet_user(self, address: str, pin: str, old_email: str, old_password: str, new_email: str, new_password: str) -> 'FullWalletInfoDTO':
        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_address(address)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_verify_pin(pin, obj.pin_hash)

        old_user: 'UserModel' = await self._user_queries.select_user_by_email(old_email)

        UserGuards.require_user_exists(old_user)
        UserGuards.require_user_not_blocked(old_user)
        UserGuards.require_verify_pass(old_password, old_user.password_hash)

        new_user: 'UserModel' = await self._user_queries.select_user_by_email(new_email)

        UserGuards.require_user_exists(new_user)
        UserGuards.require_user_not_blocked(new_user)
        UserGuards.require_verify_pass(new_password, new_user.password_hash)

        await self._wallet_commands.partial_update_wallet(obj, {'user_id': new_user.user_id})

        wallets_count = await self._wallet_queries.select_wallets_count_by_user_id(new_user.user_id)
        WalletGuards.require_wallet_limit(wallets_count)

        logger.info(f'Владелец кошелька {address} обновлен')
        return FullWalletInfoDTO.model_validate(obj)


class DeleteWalletService:
    """Сервис по удалению кошельков"""

    def __init__(self, wallet_commands: 'WalletCommandsRepository', wallet_queries: 'WalletQueriesRepository') -> None:
        self._wallet_commands = wallet_commands
        self._wallet_queries = wallet_queries

    @debug_log
    async def delete_wallet(self, wallet_id: UUID) -> None:
        obj = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)

        await self._wallet_commands.delete_wallet(obj)

        logger.info(f'Кошелек #{wallet_id} удален')

    @debug_log
    async def close_wallet(self, address: str, pin: str) -> None:
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
    async def block_wallet(self, wallet_id: UUID) -> None:
        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_wallet_not_blocked(obj)

        await self._wallet_commands.partial_update_wallet(obj, {'is_blocked': True})

        logger.info(f'Кошелек #{wallet_id} заблокирован')

    @debug_log
    async def unblock_wallet(self, wallet_id: UUID) -> None:
        obj: 'WalletModel' = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)
        WalletGuards.require_wallet_not_unblocked(obj)

        await self._wallet_commands.partial_update_wallet(obj, {'is_blocked': False})

        logger.info(f'Кошелек #{wallet_id} разблокирован')


class ShowWalletService:
    """Сервис по показу кошельков"""

    def __init__(self, wallet_queries: 'WalletQueriesRepository', user_queries: 'UserQueriesRepository') -> None:
        self._wallet_queries = wallet_queries
        self._user_queries = user_queries

    @debug_log
    async def show_wallet_by_id(self, wallet_id: UUID) -> 'FullWalletInfoDTO':
        obj = await self._wallet_queries.select_wallet_by_id(wallet_id)

        WalletGuards.require_wallet_exists(obj)

        return FullWalletInfoDTO.model_validate(obj)

    @debug_log
    async def show_wallets_by_user_id(self, user_id: UUID) -> list['FullWalletInfoDTO']:
        objs = await self._wallet_queries.select_wallets_by_user_id(user_id)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_wallets(self, offset: int = 0, limit: int = 0) -> list['FullWalletInfoDTO']:
        objs = await self._wallet_queries.select_wallets(offset, limit)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    @debug_log
    async def show_my_wallets(self, email: str, password: str) -> list['SecurityWalletInfoDTO']:
        user: 'UserModel' = await self._user_queries.select_user_by_email(email)

        UserGuards.require_user_exists(user)
        UserGuards.require_verify_pass(password, user.password_hash)

        objs = await self._wallet_queries.select_wallets_by_user_id(user.user_id)

        return [SecurityWalletInfoDTO.model_validate(obj) for obj in objs]
