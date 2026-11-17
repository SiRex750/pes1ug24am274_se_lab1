"""Lab 6 - Branch coverage tests for customs_duty.py.

Goal: make every decision (if / elif / compound condition) evaluate to
both True and False, including the boundary values.
Run:
    coverage run --branch -m pytest BranchCoverageTest_customs_duty.py
    coverage report -m
"""
import pytest
from customs_duty import duty_rate, total_duty, clearance_channel, PROHIBITED


# ======================= duty_rate =======================
# Decisions: category in PROHIBITED / == electronics / origin == FTA /
#            == clothing / origin == FTA / == books

@pytest.mark.parametrize("category", sorted(PROHIBITED))
def test_duty_rate_prohibited_true(category):
    with pytest.raises(ValueError, match="prohibited item"):
        duty_rate(category, "FTA")


@pytest.mark.parametrize(
    "category, origin, expected",
    [
        ("electronics", "FTA", 0.10),  # electronics T, FTA T
        ("electronics", "US", 0.20),   # electronics T, FTA F
        ("clothing", "FTA", 0.05),     # clothing T, FTA T
        ("clothing", "CN", 0.12),      # clothing T, FTA F
        ("books", "FTA", 0),           # books T
        ("books", "US", 0),            # books T (origin irrelevant)
        ("toys", "FTA", 0.15),         # all category checks F -> default
        ("furniture", "UK", 0.15),
    ],
)
def test_duty_rate_all_branches(category, origin, expected):
    assert duty_rate(category, origin) == expected


def test_duty_rate_is_case_sensitive():
    # "Electronics" does not match "electronics" -> default rate
    assert duty_rate("Electronics", "FTA") == 0.15


# ======================= total_duty =======================
# Decisions: value < 0 / is_gift / value <= 5000 / value <= 1000 /
#            0 < duty < 50

def test_total_duty_negative_value_raises():
    with pytest.raises(ValueError, match="negative value"):
        total_duty("books", -0.01, "US", False)


def test_total_duty_zero_value_not_negative():
    # value < 0 False at the boundary 0, non-gift and <= 1000 -> free
    assert total_duty("electronics", 0, "US", False) == 0


# --- gift branch ---
def test_gift_at_allowance_boundary_is_free():
    assert total_duty("electronics", 5000, "US", True) == 0


def test_gift_just_above_allowance_gets_minimum_duty():
    # (5001 - 5000) * 0.20 = 0.2  -> 0 < duty < 50 True -> 50
    assert total_duty("electronics", 5001, "US", True) == 50


def test_gift_large_value_only_excess_is_taxed():
    # (15000 - 5000) * 0.20 = 2000  -> minimum rule False
    assert total_duty("electronics", 15000, "US", True) == pytest.approx(2000)


def test_gift_books_above_allowance_zero_duty():
    # duty = 0 -> 0 < duty is False -> stays 0
    assert total_duty("books", 9000, "US", True) == 0


def test_gift_prohibited_above_allowance_raises():
    with pytest.raises(ValueError, match="prohibited item"):
        total_duty("weapons", 6000, "US", True)


# --- non-gift branch ---
def test_non_gift_at_personal_threshold_is_free():
    assert total_duty("electronics", 1000, "US", False) == 0


def test_non_gift_just_above_threshold_minimum_duty():
    # 1001 * 0.05 = 50.05 -> not < 50, keep computed duty
    assert total_duty("clothing", 1001, "FTA", False) == pytest.approx(50.05)


def test_duty_exactly_at_minimum_is_unchanged():
    # (6000 - 5000) * 0.05 = 50 -> 0 < 50 < 50 is False -> stays 50
    assert total_duty("clothing", 6000, "FTA", True) == pytest.approx(50)


def test_non_gift_books_over_threshold_zero_duty():
    # duty 0 -> minimum not applied
    assert total_duty("books", 50000, "US", False) == 0


def test_non_gift_regular_duty():
    assert total_duty("toys", 2000, "US", False) == pytest.approx(300)


def test_non_gift_prohibited_raises():
    with pytest.raises(ValueError, match="prohibited item"):
        total_duty("narcotics", 2000, "US", False)


# ======================= clearance_channel =======================
# Decisions: category in PROHIBITED / value > 100000 /
#            value > 20000 and not has_documents (both operands)

def test_clearance_prohibited_refused_even_with_documents():
    assert clearance_channel(10, "weapons", True) == "refuse"


def test_clearance_above_100000_inspected_even_with_documents():
    assert clearance_channel(100001, "electronics", True) == "inspect"


def test_clearance_exactly_100000_with_documents_green():
    assert clearance_channel(100000, "electronics", True) == "green"


def test_clearance_over_20000_without_documents_inspected():
    assert clearance_channel(20001, "clothing", False) == "inspect"


def test_clearance_over_20000_with_documents_green():
    assert clearance_channel(50000, "clothing", True) == "green"


def test_clearance_exactly_20000_without_documents_green():
    # value > 20000 False -> short-circuit, documents not checked
    assert clearance_channel(20000, "books", False) == "green"


def test_clearance_low_value_without_documents_green():
    assert clearance_channel(500, "toys", False) == "green"
