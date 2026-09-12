from app.services.spec import (
    bookings_overlap,
    evaluate_assay_result,
    evaluate_discrete,
    evaluate_numeric,
    next_verdict_with_retest,
)


def test_numeric_inside():
    j = evaluate_numeric(2.5, lsl=2.2, usl=2.8)
    assert j.verdict == "pass"


def test_numeric_below_lsl():
    j = evaluate_numeric(2.0, lsl=2.2, usl=2.8)
    assert j.verdict == "fail"


def test_numeric_exclusive_upper():
    j = evaluate_numeric(10.0, lsl=None, usl=10.0, inclusive_upper=False)
    assert j.verdict == "fail"


def test_numeric_no_limits_invalid():
    j = evaluate_numeric(1.0, lsl=None, usl=None)
    assert j.verdict == "invalid"


def test_discrete_pass():
    j = evaluate_discrete("OK", {"OK", "PASS"})
    assert j.verdict == "pass"


def test_discrete_fail():
    j = evaluate_discrete("NG", {"OK", "PASS"})
    assert j.verdict == "fail"


def test_retest_then_fail():
    from app.services.spec import SpecJudgement

    fail = SpecJudgement("fail", "x")
    assert next_verdict_with_retest(fail, attempt=1, retest_limit=1) == "retest"
    assert next_verdict_with_retest(fail, attempt=2, retest_limit=1) == "fail"


def test_assay_result_numeric():
    j = evaluate_assay_result(
        spec_type="numeric",
        numeric_value=150,
        text_value=None,
        lsl=None,
        usl=200,
        inclusive_lower=True,
        inclusive_upper=True,
        discrete_pass=None,
    )
    assert j.verdict == "pass"


def test_booking_overlap():
    assert bookings_overlap(0, 100, 50, 150)
    assert not bookings_overlap(0, 100, 100, 200)
