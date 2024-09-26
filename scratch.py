from apiary import apiars
from dotenv import load_dotenv
import asyncio


async def main():
    load_dotenv()
    tx = await apiars.make_buy_statement(
        "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        10,
        "bafkreihy4ldvgswp223sirjii2lck4pfvis3aswy65y2xyquudxvwakldy",
        "7850b55b1582add03da1cab6350cdccd7fc13c093b5bc61a5378469b8151341a",
    )
    print(tx)


asyncio.run(main())
