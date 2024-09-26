from apiary import apiars
from dotenv import load_dotenv
import asyncio


async def main():
    load_dotenv()
    tx = await apiars.make_buy_statement(
        "0xD4fA4dE9D8F8DB39EAf4de9A19bF6910F6B5bD60",
        1000,
        "bafkreihy4ldvgswp223sirjii2lck4pfvis3aswy65y2xyquudxvwakldy",
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    )
    print(tx)


asyncio.run(main())
