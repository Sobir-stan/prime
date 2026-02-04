import asyncio
from asyncio import gather

async def study(name,delay):
    print(f"{name} dars qilishni boshladi")
    await asyncio.sleep(delay)
    print(f"{name} dars qilishni tugatdi")

    a = asyncio.gather(study("A",2),study("B",1),study("C",3))

    if a == "B":
        print(ValueError("Xatolik B da"))

    if ValueError:
        a.cancel()


asyncio.run(study("A",2))
