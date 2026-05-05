from sqlalchemy.exc import IntegrityError
from typing import TYPE_CHECKING

from app.common.enums.wallet_enums import WalletTypesEnum
from app.modules.wallets.contracts.dtos import FullWalletInfoDTO
from app.modules.wallets.service.utils import hash_pin, verify_pin
from app.modules.users.service.utils import verify_pass
from app.modules.users.exceptions import UserNotFoundError, UserPassNotVerifiedError

if TYPE_CHECKING:
    from app.database.models import UserModel
    from app.modules.wallets.uow.uow import WalletUnitOfWork


class CreateWalletService:
    """Сервис по созданию кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

    async def _create_wallet(self, pin: str, wallet_type: WalletTypesEnum, email: str, password: str) -> 'FullWalletInfoDTO':
        user: 'UserModel' = await self._wallet_uow.wallet_queries.select_user_by_email(email)

        if not user:
            raise UserNotFoundError('User not found')

        if not verify_pass(password, user.password_hash):
            raise UserPassNotVerifiedError('User password != password_hash')

        pin_hash = hash_pin(pin)

        try:
            wallet = await self._wallet_uow.wallet_commands.create_wallet(pin_hash, wallet_type, user)
        except IntegrityError:
            await self._wallet_uow.rollback()
            raise

        await self._wallet_uow.commit()

        return FullWalletInfoDTO.model_validate(wallet)

    async def create_credit_wallet(self, pin: str, email: str, password: str) -> 'FullWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.CREDIT, email, password)

    async def create_debit_wallet(self, pin: str, email: str, password: str) -> 'FullWalletInfoDTO':
        return await self._create_wallet(pin, WalletTypesEnum.DEBIT, email, password)


class UpdateWalletService:
    """Сервис по обновлению информации кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow


class DeleteWalletService:
    """Сервис по удалению кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow


class ManageWalletService:
    """Сервис по менедженгу кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow


class ShowWalletService:
    """Сервис по показу кошельков"""

    def __init__(self, wallet_uow: 'WalletUnitOfWork') -> None:
        self._wallet_uow = wallet_uow

