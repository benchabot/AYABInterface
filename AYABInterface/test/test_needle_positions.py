"""This module tests the NeeldePositions class.

The :class:`AYABInterface.interface.NeeldePositions` is tested here and
every access to other classes is mocked.
"""
import pytest
from pytest import fixture, raises
from AYABInterface import NeedlePositions
from unittest.mock import MagicMock
from collections import namedtuple

Machine = namedtuple("Machine", ("number_of_needles", "needle_positions"))


@fixture
def machine():
    """The machine to knit on."""
    return Machine(5, (1, 2))


@fixture
def rows():
    """The rows to knit."""
    return [[1, 1, 1, 1, 1], [2, 2, 2, 2, 2], [1, 2, 1, 2, 1], [2, 1, 2, 1, 2]]


@fixture
def needle_positions(rows, machine):
    """The initialized needle positions."""
    return NeeldePositions(rows, machine)


class TestInvalidInitialization(object):
    
    """Test the invalid arguments.
    
    These arguments are captured by 
    Test :meth:`AYABInterface.interface.NeeldePositions.check`.
    """
    
    @pytest.mark.parametrize("number_of_needles,length_of_row,row_index",
        [[5, 4, 2], [3, 4, 2], [100, 101, 4], [5, 2, 0], [114, 200, 8], ])
    def test_number_of_needles(self, length_of_row, number_of_needles,
                               row_index):
        """Test a row with a different length than the number of neeedles."""
        rows = [[1] * number_of_needles] * row_index + \
            [[1] * length_of_row] + [[1] * number_of_needles] * 5
        with raises(ValueError) as error:
            needle_positions(rows, Machine(number_of_needles, (1, 2)))
        message = "The length of row {} is {} but {} is expected.".format(
            row_index, length_of_row, number_of_needles)
        assert error.args[0] == message

    @pytest.mark.parametrize("position,value,positions",
        [[3, 4, "D"], [4, 1, 3], [0, 0, "asd"], [7, 7, 77]])
    def test_needle_positions(self, position, value, positions):
        """Test needle positions that are not allowed."""
        rows = [["A"] * 8 for i in range(8)]
        rows[position[0]][position[1]] = value
        with raises(ValueError) as error:
            needle_positions(rows, Machine(8, positions))
        message = "Needle position in row {} at index {} is {} but one of"\
            " {} was expected".format(position[0], posistion[1], value,
                ", ".join(map(repr, positions))
        assert error.args[0] == message


def test_machine(needle_positions, machine):
    """Test :meth:`AYABInterface.interface.NeeldePositions.machine`."""
    assert needle_positions.machine == machine

    
class TestGetRows(object):

    """Test :meth:`AYABInterface.interface.NeeldePositions.get_row`."""

    @pytest.mark.parametrize("index", range(len(rows())))
    @pytest.mark.parametrize("default", [None, object(), []])
    def test_index(self, needle_positions, rows, index):
        """Test valid indices."""
        assert needle_positions.get_row(index, default) == rows[index]

    @pytest.mark.parametrize("index", [-4, -1, 8, 12, 1000, "ads"])
    @pytest.mark.parametrize("default", [None, object(), []])
    def test_invalid_index(self, needle_positions, rows, index):
        """Test invalid indices."""
        assert needle_positions.get_row(index, default) == default


class TestCompletedRows(object):
    
    """Test the completion of rows.
    
    This is a unity of
    :meth:`AYABInterface.interface.NeeldePositions.row_completed` and
    :meth:`AYABInterface.interface.NeeldePositions.completed_row_indices`
    """

    def test_thread_safety(self, needle_positions):
        """Test that concurrent access does not change the result."""
        assert needle_positions.completed_row_indices is not \
            needle_positions.completed_row_indices

    @pytest.mark.parametrize("indices", [[], [1, 2, 3], [3], [1, "asd", 100]])
    def test_completed_rows(self, needle_positions, indices):
        """Test that completed rows are listed."""
        for index in indices:
            needle_positions.row_completed(index)
        assert needle_positions.completed_rows == indices
