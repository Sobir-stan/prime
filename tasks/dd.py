import asyncio

# async def cat():
#     await asyncio.sleep(2)
#     print("myau")
#
# async def dog():
#     await asyncio.sleep(2)
#     print("gaf")
#
# async def main():
#     resalt = await cat()
#     resalt = await dog()
#
# asyncio.run(main())


# async def study(name, delay):
#     await asyncio.sleep(delay)
#     print(f"{name} dars qilishni boshlashdi")
#     await asyncio.sleep(delay)
#     print(f"{name} dars qilishni toxtatdi")
#
# async def main():
#     await asyncio.gather(
#         study("ali", 2),
#         study("vali", 3),
#         study("kola", 1)
#     )
#
# asyncio.run(main())


# async def study(name, delay):
#     await asyncio.sleep(delay)
#     message = f"{name} dars qilishni boshlashdi"
#     if name == "b":
#         raise ValueError("xato b da!")
#     if message != f"{name} dars qilishni boshlashdi":
#         raise AssertionError("Сообщение не соответствует ожидаемому")
#     print(message)
#     await asyncio.sleep(delay)
#     print(f"{name} dars qilishni toxtatdi")
#
# async def main():
#     await asyncio.gather(
#         study("ali", 2),
#         study("vali", 3),
#         study("kola", 1)
#     )
#
# asyncio.run(main())



# async def study(name, delay):
#     await asyncio.sleep(delay)
#     message = f"{name} dars qilishni boshlashdi"
#     if name == "b":
#         raise ValueError("xato b da!")
#     if message != f"{name} dars qilishni boshlashdi":
#         raise AssertionError("Сообщение не соответствует ожидаемому")
#     print(message)
#     await asyncio.sleep(delay)
#     print(f"{name} dars qilishni toxtatdi")
#
# async def main():
#     tasks = [
#         asyncio.create_task(study("ali", 2)),
#         asyncio.create_task(study("vali", 3)),
#         asyncio.create_task(study("kola", 1))
#     ]
#
#     done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
#
#     # если в выполненных задачах есть ошибка — отменяем остальные и пробрасываем её
#     for t in done:
#         exc = t.exception()
#         if exc is not None:
#             for p in pending:
#                 p.cancel()
#             # дождаться отменённых задач, подавляя исключения
#             await asyncio.gather(*pending, return_exceptions=True)
#             raise exc
#
#     # если ошибок нет — дождаться оставшихся результатов
#     await asyncio.gather(*pending)
#
# asyncio.run(main())