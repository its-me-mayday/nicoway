from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from decimal import Decimal

Money = Decimal


@dataclass(frozen=True)
class TimeWindow:
    start: time
    end: time

    def contains(self, value: time) -> bool:
        if self.start <= self.end:
            return self.start <= value <= self.end
        return value >= self.start or value <= self.end
