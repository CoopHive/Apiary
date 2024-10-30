use crate::{contracts::{BundlePaymentObligation, ERC721PaymentObligation}, provider};
use std::env;

use alloy::{
    hex, primitives::{self, Address, FixedBytes}, sol_types::SolValue
};

use crate::shared::{ERC20Price, ERC721Price, BundlePrice};
use crate::contracts::{ERC20PaymentObligation, JobResultObligation, IEAS};

pub struct JobPayment20 {
    pub price: ERC20Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub struct JobPayment721 {
    pub price: ERC721Price,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub struct JobPaymentBundle {
    pub price: BundlePrice,
    pub arbiter: primitives::Address,
    pub demand: JobResultObligation::StatementData,
}

pub enum JobPaymentResult {
    JobPayment20(JobPayment20),
    JobPayment721(JobPayment721),
    JobPaymentBundle(JobPaymentBundle),
}

pub async fn get_buy_statement(
    statement_uid: FixedBytes<32>,
) -> eyre::Result<JobPaymentResult> {
    let provider = provider::get_public_provider()?;

    let eas_address = env::var("EAS_CONTRACT").map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);
    let attestation = contract.getAttestation(statement_uid).call().await?._0;
    let attestation_schema_string = hex::encode(attestation.schema);

    println!("{}", attestation_schema_string);

    let erc20_schema_uid =
        env::var("ERC20_SCHEMA_UID")?;

    let erc721_schema_uid =
        env::var("ERC721_SCHEMA_UID")?;

    let bundle_schema_uid =
        env::var("BUNDLE_SCHEMA_UID")?;

    if attestation_schema_string == erc20_schema_uid {
        let attestation_data =
        ERC20PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

        Ok(JobPaymentResult::JobPayment20(JobPayment20 {
            price: ERC20Price {
                token: attestation_data.token,
                amount: attestation_data.amount,
            },
            arbiter: attestation_data.arbiter,
            demand: JobResultObligation::StatementData::abi_decode(&attestation_data.demand, true)?,
        }))
    } else if attestation_schema_string == erc721_schema_uid {
        let attestation_data =
        ERC721PaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;
        
        Ok(JobPaymentResult::JobPayment721(JobPayment721 {
            price: ERC721Price {
                token: attestation_data.token,
                id: attestation_data.tokenId,
            },
            arbiter: attestation_data.arbiter,
            demand: JobResultObligation::StatementData::abi_decode(&attestation_data.demand, true)?,
        }))
    } else if attestation_schema_string == bundle_schema_uid {
        let attestation_data =
        BundlePaymentObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;
        
        Ok(JobPaymentResult::JobPaymentBundle(JobPaymentBundle {
            price: BundlePrice {
                erc20_addresses: attestation_data.erc20Addresses,
                erc20_amounts: attestation_data.erc20Amounts,
                erc721_addresses: attestation_data.erc721Addresses,
                erc721_ids: attestation_data.erc721Ids
            },
            arbiter: attestation_data.arbiter,
            demand: JobResultObligation::StatementData::abi_decode(&attestation_data.demand, true)?,
        }))
    } else {
        return Err(eyre::eyre!("Invalid attestation schema UID."));
    }
}

pub async fn get_sell_statement(
    sell_uid: FixedBytes<32>,
) -> eyre::Result<String> {
    let provider = provider::get_public_provider()?;

    let eas_address = env::var("EAS_CONTRACT")
        .map(|a| Address::parse_checksummed(a, None))??;

    let contract = IEAS::new(eas_address, provider);

    let attestation = contract
        .getAttestation(sell_uid)
        .call()
        .await?
        ._0;

    let attestation_data =
        JobResultObligation::StatementData::abi_decode(attestation.data.as_ref(), true)?;

    Ok(attestation_data.result)
}
