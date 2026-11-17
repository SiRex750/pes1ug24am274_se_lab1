import math


def _parse_number(text):
    """Convert text to a finite float, or return None if that is not possible."""
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None
    try:
        number = float(text)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(number):  # rejects 'nan', 'inf', '-inf'
        return None
    return number


def parse_declaration(text):
    """Parse 'category:value' -> (category, value), or None if invalid."""
    if not isinstance(text, str) or text.count(':') != 1:
        return None
    category, value = text.split(':')
    category = category.strip().lower()
    value = _parse_number(value)
    if not category or value is None or value < 0:
        return None
    return category, value


def duty_amount(text):
    """Compute duty from 'value@rate' (rate in percent), or None if invalid."""
    if not isinstance(text, str) or text.count('@') != 1:
        return None
    value, rate = text.split('@')
    value = _parse_number(value)
    rate = _parse_number(rate)
    if value is None or rate is None:
        return None
    if value < 0 or not 0 <= rate <= 100:
        return None
    duty = value * rate / 100
    if not math.isfinite(duty):
        return None
    return duty


def hs_chapter(code):
    """Return the HS chapter (1-97) from a code like '8517.12', or None if invalid."""
    if not isinstance(code, str):
        return None
    code = code.strip()
    if code.count('.') > 1:
        return None
    heading, _, subheading = code.partition('.')
    # only plain ASCII digits (str.isdigit alone also accepts '²', '٣', ...)
    if len(heading) < 2 or not (heading.isascii() and heading.isdigit()):
        return None
    if subheading and not (subheading.isascii() and subheading.isdigit()):
        return None
    chapter = int(heading[:2])
    if not 1 <= chapter <= 97:
        return None
    return chapter


def main():
    print("==== Running parse_declaration ====")
    user_input = input("Enter category:value (e.g. electronics:25000): ")
    result = parse_declaration(user_input)
    if result is None:
        print("Invalid declaration. Use the format category:value with a non-negative number.")
    else:
        print("Category and Value:", result)

    print("\n==== Running duty_amount ====")
    user_input = input("Enter value@rate (e.g. 25000@20): ")
    result = duty_amount(user_input)
    if result is None:
        print("Invalid input. Use value@rate with value >= 0 and rate between 0 and 100.")
    else:
        print("Duty Amount:", result)

    print("\n==== Running hs_chapter ====")
    user_input = input("Enter an HS code (e.g. 8517.12): ")
    result = hs_chapter(user_input)
    if result is None:
        print("Invalid HS code. Use digits like 8517.12 (chapter 01-97).")
    else:
        print("Chapter:", result)


if __name__ == "__main__":
    main()
