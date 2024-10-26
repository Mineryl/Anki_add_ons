from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QAction
from aqt import gui_hooks
import datetime


def create_decks():
    """Create a parent deck with today's date and subdecks with specific naming pattern."""
    # Get today's date in YYYYMMDD format
    today = datetime.datetime.now()
    parent_deck_name = today.strftime("%Y-%m-%d")

    # Create or get the parent deck
    parent_deck_id = mw.col.decks.id(parent_deck_name)

    # Subdeck naming convention
    date_part = today.strftime("%y%m%d")
    content_parts = [
        "1.1", "1.2", "2", "3.1", "3.2", "4", "5", "6.1", "6.2", "7", "8", "9", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
        "24", "25", "26", "27", "28"
    ]

    # Create subdecks
    for content in content_parts:
        subdeck_name = f"{date_part}-{content}"
        full_deck_name = f"{parent_deck_name}::{subdeck_name}"
        mw.col.decks.id(full_deck_name)

    mw.reset()
    showInfo(f"成功创建父牌组 '{parent_deck_name}' 和所有子牌组。")

def setup_menu():
    action = QAction("自动生成牌组", mw)
    action.triggered.connect(create_decks)
    mw.form.menuTools.addAction(action)

gui_hooks.main_window_did_init.append(setup_menu)
