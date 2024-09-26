"""Fork Anvil using RPC URL."""

import os
import subprocess

from dotenv import load_dotenv

load_dotenv(override=True)

sepolia_rpc_url = os.getenv("ANVIL_RPC_URL")
subprocess.run(["anvil", "--fork-url", sepolia_rpc_url])
