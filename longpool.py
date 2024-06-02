# timeout = 60

# class MsgContainer:
#     __messages = {}

#     def add_message(self, id, msg):
#         self.__messages[id] = msg

#     async def get_message(self, id):
#         for i in range(timeout):
#             if id in self.__messages.keys() and self.__messages[id] != None:
#                 a = self.__messages[id]
#                 self.__messages[id] = None
#                 return a
#             else:
#                 await asyncio.sleep(1)
#         return None


# msg_cont = MsgContainer()

# @app.get("/message")
# async def get_message(id: str):
#     message = await msg_cont.get_message(id)
#     if message:
#         return {"msg":message}
#     else:
#         raise fastapi.HTTPException(502, {"msg":"no msg"})

# @app.post("/message")
# async def send_msg(msg:str, id:str):
#     msg_cont.add_message(id, msg)
#     return {id:msg}