# TLDR

There are a myriad of decentralized financial products with a previously defined and relatively stable yield.


It seems interesting to be able to monitor hundreds of them and use machine learning/optimization/cross-validation to define optimal strategies that are neutral with respect to the following risks:
- covariance of the underlyings with respect to a risk free asset.
- blockchain, protocol, pool, token risks. For these, necessary to go beyond covariance? https://en.wikipedia.org/wiki/Taleb_distribution

Maybe it makes sense to also postulate a crypto CAPM based on R_t of BTC/of a crypto index and work hedged? We need to go short at that point. This can be done by shorting BTC or an index. Or maybe ETH makes more sense, given the DeFi nature? To be analyzed quantitatively (information coefficient or causal inference?)

The betas of the assets in the portfolio can also be calculated with a regression on the index: the index which is based on the returns of an instrument already defined as benchmark or on the first eigenvector of the covariance matrix, walk forward. Both biased but sensible choices.

https://www.spglobal.com/spdji/en/indexes/digital-assets/sp-cryptocurrency-broad-digital-market-index/

This decomposition or even just the degree of freedom to be able to short the market could increase the risk-adjusted performance of the product.

# Yield Aggregators and Optimizers

## Yearn Finance

<img src="https://s2.coinmarketcap.com/static/img/coins/64x64/5864.png" alt="drawing" width="50"/>

DeFi’s premier yield aggregator.

- https://yearn.fi/

- There is a token yearn.finance YFI associated with the protocol: https://coinmarketcap.com/currencies/yearn-finance/

- Here is the documentation: https://docs.yearn.fi/

Supported chains are: Ethereum (L1), Fantom (L1), Arbitrum (ETH L2), Optimism (ETH L2), Base (ETH L2) and Polygon (Multi-Chain L2).

There are fees to go from fiat to Metamask token, then from token to Vault token and back.

- Each yVaults can have a Deposit/Withdrawal fee, Management fee, Performance fee.
- Each Vaults has an APR associated with the recent past. For some it also has a decomposition of the various strategies inside the vault and the time series of the Historical APR.

An additional risk is therefore the volatility of the APR itself.

yVaults are interesting. veYFI are derivative products locking liquidity to increase APR, not interested for now. yETH is good, best way to think about it is a stand-alone Vault. The rest seems as not priority as veYFI.

Main products here:

v3: https://yearn.fi/v3

juiced: https://juiced.yearn.fi/

v2: https://yearn.fi/vaults

## Harvest Finance

<img src="https://pbs.twimg.com/profile_images/1658053645802274816/DJKnLw7r_400x400.png" alt="drawing" width="50"/>

Harvest optimizes yield farming for its users via automated strategies.

There is a token for the project: FARM. Harvest offers a simplified but powerful platform to discover yield strategies all across the decentralized finance ecosystem and helps you keep track of important performance metrics. 

Good breakdown of risks to be quantified at the portfolio management level:
https://docs.harvest.finance/other/security/risks

There is an API here: https://github.com/harvest-finance/harvest-api

-----

- https://beefy.com/
- https://www.grim.finance/
- https://www.sommelier.finance/
- https://factor.fi/
- https://earnpark.com/en/
- https://www.vaults.fyi/vaults
- https://www.pickle.finance/
- https://www.yieldmos.com/
- https://www.reaper.farm/
- https://idle.finance/
- https://yieldyak.com/avalanche/
- https://www.portals.fi/
- https://www.akropolis.io/
- https://cian.app/
- https://www.charm.fi/

## Lending and Borrowing Protocols

- https://aave.com/
- https://compound.finance/
- https://veno.finance/
- https://savvydefi.io/
- https://homora-v2.alphaventuredao.io/
- https://francium.io/
- https://www.kriya.finance/
- https://www.goat.fi/#/
- https://moonwell.fi/
- https://v2.sturdy.finance/overview
- https://spark.fi/

## Decentralized Exchanges (DEXs) and AMMs

- https://traderjoexyz.com/avalanche/pool
- https://curve.fi/
- https://uniswap.org/
- https://www.sushi.com/swap
- https://gmx.io/
- https://www.arrakis.finance/
- https://www.clip.finance/
- https://tokensfarm.com/
- https://balancer.fi/


## Yield and Liquidity Pools

- https://stargate.finance/
- https://vesper.finance/
- https://pancakebunny.finance/vault
- https://aura.finance/
- https://www.alpacafinance.org/
- https://tulip.garden/strategy
- https://bru.finance/
- https://www.convexfinance.com/
- https://stellaxyz.io/


## Staking and Protocols

- https://lido.fi/
- https://www.originprotocol.com/oeth
- https://synthetix.io/
- https://www.stakingrewards.com/
- https://realt.co/
- https://www.metavisor.app/
- https://indexcoop.com/


## Derivatives and Hedging

- https://dydx.exchange/
- https://swivel.finance/
- https://toros.finance
- https://oceanpoint.fi/
- https://mellow.finance/
- https://earn.network/
- https://rainmaker.nyc/


## Blockchain Infrastructure and Analytics

- https://moralis.io/
- https://thegraph.com/en/
- https://www.covalenthq.com/
- https://www.quicknode.com/
- https://www.blockdaemon.com/
- https://bitquery.io/
- https://blockchair.com/
- https://tatum.io/
- https://nownodes.io/
- https://portfolio.nansen.ai/

## Protocol and Risk Management

- https://www.eigenlayer.xyz/
- https://solidly.com/
- https://app.kamino.finance/
- https://mozaic.finance/
- https://y24.io/
- https://rehold.io/
- https://furucombo.app/

## Monitoring

- https://yearn.watch/
- https://zapper.xyz/
- https://app.zerion.io/
- https://debank.com/
- https://dune.com/home
