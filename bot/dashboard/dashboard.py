from typing import Any

import dachshund

from bot.dashboard.pages.activity import activity_page
from bot.dashboard.pages.overview import overview_page
from bot.dashboard.storage import SQLModelStorage


def init_dachshund(event_store: str) -> None:
    """Stop any previous run and (re)open the dashboard's storage."""
    dachshund.shutdown()
    dachshund.default(path=event_store, storage=SQLModelStorage())


def build_dashboard() -> None:
    for page in (overview_page, activity_page):
        dachshund.include(page)


def start_dashboard(**options: Any) -> None:
    """Start dachshund, with `options` (`host`, `port`, ...) passed to `init`."""
    dachshund.init(
        "Ada",
        description="Code Society's Matrix bot",
        timezone="America/New_York",
        **options,
    )
