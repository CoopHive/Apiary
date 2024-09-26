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
   cd Apiary
2. Install bun if not already installed)

    ```bash
    make bun-install
3. Install uv (if not already installed)

    ```bash
    make uv-download
4. Install dependencies and set up pre-commit hooks:

    ```bash
    make install

5. Populate all the necessary environmental variables and/or confguration file:
    - REDIS_URL
    - RPC_URL
    - ERC20_PAYMENT_STATEMENT
    - DOCKER_RESULT_STATEMENT
    - EAS_CONTRACT
    - LIGHTHOUSE_TOKEN
    - PRIVATE_KEY
    - PUBLIC_KEY
    - INFERENCE_ENDPOINT.PORT
    - INFERENCE_ENDPOINT.HOST

## Usage

As a seller, simply run:

```bash
apiary --verbose start-sell --config-path ./config/seller_naive.json
```

As a buyer, run:

```bash
apiary --verbose start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/cowsay.Dockerfile --price '["0x036CbD53842c5426634e7929541eC2318f3dCF7e", 1]'
```

Note that buyers can avoid specifying the initial offer job price:

```bash
apiary --verbose start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/cowsay.Dockerfile
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
