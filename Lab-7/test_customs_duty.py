import math

from hypothesis import given, strategies as st
from customs_duty import parse_declaration, duty_amount, hs_chapter


# ---------------------------------------------------------------------------
# 1. "No crash" fuzz tests: any text (or None) must never raise an exception.
#    Invalid input should be rejected gracefully (the function returns None).
# ---------------------------------------------------------------------------

@given(st.text() | st.none())
def test_parse_declaration_no_crash(s):
    try:
        parse_declaration(s)
    except Exception as e:
        assert False, f"parse_declaration crashed on {s!r} with: {e!r}"


@given(st.text() | st.none())
def test_duty_amount_no_crash(s):
    try:
        duty_amount(s)
    except Exception as e:
        assert False, f"duty_amount crashed on {s!r} with: {e!r}"


@given(st.text() | st.none())
def test_hs_chapter_no_crash(s):
    try:
        hs_chapter(s)
    except Exception as e:
        assert False, f"hs_chapter crashed on {s!r} with: {e!r}"


# ---------------------------------------------------------------------------
# 2. Inputs shaped like the real format, so the fuzzer gets past split()
#    and stresses the number parsing (nan, inf, negatives, extra separators).
# ---------------------------------------------------------------------------

@given(st.text(), st.text())
def test_parse_declaration_structured_no_crash(category, value):
    try:
        parse_declaration(f"{category}:{value}")
    except Exception as e:
        assert False, f"parse_declaration crashed on {category!r}:{value!r} with: {e!r}"


@given(st.text(), st.text())
def test_duty_amount_structured_no_crash(value, rate):
    try:
        duty_amount(f"{value}@{rate}")
    except Exception as e:
        assert False, f"duty_amount crashed on {value!r}@{rate!r} with: {e!r}"


@given(st.text(alphabet="0123456789.", max_size=12))
def test_hs_chapter_digit_strings_no_crash(code):
    try:
        hs_chapter(code)
    except Exception as e:
        assert False, f"hs_chapter crashed on {code!r} with: {e!r}"


# ---------------------------------------------------------------------------
# 3. Output properties: whatever the input, a result that is returned must be
#    sensible (finite, non-negative values; HS chapter in the valid 1-97 range).
# ---------------------------------------------------------------------------

@given(st.text(), st.floats(allow_nan=True, allow_infinity=True))
def test_parse_declaration_output_is_valid(category, value):
    try:
        result = parse_declaration(f"{category}:{value}")
    except Exception:
        return  # crashes are reported by the no-crash tests above
    if result is not None:
        cat, val = result
        assert cat != "", "empty category accepted"
        assert math.isfinite(val) and val >= 0, f"invalid value accepted: {val}"


@given(st.floats(allow_nan=True, allow_infinity=True),
       st.floats(allow_nan=True, allow_infinity=True))
def test_duty_amount_output_is_valid(value, rate):
    try:
        result = duty_amount(f"{value}@{rate}")
    except Exception:
        return
    if result is not None:
        assert math.isfinite(result) and result >= 0, f"invalid duty: {result}"
        assert result <= value, "duty cannot exceed the goods value"


@given(st.integers(min_value=0, max_value=99999))
def test_hs_chapter_output_is_valid(n):
    code = f"{n}.10"
    try:
        result = hs_chapter(code)
    except Exception:
        return
    if result is not None:
        assert 1 <= result <= 97, f"chapter out of range for {code!r}: {result}"


# ---------------------------------------------------------------------------
# 4. Correctness on valid input: the hardened code must still work.
# ---------------------------------------------------------------------------

@given(st.sampled_from(["electronics", "Clothing", " BOOKS ", "toys"]),
       st.integers(min_value=0, max_value=10**9))
def test_parse_declaration_valid_roundtrip(category, value):
    assert parse_declaration(f"{category}:{value}") == (category.strip().lower(), float(value))


@given(st.integers(min_value=0, max_value=10**7), st.integers(min_value=0, max_value=100))
def test_duty_amount_valid(value, rate):
    assert math.isclose(duty_amount(f"{value}@{rate}"), value * rate / 100)


@given(st.integers(min_value=1, max_value=97), st.integers(min_value=0, max_value=99))
def test_hs_chapter_valid(chapter, heading):
    assert hs_chapter(f"{chapter:02d}{heading:02d}.12") == chapter
