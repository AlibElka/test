import unittest
from calculator import add, subtract, multiply, divide


class TestCalculator(unittest.TestCase):

    # --- Сложение ---
    def test_add_positive(self):          # TC-001
        self.assertEqual(add(5, 3), 8)

    def test_add_zero(self):              # TC-002
        self.assertEqual(add(7, 0), 7)

    def test_add_negative(self):          # TC-003
        self.assertEqual(add(-5, -3), -8)

    def test_add_floats(self):            # TC-004
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)

    # --- Вычитание ---
    def test_subtract_positive(self):     # TC-005
        self.assertEqual(subtract(10, 3), 7)

    def test_subtract_negative_result(self):  # TC-006
        self.assertEqual(subtract(3, 10), -7)

    # --- Умножение ---
    def test_multiply(self):              # TC-007
        self.assertEqual(multiply(6, 7), 42)

    def test_multiply_by_zero(self):      # TC-008
        self.assertEqual(multiply(999, 0), 0)

    def test_multiply_negative(self):     # TC-009
        self.assertEqual(multiply(-4, 5), -20)

    # --- Деление ---
    def test_divide_exact(self):          # TC-010
        self.assertEqual(divide(20, 4), 5)

    def test_divide_float_result(self):   # TC-011
        self.assertAlmostEqual(divide(10, 3), 3.3333333333)

    def test_divide_by_zero(self):        # TC-012 — BUG-001
        with self.assertRaises(ValueError):
            divide(5, 0)

    # --- Граничные случаи ---
    def test_large_numbers(self):         # TC-013
        self.assertEqual(multiply(999999999, 999999999), 999999998000000001)

    def test_reset(self):                 # TC-014 (симуляция сброса)
        result = add(12345, 0) - 12345
        self.assertEqual(result, 0)

    def test_chain_operations(self):      # TC-015
        result = add(2, 3)
        result = multiply(result, 4)
        self.assertEqual(result, 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
