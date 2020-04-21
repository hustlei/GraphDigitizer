# -*- coding: utf-8 -*-
"""test for project data.

Copyright (c) 2019 lileilei <hustlei@sina.cn>
"""

from pytest import fixture
from core.project import Datas

@fixture(scope="function")
def data():
    """Fixture: create a datas
    """
    return Datas()


def test_project(data,tmpdir):
    """Test for open and save for project
    """
    f = tmpdir.join("new1.digi").ensure()
    data.save("new1.digi")
    d = data.open("new1.digi")
    assert d.curves["default"].name == "default" and d.axisx[1] is 1
