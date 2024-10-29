from apiary import apiars


def test_binding():
    res = apiars.erc20.helloworld()
    assert res == "HelloWorld ERC20"
    res = apiars.erc721.helloworld()
    assert res == "HelloWorld ERC721"
    res = apiars.bundle.helloworld()
    assert res == "HelloWorld Bundle"
