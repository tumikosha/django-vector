from unittest import TestCase

from app.code.calculator import calculate_expression


class CalculatorTest(TestCase):

    def test_calculate_expression(self):
        have_error, result = calculate_expression("2+(1+1)")
        assert 4 == result

    def test_calculate_expression_div_zero(self):
        have_error, result = calculate_expression("2/0")
        assert result.find(" division by zero") > -1
        assert have_error

    def test_calculate_expression_bad1(self):
        have_error, result = calculate_expression("2+sun(2)")
        assert have_error

    def test_calculate_expression_bad2(self):
        have_error, result = calculate_expression("2+QQQQ")
        assert have_error
