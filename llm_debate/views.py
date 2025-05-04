from django.shortcuts import render
from django.contrib import admin
from llm_debate.debate_agent import DebateAgent
import os
from . import views

from django.http import StreamingHttpResponse
from django.shortcuts import render
import time
from django.conf import settings

def submit_topic(request):
    """Render a form for the user to submit a debate topic."""
    return render(request, 'submit_topic.html')

def debate(request):
    """
    Django view that handles a debate between two AI agents.
    Supports both initial page load and server-sent events (SSE).
    """
    debate_topic = request.GET.get('debate_topic', "Should a dog be allowed to be President")
    
    # Get streaming speed from request or use default
    stream_speed = request.GET.get('stream_speed', 'slow')
    
    if request.headers.get('accept') == 'text/event-stream':
        return handle_debate_stream(debate_topic, stream_speed)
    else:
        return render(request, 'debate.html', {
            'debate_topic': debate_topic,
            'stream_speed': stream_speed
        })


def handle_debate_stream(debate_topic, stream_speed='slow'):
    """Handle the SSE stream for a debate on the given topic."""
    agent_for = DebateAgent(for_or_against='for', topic=debate_topic)
    agent_against = DebateAgent(for_or_against='against', topic=debate_topic)
    
    return StreamingHttpResponse(
        generate_debate_stream(agent_for, agent_against, stream_speed), 
        content_type='text/event-stream'
    )


def generate_debate_stream(agent_for, agent_against, stream_speed='slow'):
    """Generate the debate content as a stream of SSE events."""
    # Opening statements
    yield from stream_agent_response("### FOR:\n\n", agent_for, "Please provide your opening statement.", stream_speed)
    
    opening_argument = get_last_argument(agent_for)
    yield from stream_agent_response("### AGAINST:\n\n", agent_against, opening_argument, stream_speed)
    
    # Subsequent rounds
    current_turn = 'for'
    max_rounds = 5
    
    for _ in range(1, max_rounds):
        if current_turn == 'for':
            opponent_argument = get_last_argument(agent_against)
            yield from stream_agent_response("### FOR:\n\n", agent_for, opponent_argument, stream_speed)
            current_turn = 'against'
        else:
            opponent_argument = get_last_argument(agent_for)
            yield from stream_agent_response("### AGAINST:\n\n", agent_against, opponent_argument, stream_speed)
            current_turn = 'for'


def stream_agent_response(header, agent, prompt, stream_speed='slow'):
    """
    Stream an agent's response with proper formatting and controlled speed.
    
    Args:
        header: The header text to display before the response
        agent: The DebateAgent that will generate the response
        prompt: The prompt to send to the agent
        stream_speed: Controls streaming speed - 'slow', 'medium', 'fast', or 'instant'
    """
    yield f"data:{header}\n\n"
    
    # Get delay in seconds based on stream_speed
    delay = get_stream_delay(stream_speed)
    
    for chunk in agent.respond(prompt):
        chunk_text = safe_decode(chunk)
        if should_add_space(chunk_text):
            chunk_text += ' '
        
        yield f"data:{chunk_text}\n\n"
        
        # Add delay if needed (skip for empty chunks)
        if delay > 0 and chunk_text.strip():
            time.sleep(delay)


def get_stream_delay(stream_speed):
    """
    Get the appropriate delay in seconds based on the stream speed setting.
    
    Can be configured in Django settings or uses these defaults:
    - slow: 0.1s between chunks
    - medium: 0.05s between chunks
    - fast: 0.02s between chunks
    - instant: No delay
    """
    # Get delay settings from Django settings or use defaults
    delay_settings = getattr(settings, 'STREAM_DELAY_SETTINGS', {
        'slow': 0.3,
        'medium': 0.2, 
        'fast': 0.1,
        'instant': 0
    })
    
    # Default to medium if an invalid speed is provided
    return delay_settings.get(stream_speed, delay_settings['slow'])


def get_last_argument(agent):
    """Safely get the last argument from an agent."""
    if hasattr(agent, 'previous_arguments') and agent.previous_arguments:
        return agent.previous_arguments[-1]
    return ""

def should_add_new_line(s: str) -> bool:
    """
    Check if the string has the format 'part1.part2' with exactly one dot,
    and both parts are non-empty.

    Args:
        s (str): The input string to check.

    Returns:
        bool: True if the format is valid, False otherwise.
    """
    # Split the string by '.' and check that there's exactly one split
    parts = s.split('.')
    
    # Check for exactly two parts, and both are non-empty
    return len(parts) == 2 and all(part.strip() for part in parts)

def should_add_space(text):
    """
    Determine if a space should be added after the text.
    Handles punctuation and improves spacing around numbers.
    """
    if not text or len(text) <= 1:
        return False

    # Add space after punctuation
    if text[-1] in ['.', '. ' ',', '!', '?', ':', ';', '-']:
        return True
    
    # Check for number-word boundaries (e.g., "300,000people" → "300,000 people")
    # Look for patterns where the last character is a digit and next chunk might start with a letter
    if text[-1].isdigit():
        return True
    
    # Check for word-number boundaries (e.g., "asof2023" → "as of 2023")
    # This would need to be handled differently since we don't see the next chunk yet
    
    return False


def safe_decode(data):
    """Decode bytes to UTF-8, replacing invalid characters."""
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    return data