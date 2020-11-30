# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets

logging.basicConfig()

MENSAGEM = {"texto": ""}

USERS = set()

# dict com key=user(websocket) e value=nome
nomes = {}


def msg_event():
    return json.dumps({"type": "msg", **MENSAGEM})

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_msg(remetente):
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = msg_event()
        await asyncio.wait([user.send(message) for user in USERS if user != remetente])

async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_nome(destinatario, nome):
    message = json.dumps({"type": "msg", "texto": "* → Nome alterado para {} com sucesso".format(nome)})
    await asyncio.wait([destinatario.send(message)])
    message2 = json.dumps({"type": "msg", "texto": "* → Para enviar uma mensagem privada, digite '/privado' seguido do nome do destinatário e então sua mensagem."})
    await asyncio.wait([destinatario.send(message2)])


async def register(websocket):
    USERS.add(websocket)
    await websocket.send(json.dumps({"type": "msg", "texto": "* → Seja Bem-vindo à Sala de Bate Papo. Digite '/nome' seguido de seu nome (sem espaços), por favor."}))
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def chat(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(msg_event())
        async for message in websocket:
            data = json.loads(message)
            nome_duplicado = False
            if(data["msg"].split(' ', 1)[0] == "/nome"):
                nome = data["msg"].split(' ')[1]
                for websckt, name in nomes.items():
                    if nome == name:
                        # nome duplicado
                        nome_duplicado = True
                if(nome_duplicado == False):
                    nomes[websocket] = nome
                    await notify_nome(websocket, nome)
                    MENSAGEM["texto"] = "* → {} está conectado!".format(nome)
                    await notify_msg(websocket)
                else:
                    await websocket.send(json.dumps({"type": "msg", "texto": "* → Este nome já está em uso. Por favor digite '/nome' seguido de um novo nome."}))
            
            elif(data["msg"].split(' ', 1)[0] == "/privado"):
                # mensagem privada
                destinatario_nome = data["msg"].split(' ')[1]
                msg_privada = data["msg"].split(' ', 2)[2]
                for websckt, name in nomes.items():
                    if destinatario_nome == name:
                        destinatario_websocket = websckt
                try:
                    await destinatario_websocket.send(json.dumps({"type": "msg", "texto": "[PRIVADO] " + nomes[websocket] + " >> " + msg_privada}))
                except:
                    await websocket.send(json.dumps({"type": "msg", "texto": "* → Nome inválido. Sua mensagem privada não foi enviada. Tente novamente."}))
            else:
                try:
                    MENSAGEM["texto"] = nomes[websocket] + " >> " + data["msg"]
                    await notify_msg(websocket)
                except:
                    await websocket.send(json.dumps({"type": "msg", "texto": "* → Sua mensagem não foi enviada pois você ainda não tem nome. Por favor digite '/nome' seguido de seu nome."}))
    finally:
        try:
            MENSAGEM["texto"] = "* → " + nomes[websocket] + " deconectou do chat :("
            await notify_msg(websocket)
        finally:
            await unregister(websocket)



start_server = websockets.serve(chat, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()