# CoopHive Simulator

## Overview

CoopHive Simulator is a tool designed to simulate the agent-based and game theory aspects of the CoopHive protocol, a two-sided marketplace for computing resources.

## Installation

### Requirements

- Python >= 3.10

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/CoopHive/coophive-simulator.git
   cd coophive-simulator
2. Install Poetry (if not already installed)

    ```bash
    make poetry-download
3. Install dependencies and set up pre-commit hooks:

    ```bash
    make install
## Usage

To format the code according to the project's style guidelines, run:

    make codestyle
To check the code style without modifying the files, run:

    make check-codestyle
To check the documentation style, run:

    ```bash
    make docs

To run the tests, use:

    ```bash
    make test
