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
use pyo3::exceptions::PyValueError;


type WalletProvider = FillProvider<
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

pub fn get_wallet_provider(private_key: String) -> Result<WalletProvider, pyo3::PyErr> {
    let signer: PrivateKeySigner = private_key
        .parse()
        .map_err(|_| PyValueError::new_err("couldn't parse private_key as PrivateKeySigner"))?;

    let wallet = EthereumWallet::from(signer);
    let rpc_url = env::var("RPC_URL")
        .map_err(|_| PyValueError::new_err("RPC_URL not set"))?
        .parse()
        .map_err(|_| PyValueError::new_err("couldn't parse RPC_URL as a url"))?;

    let provider = ProviderBuilder::new()
        .with_recommended_fillers()
        .wallet(wallet)
        .on_http(rpc_url);

    Ok(provider)
}

type PublicProvider = FillProvider<
    JoinFill<
        Identity,
        JoinFill<GasFiller, JoinFill<BlobGasFiller, JoinFill<NonceFiller, ChainIdFiller>>>,
    >,
    RootProvider<Http<Client>>,
    Http<Client>,
    Ethereum,
>;

pub fn get_public_provider() -> Result<PublicProvider, pyo3::PyErr> {
    let rpc_url = env::var("RPC_URL")
        .map_err(|_| PyValueError::new_err("RPC_URL not set"))?
        .parse()
        .map_err(|_| PyValueError::new_err("couldn't parse RPC_URL as a url"))?;

    let provider = ProviderBuilder::new()
        .with_recommended_fillers()
        .on_http(rpc_url);

    Ok(provider)
}
