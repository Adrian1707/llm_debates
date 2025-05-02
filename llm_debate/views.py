from django.shortcuts import render
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
import sys
from base64 import urlsafe_b64decode
from llm_debate.debate_agent import DebateAgent
import os
import json
from dotenv import load_dotenv
from . import views

load_dotenv()  # Loads .env file from current directory by default

from django.http import StreamingHttpResponse
from django.shortcuts import render

def submit_topic(request):
    """Render a form for the user to submit a debate topic."""
    return render(request, 'submit_topic.html')

def hello_world(request):
    debate_topic = request.GET.get('debate_topic')
    if not debate_topic:
        debate_topic = "Should a dog be allowed to be President"
    
    # Check if this is an SSE request or the initial page load
    if request.headers.get('accept') == 'text/event-stream':
        agent_for = DebateAgent(side='for', topic=debate_topic)
        agent_against = DebateAgent(side='against', topic=debate_topic)

        def event_stream():
            # Opening statement FOR side
            yield "data:### FOR:\n\n"
            for chunk in agent_for.respond("Please provide your opening statement."):
                # Ensure each chunk is properly formatted with spaces
                chunk_text = _safe_decode(chunk)
                # Add a space after punctuation if needed
                if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                    chunk_text += ' '
                yield f"data:{chunk_text}\n\n"

            # Opening statement AGAINST side responds to FOR's opener
            yield "data:### AGAINST:\n\n"
            for chunk in agent_against.respond(agent_for.previous_arguments[-1]):
                chunk_text = _safe_decode(chunk)
                if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                    chunk_text += ' '
                yield f"data:{chunk_text}\n\n"

            current_turn = 'for'
            max_rounds = 5

            for round_num in range(1, max_rounds):
                if current_turn == 'for':
                    opponent_argument = agent_against.previous_arguments[-1]
                    yield "data:### FOR:\n\n"
                    for chunk in agent_for.respond(opponent_argument):
                        chunk_text = _safe_decode(chunk)
                        if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                            chunk_text += ' '
                        yield f"data:{chunk_text}\n\n"
                    current_turn = 'against'
                else:
                    opponent_argument = agent_for.previous_arguments[-1]
                    yield "data:### AGAINST:\n\n"
                    for chunk in agent_against.respond(opponent_argument):
                        chunk_text = _safe_decode(chunk)
                        if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                            chunk_text += ' '
                        yield f"data:{chunk_text}\n\n"
                    current_turn = 'for'

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    else:
        # Initial page load - render the template
        return render(request, 'hello_debate.html', {'debate_topic': debate_topic})

def _safe_decode(data):
    """Decode bytes to UTF-8, replacing invalid characters."""
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    return data

def run_debate(agent_for, agent_against, max_rounds=5):
    """Runs the debate and returns the log of arguments."""
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

    for round_num in range(1, max_rounds):
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

def generate_debate_stream(debate_log):
    """Generates the debate log as a stream."""
    for entry in debate_log:
        yield f"### {entry['side'].upper()}:\n{entry['text']}\n\n"
