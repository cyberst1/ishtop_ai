from app.keyboards.main_menu import main_menu_kb
from app.keyboards.search import role_kb, job_card_kb, browsing_kb
from app.keyboards.profile import profile_kb
from app.keyboards.plans import plans_kb
from app.keyboards.bonus import earn_kb, bonus_channels_kb
from app.keyboards.coins import packages_kb
from app.keyboards.admin import admin_main_kb, admin_user_card_kb, admin_back_kb

__all__ = [
    "main_menu_kb", "role_kb", "job_card_kb", "browsing_kb",
    "profile_kb", "plans_kb", "earn_kb", "bonus_channels_kb",
    "packages_kb",
    "admin_main_kb", "admin_user_card_kb", "admin_back_kb",
]
