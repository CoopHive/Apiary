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

```bash
apiary --verbose start-sell --config-path ./config/seller_naive.json
```
```bash
apiary --verbose start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/cowsay.Dockerfile
```
```bash
apiary --verbose start-buy --config-path ./config/buyer_naive.json --job-path ./jobs/cowsay.Dockerfile --price '["0x036CbD53842c5426634e7929541eC2318f3dCF7e", 1]'
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
