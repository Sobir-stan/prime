import asyncio

semaphore = asyncio.Semaphore(3)

async def ishchi(nomi):
    async with semaphore:
        print(f"{nomi}: ishni boshladim")


        if nomi == "Ishchi-3":
            raise ValueError("XATO Ishchi-3 da!")

        await asyncio.sleep(2)
        print(f"{nomi}: ishni tugatdim")

async def main():
    tasks = []

    for i in range(1, 8):
        task = asyncio.create_task(ishchi(f"Ishchi-{i}"))
        tasks.append(task)

    try:
        await asyncio.gather(*tasks)

    except Exception as e:
        print("Xatolik:", e)

        for task in tasks:
            task.cancel()

asyncio.run(main())

