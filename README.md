# Apiary

## Overview

Apiary is a tool designed to simulate the agent-based and game theory aspects of the CoopHive protocol, a two-sided marketplace for computing resources.

## Installation

### Requirements

- Python >= 3.12

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/CoopHive/Apiary.git
   cd 
2. Install uv (if not already installed)

    ```bash
    make uv-download
3. Install dependencies and set up pre-commit hooks:

    ```bash
    make install
## Usage

Seller setup:
```bash
coophive --verbose run --role seller --private-key 7850b55b1582add03da1cab6350cdccd7fc13c093b5bc61a5378469b8151341a --public-key 0x1C53Ec481419daA436B47B2c916Fa3766C6Da9Fc --policy-name naive_accepter --inference-endpoint-port 8000

bun run runner.ts seller localhost:8000 ""  rediss://default:***@***.upstash.io:6379
```
Buyer setup:
```bash
coophive --verbose run --role buyer --private-key 0202ea5001ba9d11e8fecb4a3a943fbaa4a1068821e35533bd2161e76d333811 --public-key 0x002189E2F82ac8FBF19e2Dc279d19E07eCE12cfb --policy-name naive_accepter --inference-endpoint-port 8001

bun run runner.ts buyer localhost:8001 '{"pubkey": "0x002189E2F82ac8FBF19e2Dc279d19E07eCE12cfb","offerId": "offer_0","data": {"_tag": "offer","query": "FROM alpine:3.7\nRUN apk update && apk add --no-cache git perl && cd /tmp && git clone https://github.com/jasonm23/cowsay.git && cd cowsay ; ./install.sh /usr/local && rm -rf /var/cache/apk/* /var/tmp/* /tmp/* && apk del git\nCMD [\"/usr/local/bin/cowsay\",\"Docker is very good !\"]","price": ["0x036CbD53842c5426634e7929541eC2318f3dCF7e"]}}' rediss://default:***@***.upstash.io:6379
```

### Make

To format the code according to the project's style guidelines, run:

    make codestyle
To check the code style without modifying the files, run:

    make check-codestyle
To check the documentation style, run:

    make docs

To run the tests, use:

    make test

To upgrade class and package diagrams, use:

    make diagrams
