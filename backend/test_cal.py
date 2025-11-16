import pytest
from unittest.mock import patch, mock_open
from cal import MyClass, read_file, calculate_average, print_area, calculate_area, overly_complex_function


@pytest.fixture
def myclass_instance():
    """Create a MyClass instance with an initial integer value for testing."""
    return MyClass(10)


def test_myclass___init___sets_value():
    """Test MyClass initialization sets the provided value."""
    obj = MyClass(5)
    assert obj.value == 5


def test_myclass_increment_mutates_value(myclass_instance):
    """Test that increment increases value by 1 and returns None."""
    before = myclass_instance.value
    result = myclass_instance.increment()
    assert result is None
    assert myclass_instance.value == before + 1


def test_myclass_increment_multiple_times(myclass_instance):
    """Test that multiple increments compound correctly."""
    myclass_instance.increment()
    myclass_instance.increment()
    myclass_instance.increment()
    assert myclass_instance.value == 13


def test_myclass_increment_raises_typeerror_with_non_numeric_value():
    """Test that increment raises TypeError when value is not numeric."""
    obj = MyClass("not-a-number")
    with pytest.raises(TypeError):
        obj.increment()


def test_read_file_returns_content_with_mock_open():
    """Test read_file returns file contents using a mocked open."""
    mocked_data = "hello world"
    with patch("cal.open", mock_open(read_data=mocked_data), create=True) as m:
        result = read_file("/tmp/f.txt")
        assert result == mocked_data
        m.assert_called_once_with("/tmp/f.txt")
        handle = m()
        assert handle.read.called


def test_read_file_raises_file_not_found():
    """Test read_file propagates FileNotFoundError."""
    with patch("cal.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            read_file("missing.txt")


def test_calculate_average_normal_list():
    """Test calculate_average with a normal list of integers."""
    assert calculate_average([1, 2, 3, 4]) == 2.5


def test_calculate_average_with_floats():
    """Test calculate_average with a list of floats."""
    assert calculate_average([1.5, 2.5, 3.0]) == pytest.approx(2.3333333333)


def test_calculate_average_empty_list_raises():
    """Test calculate_average raises ZeroDivisionError on empty list."""
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


def test_print_area_raises_typeerror_before_print_called():
    """Test print_area raises TypeError due to string concatenation with float and does not call print."""
    with patch("cal.print") as mock_print:
        with pytest.raises(TypeError):
            print_area(2)
        mock_print.assert_not_called()


def test_calculate_area_returns_float():
    """Test calculate_area returns a float value."""
    result = calculate_area(5)
    assert isinstance(result, float)


def test_calculate_area_current_behavior_with_bitwise_xor():
    """Test calculate_area current behavior using XOR operator (^), not exponentiation."""
    # For radius=3: 3 ^ 2 == 1, so area should be 3.14 * 1 == 3.14
    assert calculate_area(3) == pytest.approx(3.14)


@pytest.mark.parametrize(
    "x, expected",
    [
        (30, "Divisible by 2, 3, and 5"),
        (6, "Divisible by 2 and 3 but not 5"),
        (8, "Divisible by 2 but not by 3"),
        (9, "Odd but divisible by 3"),
        (25, "Odd and divisible by 5"),
        (7, "Odd and not divisible by 3 or 5"),
        (0, "Zero"),
        (-4, "Negative even number"),
        (-3, "Negative odd number"),
    ],
)
def test_overly_complex_function_prints_expected_message(x, expected):
    """Test overly_complex_function prints the expected message for various inputs."""
    with patch("cal.print") as mock_print:
        overly_complex_function(x)
        mock_print.assert_called_once_with(expected)