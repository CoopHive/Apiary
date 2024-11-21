use alloy::primitives::{Address, U256};

pub struct ERC20Price {
    pub token: Address,
    pub amount: U256,
}

pub struct ERC721Price {
    pub token: Address,
    pub id: U256,
}

pub struct BundlePrice {
    pub erc20_addresses: Vec<Address>,
    pub erc20_amounts: Vec<U256>,
    pub erc721_addresses: Vec<Address>,
    pub erc721_ids: Vec<U256>,
}