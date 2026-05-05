from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError
from typing import TYPE_CHECKING, Any

from app.common.enums.wallet_enums import WalletTypesEnum
from app.modules.wallets.contracts.dtos import FullWalletInfoDTO
from app.modules.wallets.contracts.dtos import SecurityWalletInfoDTO
from app.modules.wallets.exceptions import WalletCreateError, WalletNotFoundError, WalletIsBlockedError, \
    WalletIsNotBlockedError, WalletPinNotVerifiedError, InvalidFieldError, WalletLimitError
from app.modules.wallets.service.utils import hash_pin, verify_pin
from app.modules.users.service.utils import verify_pass
from app.modules.users.exceptions import UserNotFoundError, UserPassNotVerifiedError, UserIsBlockedError

if TYPE_CHECKING:
    from app.database.models import WalletModel
    from app.database.models import UserModel
    from app.modules.wallets.uow.uow import WalletUnitOfWork
    from app.modules.wallets.uow.uow import AccountUnitOfWork


class CreateWalletService:
    """Сервис по созданию кошельков"""

    def __init__(self, account_uow: 'AccountUnitOfWork') -> None:
        self._account_uow = account_uow

    async def _create_wallet(self, pin: str, wallet_type: WalletTypesEnum, email: str, password: str) -> 'SecurityWalletInfoDTO':
        user: 'UserModel' = await self._account_uow.user_queries.select_user_by_email(email)

        if not user:
            raise UserNotFoundError('User not found')

        if user.is_blocked:
            raise UserIsBlockedError('User is blocked')

        wallets_count = await self._account_uow.wallet_queries.select_wallets_count_by_user_id(user.user_id)
        if wallets_count >= 6:
            raise WalletLimitError('Wallet limit error (max limit = 5)')

        if not verify_pass(password, user.password_hash):
            raise UserPassNotVerifiedError('User password != password_hash')

        pin_hash = hash_pin(pin)

        try:
            wallet = await self._account_uow.wallet_commands.create_wallet(pin_hash, wallet_type, user.user_id)
        except IntegrityError:
            await self._account_uow.rollback()
            raise WalletCreateError('Error while wallet creating')

        await self._account_uow.commit()

        logger.info(f'Кошелек {wallet.address} создан')
        return SecurityWalletInfoDTO.model_validate(wallet)

    async def create_credit_wallet(self, pin: str, email: str, password: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.CREDIT, email, password)

    async def create_debit_wallet(self, pin: str, email: str, password: str) -> 'SecurityWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.DEBIT, email, password)


class UpdateWalletService:
    """Сервис по обновлению информации кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

    async def partial_update_wallet(self, address: str, pin: str, data: dict[str, Any]) -> 'SecurityWalletInfoDTO':
        obj = await self._wallet_uow.wallet_queries.select_wallet_by_address(address)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        if not verify_pin(pin, obj.pin_hash):
            raise WalletPinNotVerifiedError('Wallet pin not verified')

        whitelist = ['pin_hash', 'user_id']

        for key, value in data.items():
            if key not in whitelist:
                raise InvalidFieldError(f'Invalid field {key} error')

            setattr(obj, key, value)

        await self._wallet_uow.commit()

        logger.info(f'Информация кошелька {address} обновлена')
        return SecurityWalletInfoDTO.model_validate(obj)


class DeleteWalletService:
    """Сервис по удалению кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

    async def delete_wallet(self, wallet_id: UUID) -> None:
        obj = await self._wallet_uow.wallet_queries.select_wallet_by_id(wallet_id)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        await self._wallet_uow.wallet_commands.delete_wallet(obj)

        await self._wallet_uow.commit()
        logger.info(f'Кошелек #{wallet_id} удален')

    async def close_wallet(self, address: str, pin: str) -> None:
        obj = await self._wallet_uow.wallet_queries.select_wallet_by_address(address)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        if not verify_pin(pin, obj.pin_hash):
            raise WalletPinNotVerifiedError('Wallet pin not verified')

        await self._wallet_uow.wallet_commands.delete_wallet(obj)

        await self._wallet_uow.commit()
        logger.info(f'Кошелек {address} закрыт')


class ManageWalletService:
    """Сервис по менедженгу кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

    async def block_wallet(self, wallet_id: UUID) -> None:
        obj: 'WalletModel' = await self._wallet_uow.wallet_queries.select_wallet_by_id(wallet_id)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        if obj.is_blocked:
            raise WalletIsBlockedError('Wallet already blocked')

        await self._wallet_uow.wallet_commands.partial_update_wallet(obj, {'is_blocked': True})

        await self._wallet_uow.commit()
        logger.info(f'Кошелек #{wallet_id} заблокирован')

    async def unblock_wallet(self, wallet_id: UUID) -> None:
        obj: 'WalletModel' = await self._wallet_uow.wallet_queries.select_wallet_by_id(wallet_id)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        if not obj.is_blocked:
            raise WalletIsNotBlockedError('Wallet already unblocked')

        await self._wallet_uow.wallet_commands.partial_update_wallet(obj, {'is_blocked': False})

        await self._wallet_uow.commit()
        logger.info(f'Кошелек #{wallet_id} разблокирован')


class ShowWalletService:
    """Сервис по показу кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

    async def show_wallet_by_id(self, wallet_id: UUID) -> 'FullWalletInfoDTO':
        obj = await self._wallet_uow.wallet_queries.select_wallet_by_id(wallet_id)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        return FullWalletInfoDTO.model_validate(obj)

    async def show_wallets_by_user_id(self, user_id: UUID) -> list['FullWalletInfoDTO']:
        objs = await self._wallet_uow.wallet_queries.select_wallets_by_user_id(user_id)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    async def show_wallets(self, offset: int = 0, limit: int = 0) -> list['FullWalletInfoDTO']:
        objs = await self._wallet_uow.wallet_queries.select_wallets(offset, limit)

        return [FullWalletInfoDTO.model_validate(obj) for obj in objs]

    async def show_wallet_by_address(self, address: str, pin: str) -> 'SecurityWalletInfoDTO':
        obj = await self._wallet_uow.wallet_queries.select_wallet_by_address(address)

        if not obj:
            raise WalletNotFoundError('Wallet not found')

        if not verify_pin(pin, obj.pin_hash):
            raise WalletPinNotVerifiedError('Wallet pin not verified')

        return SecurityWalletInfoDTO.model_validate(obj)