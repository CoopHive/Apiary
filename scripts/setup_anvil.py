"""Fork Anvil using RPC URL."""

import os
import subprocess

sepolia_rpc_url = os.getenv("RPC_URL")
subprocess.run(["anvil", "--fork-url", sepolia_rpc_url])
