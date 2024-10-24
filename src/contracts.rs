use alloy::sol;

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IEAS,
    "src/contracts/IEAS.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC20,
    "src/contracts/IERC20.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    IERC721,
    "src/contracts/IERC721.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC20PaymentObligation,
    "src/contracts/ERC20PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    ERC721PaymentObligation,
    "src/contracts/ERC721PaymentObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    JobResultObligation,
    "src/contracts/JobResultObligation.json"
);

sol!(
    #[allow(missing_docs)]
    #[sol(rpc)]
    RedisProvisionObligation,
    "src/contracts/RedisProvisionObligation.json"
);
