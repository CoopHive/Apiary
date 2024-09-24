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
use pyo3::{exceptions::PyValueError, PyErr};
use std::env;

use crate::py_val_err;

pub fn get_provider() -> Result<
    FillProvider<
        JoinFill<
            JoinFill<
                alloy::providers::Identity,
                JoinFill<GasFiller, JoinFill<BlobGasFiller, JoinFill<NonceFiller, ChainIdFiller>>>,
            >,
            WalletFiller<EthereumWallet>,
        >,
        RootProvider<Http<Client>>,
        Http<Client>,
        Ethereum,
    >,
    pyo3::PyErr,
> {
    let signer: PrivateKeySigner = env::var("PRIVATE_KEY")
        .or_else(|_| py_val_err!("PRIVATE_KEY not set"))?
        .parse()
        .or_else(|_| py_val_err!("couldn't parse PRIVATE_KEY as a private key"))?;
    let wallet = EthereumWallet::from(signer);
    let rpc_url = env::var("RPC_URL")
        .or_else(|_| py_val_err!("RPC_URL not set"))?
        .parse()
        .or_else(|_| py_val_err!("couldn't parse RPC_URL as a url"))?;
    let provider = ProviderBuilder::new()
        .with_recommended_fillers()
        .wallet(wallet)
        .on_http(rpc_url);
    Ok(provider)
}
