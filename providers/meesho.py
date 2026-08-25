from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Product:
    product_id: str
    title: str
    price_inr: float
    commission_percent: float
    product_url: str
    image_urls: list[str]
    description: str = ""


class ProductProvider(Protocol):
    def list_products(self) -> list[Product]: ...


class MeeshoProvider:
    """Adapter boundary for an officially permitted Meesho data source.

    This intentionally does not automate Meesho login, scrape private pages,
    or call undocumented endpoints. Connect an authorized feed/export/API here.
    """

    def __init__(self, enabled: bool = False, feed_url: str = "") -> None:
        self.enabled = enabled
        self.feed_url = feed_url

    def list_products(self) -> list[Product]:
        if not self.enabled:
            return []
        if not self.feed_url:
            raise RuntimeError("Meesho provider is enabled but no authorized feed URL is configured")
        raise NotImplementedError("Connect an officially permitted Meesho product feed/API here")
