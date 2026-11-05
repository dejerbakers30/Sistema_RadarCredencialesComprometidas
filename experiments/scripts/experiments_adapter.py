"""Import-safe adapter shared by experiment scripts."""

from __future__ import annotations


class SnapshotHIBP:
    def __init__(self, breaches: dict[str, list[str]], catalogue: list[dict]):
        self.breaches = breaches
        self.catalogue = catalogue
        self.base_url = "https://haveibeenpwned.com/api/v3"

    async def breached_domain(self, _domain: str) -> dict[str, list[str]]:
        return self.breaches

    async def all_breaches(self) -> list[dict]:
        return self.catalogue
