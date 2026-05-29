from app.database.repositories.users import UsersRepo
from app.database.repositories.jobs import JobsRepo
from app.database.repositories.searches import SearchesRepo
from app.database.repositories.referrals import ReferralsRepo
from app.database.repositories.subscriptions import SubscriptionsRepo
from app.database.repositories.bonus_channels import BonusRepo
from app.database.repositories.admin_logs import AdminLogsRepo
from app.database.repositories.blocks import BlocksRepo
from app.database.repositories.coin_purchases import CoinPurchasesRepo

__all__ = [
    "UsersRepo", "JobsRepo", "SearchesRepo", "ReferralsRepo",
    "SubscriptionsRepo", "BonusRepo", "AdminLogsRepo", "BlocksRepo",
    "CoinPurchasesRepo",
]
