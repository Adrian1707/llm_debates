from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.http import JsonResponse
import sys
from base64 import urlsafe_b64decode
from llm_debate.debate_agent import DebateAgent
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Loads .env file from current directory by default

def hello_world(request):
    debate_topic = "Should a dog be allowed to be President"
    agent_for = DebateAgent(side='for', topic=debate_topic)
    agent_against = DebateAgent(side='against', topic=debate_topic)

    # Start the debate loop
    start_debate(agent_for, agent_against, max_rounds=5)
    return HttpResponse("Hello World!")

def start_debate(agent_for, agent_against, max_rounds=5):
    debate_log = []

    # Opening statement FOR side
    opening_for_text = "".join(list(agent_for.respond("Please provide your opening statement.")))
    agent_for.previous_arguments.append(opening_for_text)
    debate_log.append({'side': 'for', 'text': opening_for_text})

    # Opening statement AGAINST side responds to FOR's opener
    opening_against_text = "".join(list(agent_against.respond(opening_for_text)))
    agent_against.previous_arguments.append(opening_against_text)
    debate_log.append({'side': 'against', 'text': opening_against_text})

    current_turn = 'for'

    # Start at first rebuttal after both have opened (so range(1,max_rounds))
    for round_num in range(1, max_rounds):
        print(f"Round {round_num}")

        if current_turn == 'for':
            opponent_argument = agent_against.previous_arguments[-1]
            response_text = "".join(list(agent_for.respond(opponent_argument)))
            agent_for.previous_arguments.append(response_text)
            debate_log.append({'side': 'for', 'text': response_text})
            current_turn = 'against'
        else:
            opponent_argument = agent_for.previous_arguments[-1]
            response_text = "".join(list(agent_against.respond(opponent_argument)))
            agent_against.previous_arguments.append(response_text)
            debate_log.append({'side': 'against', 'text': response_text})
            current_turn = 'for'

    return debate_log

urlpatterns = [
    path('', hello_world),  # root endpoint
]