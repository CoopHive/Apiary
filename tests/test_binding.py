from apiary import apiars


def test_binding():
    res = apiars.helloworld()
    assert res == "HelloWorld"
