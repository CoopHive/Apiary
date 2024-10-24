use alloy::{
    primitives::{self, b256, Address, Bytes, FixedBytes, U256},
    sol,
    sol_types::{SolEvent, SolValue},
};
use std::env;

use crate::contracts::{ERC20PaymentObligation, RedisProvisionObligation, IEAS, IERC20};
use crate::provider;

pub async fn make_buy_statement() -> eyre::Result<FixedBytes<32>> {}
