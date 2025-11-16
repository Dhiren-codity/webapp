import pytest
from unittest.mock import patch, mock_open
from cal import MyClass, calculate_area, print_area, read_file, calculate_average, overly_complex_function


@pytest.fixture
def myclass_instance():
    """Provide a MyClass instance with a standard integer value."""
    return MyClass(value=10)


@pytest.fixture
def myclass_zero_instance():
    """Provide a MyClass instance initialized with zero."""
    return MyClass(value=0)


@pytest.fixture
def myclass_float_instance():
    """Provide a MyClass instance initialized with a float."""
    return MyClass(value=1.5)


@pytest.fixture
def myclass_non_numeric_instance():
    """Provide a MyClass instance initialized with a non-numeric value to test errors."""
    return MyClass(value="not-a-number")


def test_myclass___init___valid_int():
    """Test MyClass initialization with a valid integer."""
    obj = MyClass(5)
    assert obj.value == 5


def test_myclass___init___negative_value():
    """Test MyClass initialization with a negative integer."""
    obj = MyClass(-3)
    assert obj.value == -3


def test_myclass___init___float_value():
    """Test MyClass initialization with a float."""
    obj = MyClass(2.75)
    assert obj.value == 2.75


def test_myclass_increment_increases_by_one(myclass_instance):
    """Test increment increases the value by exactly one."""
    myclass_instance.increment()
    assert myclass_instance.value == 11


def test_myclass_increment_multiple_calls(myclass_instance):
    """Test increment works across multiple sequential calls."""
    myclass_instance.increment()
    myclass_instance.increment()
    myclass_instance.increment()
    assert myclass_instance.value == 13


def test_myclass_increment_on_zero(myclass_zero_instance):
    """Test increment when starting from zero."""
    myclass_zero_instance.increment()
    assert myclass_zero_instance.value == 1


def test_myclass_increment_on_float(myclass_float_instance):
    """Test increment when the value is a float."""
    myclass_float_instance.increment()
    assert myclass_float_instance.value == 2.5


def test_myclass_increment_raises_type_error_on_non_numeric(myclass_non_numeric_instance):
    """Test increment raises TypeError when value is non-numeric."""
    with pytest.raises(TypeError):
        myclass_non_numeric_instance.increment()


def test_myclass_increment_large_integer():
    """Test increment handles very large integers correctly."""
    large = 10**18
    obj = MyClass(large)
    obj.increment()
    assert obj.value == large + 1


def test_calculate_area_with_integer_uses_bitwise_xor_behavior():
    """Test calculate_area returns result using bitwise XOR for integer radius."""
    # 3 ^ 2 == 1, so area should be 3.14 * 1 == 3.14
    result = calculate_area(3)
    assert result == 3.14


def test_calculate_area_raises_type_error_with_float_radius():
    """Test calculate_area raises TypeError when radius is a float (due to bitwise XOR)."""
    with pytest.raises(TypeError):
        calculate_area(3.0)


def test_print_area_calls_print_with_mocked_calculate_area():
    """Test print_area prints the correct string when calculate_area is mocked to return a string."""
    with patch('cal.calculate_area', return_value="42.0") as mock_calc, patch('builtins.print') as mock_print:
        print_area(7)
        mock_calc.assert_called_once_with(7)
        mock_print.assert_called_once_with("The area is: 42.0")


def test_print_area_raises_type_error_when_concatenating_string_and_float():
    """Test print_area raises TypeError when trying to concatenate str and float."""
    # For integer radius, calculate_area returns a float (e.g., 3.14), causing TypeError on concatenation
    with pytest.raises(TypeError):
        print_area(3)


def test_read_file_returns_content_and_uses_open():
    """Test read_file returns file content and uses open correctly."""
    mocked_content = "hello, world"
    m = mock_open(read_data=mocked_content)
    with patch('cal.open', m):
        result = read_file("dummy/path.txt")
        assert result == mocked_content
        m.assert_called_once_with("dummy/path.txt")


def test_read_file_propagates_file_not_found_error():
    """Test read_file propagates FileNotFoundError from open."""
    m = mock_open()
    m.side_effect = FileNotFoundError("not found")
    with patch('cal.open', m):
        with pytest.raises(FileNotFoundError):
            read_file("missing.txt")


def test_calculate_average_normal_list():
    """Test calculate_average returns the correct average for a normal list."""
    result = calculate_average([1, 2, 3, 4])
    assert result == 2.5


def test_calculate_average_empty_list_raises_zero_division():
    """Test calculate_average raises ZeroDivisionError for an empty list."""
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


def test_overly_complex_function_divisible_by_2_3_5():
    """Test overly_complex_function prints for number divisible by 2, 3, and 5."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(30)
        mock_print.assert_called_once_with("Divisible by 2, 3, and 5")


def test_overly_complex_function_divisible_by_2_and_3_not_5():
    """Test overly_complex_function prints for number divisible by 2 and 3 but not 5."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(6)
        mock_print.assert_called_once_with("Divisible by 2 and 3 but not 5")


def test_overly_complex_function_divisible_by_2_not_3():
    """Test overly_complex_function prints for number divisible by 2 but not by 3."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(8)
        mock_print.assert_called_once_with("Divisible by 2 but not by 3")


def test_overly_complex_function_odd_divisible_by_3():
    """Test overly_complex_function prints for odd number divisible by 3."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(9)
        mock_print.assert_called_once_with("Odd but divisible by 3")


def test_overly_complex_function_odd_divisible_by_5():
    """Test overly_complex_function prints for odd number divisible by 5."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(25)
        mock_print.assert_called_once_with("Odd and divisible by 5")


def test_overly_complex_function_odd_not_divisible_by_3_or_5():
    """Test overly_complex_function prints for odd number not divisible by 3 or 5."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(7)
        mock_print.assert_called_once_with("Odd and not divisible by 3 or 5")


def test_overly_complex_function_zero():
    """Test overly_complex_function prints for zero."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(0)
        mock_print.assert_called_once_with("Zero")


def test_overly_complex_function_negative_even():
    """Test overly_complex_function prints for negative even number."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(-4)
        mock_print.assert_called_once_with("Negative even number")


def test_overly_complex_function_negative_odd():
    """Test overly_complex_function prints for negative odd number."""
    with patch('builtins.print') as mock_print:
        overly_complex_function(-3)
        mock_print.assert_called_once_with("Negative odd number")