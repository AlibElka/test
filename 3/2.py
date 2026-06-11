import pytest
from functions import validate_password, divide


class TestValidatePassword:

    # позитив
    def test_valid_password_basic(self):
        assert validate_password("Abcde123") is True

    def test_valid_password_long(self):
        assert validate_password("SuperSecure999!") is True

    def test_valid_password_digits_and_letters(self):
        assert validate_password("hello1234") is True

    # нега
    def test_invalid_too_short(self):
        assert validate_password("Ab1") is False

    def test_invalid_no_digit(self):
        assert validate_password("AbcdefGH") is False

    def test_invalid_no_letter(self):
        assert validate_password("12345678") is False

    def test_invalid_has_space(self):
        assert validate_password("Abc 1234") is False

    # граничные
    def test_exactly_8_chars(self):
        assert validate_password("Abcde12!") is True

    def test_exactly_7_chars(self):
        assert validate_password("Abcde1!") is False

    def test_empty_string(self):
        assert validate_password("") is False

    # ошибочныеее
    def test_non_string_input_int(self):
        with pytest.raises(TypeError):
            validate_password(12345678)

    def test_non_string_input_none(self):
        with pytest.raises(TypeError):
            validate_password(None)

    # параметризованный
    @pytest.mark.parametrize("pwd, expected", [
        ("Abcde123",  True),   
        ("short1",    False),
        ("noooo000 ", False),
        ("NOODIGITS", False), 
        ("12345678",  False),
        ("Correct1!", True), 
    ])
    def test_parametrized_validate(self, pwd, expected):
        assert validate_password(pwd) is expected


class TestDivide:

    # позитивный
    def test_divide_int_positive(self):
        assert divide(10, 2) == 5.0

    def test_divide_float(self):
        assert divide(7.5, 2.5) == pytest.approx(3.0)

    def test_divide_int_and_float(self):
        assert divide(9, 4.5) == pytest.approx(2.0)

    def test_divide_negative(self):
        assert divide(-10, 2) == -5.0

    def test_divide_both_negative(self):
        assert divide(-6, -3) == pytest.approx(2.0)

    # граничные
    def test_divide_zero_numerator(self):
        assert divide(0, 5) == 0.0

    def test_divide_result_float(self):
        assert divide(1, 3) == pytest.approx(0.3333, rel=1e-3)

    # ошибочные данные
    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

    def test_divide_by_zero_float(self):
        with pytest.raises(ZeroDivisionError):
            divide(5, 0.0)

    def test_divide_string_argument(self):
        with pytest.raises(TypeError):
            divide("10", 2)

    def test_divide_none_argument(self):
        with pytest.raises(TypeError):
            divide(None, 2)

    # параметризованный
    @pytest.mark.parametrize("a, b, expected", [
        (10,   2,   5.0),
        (-10,  2,  -5.0),
        (0,    5,   0.0),
        (1,    4,   0.25),
        (7.5,  2.5, 3.0),
    ])
    def test_parametrized_divide(self, a, b, expected):
        assert divide(a, b) == pytest.approx(expected)