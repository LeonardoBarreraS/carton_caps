from __future__ import annotations

from enum import Enum


class RuleType(str, Enum):
    ELIGIBILITY = "eligibility"
    BONUS = "bonus"
    INVITATION = "invitation"
    REQUIREMENT = "requirement"
