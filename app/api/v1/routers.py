from app.api.v1.endpoints import health_router
from app.modules.auth.api.v1.endpoints import auth_router
from app.modules.balances.api.v1.endpoints import admin_balance_router, user_balance_router
from app.modules.operations.api.v1.endpoints import operation_router
from app.modules.transactions.api.v1.endpoints import admin_trn_router
from app.modules.users.api.v1.endpoints import admin_router, user_router
from app.modules.wallets.api.v1.endpoints import admin_wallet_router, user_wallet_router

routers = [
    health_router,
    auth_router,
    user_router,
    admin_router,
    user_wallet_router,
    admin_wallet_router,
    user_balance_router,
    admin_balance_router,
    admin_trn_router,
    operation_router,
]
