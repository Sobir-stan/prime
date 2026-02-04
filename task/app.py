import asyncio

async def study(name, delay):
    print(f"{name} dars qilishni boshladi")

    if name == "B":
        raise ValueError("Xato B da!")

    await asyncio.sleep(delay)

    print(f"{name} dars qilishni tugatdi")
    return f"{name} xonadan chiqdi"
async def main():
    tasks = [
        study("A", 2),
        study("B", 3),
        study("C", 1)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"Xato yuz berdi: {result}")
        else:
            print(result)
asyncio.run(main())

