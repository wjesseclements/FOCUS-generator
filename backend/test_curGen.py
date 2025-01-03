import pytest
from curGen import generate_focus_data

def test_generate_focus_data():
    data = generate_focus_data(10)
    assert len(data) == 10