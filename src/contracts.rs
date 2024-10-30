use alloy::sol;

// general

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    IEAS,
    "src/contracts/IEAS.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    IERC20,
    "src/contracts/IERC20.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    IERC721,
    "src/contracts/IERC721.json"
);

// obligations

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    ERC20PaymentObligation,
    "src/contracts/ERC20PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    ERC721PaymentObligation,
    "src/contracts/ERC721PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    BundlePaymentObligation,
    "src/contracts/BundlePaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    JobResultObligation,
    "src/contracts/JobResultObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    #[derive(Debug)]
    RedisProvisionObligation,
    "src/contracts/RedisProvisionObligation.json"
);
