from apiary import apiars


def test_binding():
    res = apiars.erc20.erc20_helloworld()
    assert res == "HelloWorld ERC20"
    res = apiars.erc721.erc721_helloworld()
    assert res == "HelloWorld ERC721"
