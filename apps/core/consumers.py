import json
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import AssistantEventHandler
from typing_extensions import override
from englishcode_ai_chatbot_rest.settings.base import openai_client
from asgiref.sync import async_to_sync, sync_to_async


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import AssistantEventHandler
from typing_extensions import override
from englishcode_ai_chatbot_rest.settings.base import openai_client
from asgiref.sync import async_to_sync, sync_to_async


class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("ENTRA a connect")
        await self.accept()

        # Inicializa el ID del asistente
        self.assistant_id = "asst_4h6Rhvsk5kg6M4kvZndcmWCT"

        # Crear el Thread
        #self.thread = await sync_to_async(openai_client.beta.threads.create)()
        self.thread_id = "thread_lS2y9R4104M8j0JQTKe9zWyo"

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print("ENTRA a receive")

        await self.send(text_data=json.dumps({
            'message': "hola"
        }))

        text_data_json = json.loads(text_data)
        user_message = text_data_json['message']

        # Añadir el mensaje del usuario al Thread
        await sync_to_async(openai_client.beta.threads.messages.create)(
            thread_id=self.thread_id,
            role="user",
            content=user_message,
        )

        # Crear y manejar el streaming de la respuesta
        class EventHandler(AssistantEventHandler):
            def __init__(self, send_method):
                super().__init__()
                self.send_method = send_method
                print("EventHandler inicializado")

            @override
            async def on_text_created(self, text) -> None:
                print(f"on_text_created: {text}")
                await self.send_method(json.dumps({
                    'message': f"assistant > {text}"
                }))

            @override
            async def on_text_delta(self, delta, snapshot):
                print(f"on_text_delta: {delta.value}")
                await self.send_method(json.dumps({
                    'message': delta.value
                }))

            async def on_tool_call_created(self, tool_call):
                print(f"on_tool_call_created: {tool_call.type}")
                await self.send_method(json.dumps({
                    'message': f"assistant > {tool_call.type}"
                }))

            async def on_tool_call_delta(self, delta, snapshot):
                print(f"on_tool_call_delta: {delta.type}")
                if delta.type == 'code_interpreter':
                    if delta.code_interpreter.input:
                        await self.send_method(json.dumps({
                            'message': delta.code_interpreter.input
                        }))
                    if delta.code_interpreter.outputs:
                        await self.send_method(json.dumps({
                            'message': "output >"
                        }))
                        for output in delta.code_interpreter.outputs:
                            if output.type == "logs":
                                await self.send_method(json.dumps({
                                    'message': output.logs
                                }))

        event_handler = EventHandler(self.send)

        # Ejecutar el streaming en un contexto síncrono
        print("Ejecutando el streaming...")
        await sync_to_async(self.run_streaming)(event_handler)
        print("TERMINA RECEIVE")

    def run_streaming(self, event_handler):
        with openai_client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            # instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
        print("Streaming finalizado")
