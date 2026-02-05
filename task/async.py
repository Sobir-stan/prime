import asyncio
from asyncio import gather
from threading import Semaphore


async def work1(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work2(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work3(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work4(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work5(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work6(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def work7(delay):
    with Semaphore(2):
        print(f"ishni boshladim")
        await asyncio.sleep(delay)
        print(f"ishni tugatdim")

async def main():
    await gather(
        work1(2),
        work2(2),
        work3(2),
        work4(2),
        work5(2),
        work6(2),
        work7(2),
    )
asyncio.run(main())