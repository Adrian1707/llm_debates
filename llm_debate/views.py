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
    debate_topic = request.GET.get('debate_topic')
    if not debate_topic:
        debate_topic = "Should a dog be allowed to be President"
    
    # Check if this is an SSE request or the initial page load
    if request.headers.get('accept') == 'text/event-stream':
        agent_for = DebateAgent(for_or_against='for', topic=debate_topic)
        agent_against = DebateAgent(for_or_against='against', topic=debate_topic)

        def event_stream():
            # Opening statement FOR side
            yield "data:### FOR:\n\n"
            for chunk in agent_for.respond("Please provide your opening statement."):
                chunk_text = _safe_decode(chunk)
                if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                    chunk_text += ' '
                yield f"data:{chunk_text}\n\n"

            # Check if previous_arguments exists and is non-empty
            if hasattr(agent_for, 'previous_arguments') and agent_for.previous_arguments:
                previous_arg = agent_for.previous_arguments[-1]
            else:
                # Handle the case where previous_arguments is missing or empty
                previous_arg = ""  # Or set to some default value

            # Opening statement AGAINST side responds to FOR's opener
            yield "data:### AGAINST:\n\n"
            for chunk in agent_against.respond(previous_arg):
                # Ensure each chunk is properly formatted with spaces
                chunk_text = _safe_decode(chunk)
                # Add a space after punctuation if needed
                if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                    chunk_text += ' '
                yield f"data:{chunk_text}\n\n"

            current_turn = 'for'
            max_rounds = 5

            for round_num in range(1, max_rounds):
                if current_turn == 'for':
                    # Check if previous_arguments exists and is non-empty
                    opponent_argument = (
                        agent_against.previous_arguments[-1]
                        if hasattr(agent_against, 'previous_arguments') and agent_against.previous_arguments
                        else ""  # Or some default prompt
                    )
                    yield "data:### FOR:\n\n"
                    for chunk in agent_for.respond(opponent_argument):
                        chunk_text = _safe_decode(chunk)
                        if chunk_text and chunk_text[-1] in ['.', ',', '!', '?', ':', ';'] and len(chunk_text) > 1:
                            chunk_text += ' '
                        yield f"data:{chunk_text}\n\n"
                    current_turn = 'against'
                else:
                    # Similarly for the 'against' side
                    opponent_argument = (
                        agent_for.previous_arguments[-1]
                        if hasattr(agent_for, 'previous_arguments') and agent_for.previous_arguments
                        else ""  # Or some default prompt
                    )
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
        return render(request, 'debate.html', {'debate_topic': debate_topic})

def _safe_decode(data):
    """Decode bytes to UTF-8, replacing invalid characters."""
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    return data
