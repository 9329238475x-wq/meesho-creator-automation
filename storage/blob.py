from __future__ import annotations

from pathlib import Path


class Storage:
    """Optional local storage abstraction.

    Replace this class later with S3/R2/GCS/etc. without changing pipeline code.
    """

    def __init__(self, root: str = "output"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, filename: str) -> Path:
        return self.root / filename
