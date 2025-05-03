from django.shortcuts import render
from django.contrib import admin
from llm_debate.debate_agent import DebateAgent
import os
from . import views

from django.http import StreamingHttpResponse
from django.shortcuts import render

def submit_topic(request):
    """Render a form for the user to submit a debate topic."""
    return render(request, 'submit_topic.html')

def debate(request):
    """
    Django view that handles a debate between two AI agents.
    Supports both initial page load and server-sent events (SSE).
    """
    debate_topic = request.GET.get('debate_topic', "Should a dog be allowed to be President")
    
    if request.headers.get('accept') == 'text/event-stream':
        return handle_debate_stream(debate_topic)
    else:
        return render(request, 'debate.html', {'debate_topic': debate_topic})


def handle_debate_stream(debate_topic):
    """Handle the SSE stream for a debate on the given topic."""
    agent_for = DebateAgent(for_or_against='for', topic=debate_topic)
    agent_against = DebateAgent(for_or_against='against', topic=debate_topic)
    
    return StreamingHttpResponse(
        generate_debate_stream(agent_for, agent_against), 
        content_type='text/event-stream'
    )


def generate_debate_stream(agent_for, agent_against):
    """Generate the debate content as a stream of SSE events."""
    # Opening statements
    yield from stream_agent_response("### FOR:\n\n", agent_for, "Please provide your opening statement.")
    
    opening_argument = get_last_argument(agent_for)
    yield from stream_agent_response("### AGAINST:\n\n", agent_against, opening_argument)
    
    # Subsequent rounds
    current_turn = 'for'
    max_rounds = 5
    
    for _ in range(1, max_rounds):
        if current_turn == 'for':
            opponent_argument = get_last_argument(agent_against)
            yield from stream_agent_response("### FOR:\n\n", agent_for, opponent_argument)
            current_turn = 'against'
        else:
            opponent_argument = get_last_argument(agent_for)
            yield from stream_agent_response("### AGAINST:\n\n", agent_against, opponent_argument)
            current_turn = 'for'


def stream_agent_response(header, agent, prompt):
    """Stream an agent's response with proper formatting."""
    yield f"data:{header}\n\n"
    
    for chunk in agent.respond(prompt):
        chunk_text = safe_decode(chunk)
        if should_add_space(chunk_text):
            chunk_text += ' '
        yield f"data:{chunk_text}\n\n"


def get_last_argument(agent):
    """Safely get the last argument from an agent."""
    if hasattr(agent, 'previous_arguments') and agent.previous_arguments:
        return agent.previous_arguments[-1]
    return ""


def should_add_space(text):
    """Determine if a space should be added after the text."""
    return (text and 
            text[-1] in ['.', ',', '!', '?', ':', ';'] and 
            len(text) > 1)


def safe_decode(data):
    """Decode bytes to UTF-8, replacing invalid characters."""
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    return data
