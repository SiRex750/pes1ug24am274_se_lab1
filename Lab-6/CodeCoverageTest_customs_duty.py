"""Lab 6 - Code (line) coverage tests for customs_duty.py.

Goal: execute every line of customs_duty.py at least once.
Run:
    coverage run -m pytest CodeCoverageTest_customs_duty.py
    coverage report -m
"""
import pytest
from customs_duty import duty_rate, total_duty, clearance_channel


# ---------- starter tests ----------
def test_books_are_duty_free():
    assert duty_rate("books", "FTA") == 0


def test_low_value_personal_import():
    assert total_duty("books", 500, "US", False) == 0


# ---------- duty_rate ----------
def test_prohibited_category_raises():
    with pytest.raises(ValueError, match="prohibited item"):
        duty_rate("weapons", "US")


def test_electronics_from_fta_country():
    assert duty_rate("electronics", "FTA") == 0.10


def test_electronics_from_non_fta_country():
    assert duty_rate("electronics", "US") == 0.20


def test_clothing_from_fta_country():
    assert duty_rate("clothing", "FTA") == 0.05


def test_clothing_from_non_fta_country():
    assert duty_rate("clothing", "CN") == 0.12


def test_other_category_default_rate():
    assert duty_rate("toys", "US") == 0.15


# ---------- total_duty ----------
def test_negative_value_raises():
    with pytest.raises(ValueError, match="negative value"):
        total_duty("electronics", -1, "US", False)


def test_gift_within_allowance_is_free():
    assert total_duty("electronics", 4000, "US", True) == 0


def test_gift_above_allowance_small_duty_hits_minimum():
    # (5100 - 5000) * 0.15 = 15  -> raised to the 50 minimum
    assert total_duty("toys", 5100, "US", True) == 50


def test_commercial_import_regular_duty():
    # 10000 * 0.20 = 2000
    assert total_duty("electronics", 10000, "US", False) == pytest.approx(2000)


# ---------- clearance_channel ----------
def test_prohibited_goods_refused():
    assert clearance_channel(500, "narcotics", True) == "refuse"


def test_very_high_value_inspected():
    assert clearance_channel(150000, "electronics", True) == "inspect"


def test_high_value_without_documents_inspected():
    assert clearance_channel(25000, "clothing", False) == "inspect"


def test_normal_shipment_green():
    assert clearance_channel(5000, "books", True) == "green"
