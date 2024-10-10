use alloy::{
    network::{Ethereum, EthereumWallet},
    providers::{
        fillers::{
            BlobGasFiller, ChainIdFiller, FillProvider, GasFiller, JoinFill, NonceFiller,
            WalletFiller,
        },
        ProviderBuilder, RootProvider,
    },
    signers::local::PrivateKeySigner,
    transports::http::{Client, Http},
};
use alloy_provider::Identity;
use std::env;

use crate::shared::py_val_err;

type DefaultProvider = FillProvider<
    JoinFill<
        JoinFill<
            Identity,
            JoinFill<GasFiller, JoinFill<BlobGasFiller, JoinFill<NonceFiller, ChainIdFiller>>>,
        >,
        WalletFiller<EthereumWallet>,
    >,
    RootProvider<Http<Client>>,
    Http<Client>,
    Ethereum,
>;

pub fn get_provider(private_key: String) -> Result<DefaultProvider, pyo3::PyErr> {
    let signer: PrivateKeySigner = private_key
        .parse()
        .map_err(|_| py_val_err("couldn't parse private_key as PrivateKeySigner"))?;

    let wallet = EthereumWallet::from(signer);
    let rpc_url = env::var("RPC_URL")
        .map_err(|_| py_val_err("RPC_URL not set"))?
        .parse()
        .map_err(|_| py_val_err("couldn't parse RPC_URL as a url"))?;

    let provider = ProviderBuilder::new()
        .with_recommended_fillers()
        .wallet(wallet)
        .on_http(rpc_url);

    Ok(provider)
}
