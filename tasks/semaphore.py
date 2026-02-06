from asyncio import gather, sleep, run
import asyncio

semphore = asyncio.Semaphore(3)

async def work(worker):
    async with semphore:
        print(f"{worker} ishni boshladim")
        await sleep(2)
        print(f"{worker} ishni tugatdim")

async def main():
    tasks = []
    for i in range(7):
        tasks.append(work(i+1))
    await gather(*tasks)

run(main())

