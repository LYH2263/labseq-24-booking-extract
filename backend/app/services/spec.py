"""Specification evaluation engine for assay results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpecJudgement:
    verdict: str  # pass|fail|invalid
    reason: str


def evaluate_numeric(
    value: float,
    *,
    lsl: float | None,
    usl: float | None,
    inclusive_lower: bool = True,
    inclusive_upper: bool = True,
) -> SpecJudgement:
    """Evaluate a numeric measurement against optional lower/upper spec limits."""
    if lsl is None and usl is None:
        return SpecJudgement("invalid", "未配置规格限")

    if lsl is not None:
        ok_low = value >= lsl if inclusive_lower else value > lsl
        if not ok_low:
            op = "≥" if inclusive_lower else ">"
            return SpecJudgement("fail", f"低于下限（需 {op} {lsl}，实测 {value}）")

    if usl is not None:
        ok_high = value <= usl if inclusive_upper else value < usl
        if not ok_high:
            op = "≤" if inclusive_upper else "<"
            return SpecJudgement("fail", f"超过上限（需 {op} {usl}，实测 {value}）")

    return SpecJudgement("pass", "在规格限内")


def parse_discrete_pass(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {tok.strip() for tok in raw.split(",") if tok.strip()}


def evaluate_discrete(value: str, allowed: set[str]) -> SpecJudgement:
    if not allowed:
        return SpecJudgement("invalid", "未配置离散合格集")
    token = value.strip()
    if not token:
        return SpecJudgement("invalid", "空结果")
    if token in allowed:
        return SpecJudgement("pass", f"命中合格集 {sorted(allowed)}")
    return SpecJudgement("fail", f"「{token}」不在合格集 {sorted(allowed)}")


def evaluate_assay_result(
    *,
    spec_type: str,
    numeric_value: float | None,
    text_value: str | None,
    lsl: float | None,
    usl: float | None,
    inclusive_lower: bool,
    inclusive_upper: bool,
    discrete_pass: str | None,
) -> SpecJudgement:
    if spec_type == "numeric":
        if numeric_value is None:
            return SpecJudgement("invalid", "数值型检验缺少 numeric_value")
        return evaluate_numeric(
            numeric_value,
            lsl=lsl,
            usl=usl,
            inclusive_lower=inclusive_lower,
            inclusive_upper=inclusive_upper,
        )
    if spec_type == "discrete":
        return evaluate_discrete(text_value or "", parse_discrete_pass(discrete_pass))
    return SpecJudgement("invalid", f"未知 spec_type: {spec_type}")


def next_verdict_with_retest(
    judgement: SpecJudgement,
    *,
    attempt: int,
    retest_limit: int,
) -> str:
    """Map raw judgement to stored verdict, allowing retest while attempts remain.

    attempt is 1-based count of the result being recorded now.
    retest_limit is max extra attempts after the first failure (e.g. 1 => can fail once then retest).
    """
    if judgement.verdict == "invalid":
        return "invalid"
    if judgement.verdict == "pass":
        return "pass"
    # fail
    if attempt <= retest_limit:
        return "retest"
    return "fail"


def bookings_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    """Half-open [start, end) overlap for instrument bookings."""
    if a_end < a_start or b_end < b_start:
        raise ValueError("invalid booking interval")
    return a_start < b_end and b_start < a_end
