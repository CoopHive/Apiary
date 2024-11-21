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

pub fn get_wallet_provider(private_key: String) -> eyre::Result<WalletProvider> {
    let signer: PrivateKeySigner = private_key
        .parse()?;

    let wallet = EthereumWallet::from(signer);
    let rpc_url = env::var("RPC_URL")?
        .parse()?;

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

pub fn get_public_provider() -> eyre::Result<PublicProvider> {
    let rpc_url = env::var("RPC_URL")?
        .parse()?;

    let provider = ProviderBuilder::new()
        .on_http(rpc_url);

    Ok(provider)
}
