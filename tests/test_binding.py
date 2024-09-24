import pytest

from apiary import apiars


@pytest.mark.asyncio
async def test_helloworld():
    res = await apiars.helloworld()
    assert res == "HelloWorld"
