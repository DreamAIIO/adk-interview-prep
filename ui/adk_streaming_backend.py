"""
Real-time ADK voice streaming backend.
Implements true bidirectional voice streaming using ADK's native capabilities.
"""
import asyncio
import logging
import json
import time
from typing import AsyncGenerator, Dict, Any, Optional
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Part, Content, Blob

logger = logging.getLogger(__name__)

class ADKVoiceStreamingServer:
    """
    Real-time voice streaming server using ADK's native capabilities.
    Handles WebSocket connections for bidirectional voice streaming.
    """
    
    def __init__(self, interview_manager):
        """Initialize the streaming server."""
        self.interview_manager = interview_manager
        self.app = FastAPI(title="ADK Voice Streaming Server")
        self.active_sessions = {}
        self.session_service = InMemorySessionService()
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes for voice streaming."""
        
        @self.app.get("/")
        async def get_voice_interface():
            """Serve the voice interface HTML."""
            return HTMLResponse(self.get_voice_html())
        
        @self.app.websocket("/voice_stream/{session_id}")
        async def voice_stream_endpoint(websocket: WebSocket, session_id: str):
            """Handle real-time voice streaming via WebSocket."""
            await self.handle_voice_stream(websocket, session_id)
    
    async def handle_voice_stream(self, websocket: WebSocket, session_id: str):
        """Handle individual voice streaming session."""
        await websocket.accept()
        
        try:
            # Initialize ADK streaming session
            session = await self.session_service.create_session(
                app_name="voice_interview_coach",
                user_id=f"voice_user_{session_id}",
                session_id=session_id
            )
            
            # Setup ADK runner for voice agent
            runner = InMemoryRunner(
                app_name="voice_interview_coach",
                agent=self.interview_manager.voice_agent.voice_agent
            )
            
            # Configure for real-time audio streaming
            run_config = RunConfig(
                response_modalities=["AUDIO", "TEXT"],
                enable_audio_streaming=True
            )
            
            # Create live request queue for bidirectional streaming
            live_request_queue = LiveRequestQueue()
            
            # Start ADK live streaming
            live_events = runner.run_live(
                session=session,
                live_request_queue=live_request_queue,
                run_config=run_config
            )
            
            # Store session info
            self.active_sessions[session_id] = {
                'websocket': websocket,
                'session': session,
                'runner': runner,
                'live_request_queue': live_request_queue,
                'start_time': time.time()
            }
            
            # Send initial greeting
            await self.send_initial_greeting(websocket, live_request_queue)
            
            # Handle bidirectional streaming
            await asyncio.gather(
                self.handle_incoming_audio(websocket, session_id, live_request_queue),
                self.handle_outgoing_responses(websocket, session_id, live_events)
            )
            
        except WebSocketDisconnect:
            logger.info(f"Voice session {session_id} disconnected")
        except Exception as e:
            logger.error(f"Error in voice streaming session {session_id}: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": f"Streaming error: {str(e)}"
            })
        finally:
            # Cleanup session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def send_initial_greeting(self, websocket: WebSocket, live_request_queue: LiveRequestQueue):
        """Send initial greeting to start the conversation."""
        greeting = """
        Hi there! I'm your AI interview coach with real-time voice capabilities. 
        I can help you practice interview questions, provide feedback, and conduct mock interviews.
        
        Just speak naturally - I'm listening and will respond in real-time!
        """
        
        await websocket.send_json({
            "type": "agent_greeting",
            "content": greeting,
            "timestamp": time.time()
        })
    
    async def handle_incoming_audio(self, websocket: WebSocket, session_id: str, live_request_queue: LiveRequestQueue):
        """Handle incoming audio from the client."""
        try:
            while True:
                # Receive audio data from WebSocket
                data = await websocket.receive_bytes()
                
                # Create audio blob for ADK
                audio_blob = Blob(
                    mime_type="audio/wav",  # Assuming WAV format
                    data=data
                )
                
                # Create content with audio
                audio_content = Content(
                    role="user",
                    parts=[Part(inline_data=audio_blob)]
                )
                
                # Send to ADK for processing
                await live_request_queue.put(audio_content)
                
                # Send acknowledgment to client
                await websocket.send_json({
                    "type": "audio_received",
                    "timestamp": time.time(),
                    "session_id": session_id
                })
                
        except WebSocketDisconnect:
            logger.info(f"Client disconnected from session {session_id}")
        except Exception as e:
            logger.error(f"Error handling incoming audio for session {session_id}: {str(e)}")
    
    async def handle_outgoing_responses(self, websocket: WebSocket, session_id: str, live_events):
        """Handle outgoing responses from ADK."""
        try:
            async for event in live_events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        
                        # Handle text responses
                        if part.text:
                            await websocket.send_json({
                                "type": "agent_text_response",
                                "content": part.text,
                                "timestamp": time.time(),
                                "session_id": session_id
                            })
                        
                        # Handle audio responses
                        elif hasattr(part, 'inline_data') and part.inline_data:
                            # Send audio response
                            await websocket.send_json({
                                "type": "agent_audio_response",
                                "audio_data": part.inline_data.data.hex(),  # Send as hex string
                                "mime_type": part.inline_data.mime_type,
                                "timestamp": time.time(),
                                "session_id": session_id
                            })
                
                # Handle session completion
                if hasattr(event, 'finish_reason') and event.finish_reason:
                    await websocket.send_json({
                        "type": "session_complete",
                        "reason": event.finish_reason,
                        "timestamp": time.time()
                    })
                    break
                    
        except Exception as e:
            logger.error(f"Error handling outgoing responses for session {session_id}: {str(e)}")
    
    def get_voice_html(self) -> str:
        """Get the HTML for the voice interface."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ADK Real-Time Voice Streaming</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                .status { padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center; font-weight: bold; }
                .connected { background: #d4edda; color: #155724; }
                .disconnected { background: #f8d7da; color: #721c24; }
                .recording { background: #fff3cd; color: #856404; }
                .conversation { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
                .message { margin: 5px 0; padding: 8px; border-radius: 5px; }
                .user-message { background: #e3f2fd; text-align: right; }
                .agent-message { background: #f3e5f5; text-align: left; }
                .controls { text-align: center; margin: 20px 0; }
                .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                .btn-primary { background: #007bff; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-success { background: #28a745; color: white; }
                .btn:disabled { opacity: 0.6; cursor: not-allowed; }
                .pulse { animation: pulse 1.5s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎙️ ADK Real-Time Voice Streaming</h1>
                <div id="status" class="status disconnected">Not Connected</div>
                
                <div class="controls">
                    <button id="connectBtn" class="btn btn-primary">Connect to ADK</button>
                    <button id="recordBtn" class="btn btn-success" disabled>Start Recording</button>
                    <button id="stopBtn" class="btn btn-danger" disabled>Stop Recording</button>
                </div>
                
                <div id="conversation" class="conversation">
                    <div class="message agent-message">
                        <strong>ADK Coach:</strong> Click "Connect to ADK" to start real-time voice streaming!
                    </div>
                </div>
                
                <div>
                    <h3>🎯 Voice Commands:</h3>
                    <ul>
                        <li>"Give me a practice question"</li>
                        <li>"Help me with problem solving"</li>
                        <li>"Evaluate my last answer"</li>
                        <li>"Switch to mock interview mode"</li>
                    </ul>
                </div>
            </div>
            
            <script>
                let websocket = null;
                let mediaRecorder = null;
                let audioStream = null;
                let isRecording = false;
                
                const statusDiv = document.getElementById('status');
                const conversationDiv = document.getElementById('conversation');
                const connectBtn = document.getElementById('connectBtn');
                const recordBtn = document.getElementById('recordBtn');
                const stopBtn = document.getElementById('stopBtn');
                
                // Generate session ID
                const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
                
                connectBtn.addEventListener('click', connectToADK);
                recordBtn.addEventListener('click', startRecording);
                stopBtn.addEventListener('click', stopRecording);
                
                async function connectToADK() {
                    try {
                        const wsUrl = `ws://localhost:8000/voice_stream/${sessionId}`;
                        websocket = new WebSocket(wsUrl);
                        
                        websocket.onopen = function() {
                            statusDiv.className = 'status connected';
                            statusDiv.textContent = '🟢 Connected to ADK - Ready for Voice!';
                            connectBtn.disabled = true;
                            recordBtn.disabled = false;
                        };
                        
                        websocket.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            handleADKResponse(data);
                        };
                        
                        websocket.onclose = function() {
                            statusDiv.className = 'status disconnected';
                            statusDiv.textContent = '🔴 Disconnected from ADK';
                            connectBtn.disabled = false;
                            recordBtn.disabled = true;
                            stopBtn.disabled = true;
                        };
                        
                        websocket.onerror = function(error) {
                            console.error('WebSocket error:', error);
                            addMessage('agent', 'Connection error occurred');
                        };
                        
                    } catch (error) {
                        console.error('Failed to connect:', error);
                        addMessage('agent', 'Failed to connect to ADK streaming server');
                    }
                }
                
                async function startRecording() {
                    try {
                        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm;codecs=opus' });
                        
                        mediaRecorder.ondataavailable = function(event) {
                            if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {
                                // Send audio data to ADK
                                websocket.send(event.data);
                            }
                        };
                        
                        mediaRecorder.start(1000); // Send chunks every 1 second
                        isRecording = true;
                        
                        statusDiv.className = 'status recording pulse';
                        statusDiv.textContent = '🎙️ Recording - Speak now!';
                        recordBtn.disabled = true;
                        stopBtn.disabled = false;
                        
                        addMessage('system', 'Started recording - speak your question or response');
                        
                    } catch (error) {
                        console.error('Failed to start recording:', error);
                        addMessage('agent', 'Failed to access microphone');
                    }
                }
                
                function stopRecording() {
                    if (mediaRecorder && isRecording) {
                        mediaRecorder.stop();
                        audioStream.getTracks().forEach(track => track.stop());
                        isRecording = false;
                        
                        statusDiv.className = 'status connected';
                        statusDiv.textContent = '🟢 Connected - Processing your audio...';
                        recordBtn.disabled = false;
                        stopBtn.disabled = true;
                        
                        addMessage('system', 'Stopped recording - ADK is processing...');
                    }
                }
                
                function handleADKResponse(data) {
                    switch(data.type) {
                        case 'agent_greeting':
                            addMessage('agent', data.content);
                            break;
                        case 'agent_text_response':
                            addMessage('agent', data.content);
                            break;
                        case 'agent_audio_response':
                            addMessage('agent', '[Audio Response] ' + data.content);
                            // TODO: Play audio response
                            playAudioResponse(data.audio_data, data.mime_type);
                            break;
                        case 'audio_received':
                            addMessage('system', 'ADK received your audio - generating response...');
                            break;
                        case 'session_complete':
                            addMessage('system', 'Session completed');
                            break;
                        case 'error':
                            addMessage('agent', 'Error: ' + data.message);
                            break;
                    }
                }
                
                function addMessage(sender, content) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + (sender === 'user' ? 'user-message' : 'agent-message');
                    
                    const timestamp = new Date().toLocaleTimeString();
                    const icon = sender === 'user' ? '🗣️' : sender === 'agent' ? '🤖' : '⚙️';
                    
                    messageDiv.innerHTML = `<strong>${icon} ${sender.charAt(0).toUpperCase() + sender.slice(1)}:</strong> ${content} <small style="color: #666;">[${timestamp}]</small>`;
                    
                    conversationDiv.appendChild(messageDiv);
                    conversationDiv.scrollTop = conversationDiv.scrollHeight;
                }
                
                function playAudioResponse(hexData, mimeType) {
                    try {
                        // Convert hex string back to binary
                        const bytes = new Uint8Array(hexData.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
                        const blob = new Blob([bytes], { type: mimeType });
                        const audioUrl = URL.createObjectURL(blob);
                        
                        const audio = new Audio(audioUrl);
                        audio.play().catch(e => console.error('Error playing audio:', e));
                        
                        // Cleanup
                        audio.onended = () => URL.revokeObjectURL(audioUrl);
                    } catch (error) {
                        console.error('Error playing audio response:', error);
                    }
                }
            </script>
        </body>
        </html>
        """
    
    def run_server(self, host: str = "localhost", port: int = 8000):
        """Run the voice streaming server."""
        logger.info(f"Starting ADK Voice Streaming Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Integration with Streamlit
def create_adk_streaming_server(interview_manager):
    """Create and return the ADK streaming server instance."""
    return ADKVoiceStreamingServer(interview_manager)

def get_real_time_voice_interface_url(port: int = 8000) -> str:
    """Get the URL for the real-time voice interface."""
    return f"http://localhost:{port}"