from typing_extensions import override
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from openai import AssistantEventHandler
from englishcode_ai_chatbot_rest.settings.base import openai_client


# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 
class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)


# Create your views here.

class TestAPIView(APIView):
    def post(self, request, *args, **kwargs):

        openai_thread = openai_client.beta.threads.create()
        print("OPENAI THREAD: ", openai_thread.id)

        message = openai_client.beta.threads.messages.create(
            thread_id=openai_thread.id,
            role="user",
            content="hi"
        )

        # Without Streaming

        run = openai_client.beta.threads.runs.create_and_poll(
            thread_id=openai_thread.id,
            assistant_id="asst_4h6Rhvsk5kg6M4kvZndcmWCT"
        )

        if run.status == 'completed':
            messages = openai_client.beta.threads.messages.list(
                thread_id=openai_thread.id
            )
            print("MESSAGES: ", messages)
        else:
            print(run.status)

        return Response({"message": messages})
