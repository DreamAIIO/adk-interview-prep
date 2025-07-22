"""
Streamlit Voice Integration with real ADK streaming.
Implements WebRTC microphone access + LiveRequestQueue streaming.
"""
import streamlit as st
import asyncio
import json
import base64
import time
from typing import Dict, Any
import streamlit.components.v1 as components

def render_real_voice_streaming(self):
    """Render real-time voice streaming interface with ADK integration."""
    st.header("🎙️ Real-Time ADK Voice Streaming")
    
    if not st.session_state.voice_enabled:
        st.warning("⚠️ Voice is disabled. Enable it in the sidebar to use this feature.")
        return
    
    st.success("🚀 **Real ADK Live Streaming** - True bidirectional voice with LiveRequestQueue")
    
    # Initialize streaming state
    if 'voice_streaming_active' not in st.session_state:
        st.session_state.voice_streaming_active = False
    if 'voice_events' not in st.session_state:
        st.session_state.voice_events = []
    if 'streaming_task' not in st.session_state:
        st.session_state.streaming_task = None
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎤 Live Voice Control")
        
        # Streaming controls
        if not st.session_state.voice_streaming_active:
            if st.button("🔴 Start Live Voice Streaming", type="primary", key="start_real_streaming"):
                self._start_real_voice_streaming()
        else:
            st.success("🟢 **LIVE STREAMING ACTIVE**")
            
            # Real-time status
            status = st.session_state.interview_manager.voice_agent.get_streaming_status()
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #28a745, #20c997); 
                        color: white; padding: 1rem; border-radius: 10px; 
                        text-align: center; animation: pulse 2s infinite;">
                🎙️ <strong>SPEAK NOW - ADK IS LISTENING</strong><br>
                <small>Model: {status.get('model', 'Unknown')} | Session Active: {status.get('active', False)}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⏹️ Stop Live Streaming", type="secondary", key="stop_real_streaming"):
                self._stop_real_voice_streaming()
        
        # Test controls
        st.markdown("---")
        st.subheader("🧪 Test Controls")
        
        if st.session_state.voice_streaming_active:
            # Text input for testing
            test_text = st.text_input("Test with text:", key="voice_test_input")
            if st.button("📤 Send Text to Stream") and test_text:
                self._send_text_to_stream(test_text)
            
            # Audio file test
            st.markdown("**Test with audio file:**")
            uploaded_audio = st.file_uploader(
                "Upload test audio:", 
                type=['wav', 'mp3', 'm4a'], 
                key="test_audio_upload"
            )
            if uploaded_audio and st.button("🎵 Send Audio to Stream"):
                self._send_audio_to_stream(uploaded_audio)
        
        # WebRTC Interface
        st.markdown("---")
        st.subheader("🌐 Browser Microphone")
        
        if st.session_state.voice_streaming_active:
            # Embed WebRTC interface
            self._render_webrtc_interface()
        else:
            st.info("Start streaming to enable microphone access")
    
    with col2:
        st.subheader("💬 Live Event Stream")
        
        # Real-time event display
        event_container = st.container(height=500)
        with event_container:
            if st.session_state.voice_streaming_active:
                # Display streaming events
                events = st.session_state.voice_events[-20:]  # Last 20 events
                
                if not events:
                    st.info("🎙️ Waiting for voice input...")
                
                for event in events:
                    timestamp = time.strftime("%H:%M:%S", time.localtime(event.get('timestamp', time.time())))
                    event_type = event.get('event_type', 'unknown')
                    
                    if event_type == 'text_response':
                        st.markdown(f"""
                        <div style="background: #e8f5e8; padding: 0.8rem; margin: 0.3rem 0; 
                                    border-radius: 8px; border-left: 4px solid #28a745;">
                            <strong>🤖 ADK Response:</strong> {event.get('content', '')}<br>
                            <small style="color: #666;">[{timestamp}]</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif event_type == 'audio_response':
                        st.markdown(f"""
                        <div style="background: #fff3e0; padding: 0.8rem; margin: 0.3rem 0; 
                                    border-radius: 8px; border-left: 4px solid #ff9800;">
                            <strong>🔊 Audio Response:</strong> Voice message received<br>
                            <small style="color: #666;">[{timestamp}]</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Audio playback
                        if event.get('audio_data'):
                            try:
                                audio_bytes = base64.b64decode(event['audio_data'])
                                st.audio(audio_bytes, format='audio/wav')
                            except Exception as e:
                                st.error(f"Audio playback error: {e}")
                    
                    elif event_type == 'user_input':
                        st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 0.8rem; margin: 0.3rem 0; 
                                    border-radius: 8px; border-left: 4px solid #2196f3;">
                            <strong>🎙️ You:</strong> {event.get('content', 'Audio input')}<br>
                            <small style="color: #666;">[{timestamp}]</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif event.get('type') == 'error':
                        st.error(f"❌ Error: {event.get('message', 'Unknown error')}")
                
                # Auto-refresh for real-time updates
                if st.session_state.voice_streaming_active:
                    time.sleep(0.1)  # Small delay
                    st.rerun()
            else:
                st.info("🎙️ Start voice streaming to see live events here!")
    
    # Technical details
    with st.expander("🔧 Real ADK Streaming Implementation"):
        st.markdown("""
        ### How Real ADK Streaming Works:
        
        **1. LiveRequestQueue Pattern:**
        ```python
        live_request_queue = LiveRequestQueue()
        run_config = RunConfig(response_modalities=["AUDIO"])
        live_events = runner.run_live(session, live_request_queue, run_config)
        ```
        
        **2. Bidirectional Flow:**
        - Browser microphone → WebRTC → Streamlit → LiveRequestQueue
        - ADK processes audio with gemini-2.0-flash-live-001
        - live_events stream → Audio responses → Browser playback
        
        **3. Real-time Event Processing:**
        - Async generator processes events as they arrive
        - Text and audio responses handled separately
        - Continuous streaming without file uploads
        
        **4. Browser Integration:**
        - WebRTC for microphone access
        - Real-time audio streaming to backend
        - Audio playback of responses
        """)

def _render_webrtc_interface(self):
    """Render WebRTC interface for microphone access."""
    webrtc_html = """
    <div id="voice-interface" style="text-align: center; padding: 20px; border: 2px dashed #ccc; border-radius: 10px;">
        <h4>🎙️ Live Microphone Interface</h4>
        <button id="startRecord" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">
            Start Recording
        </button>
        <button id="stopRecord" style="background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;" disabled>
            Stop Recording
        </button>
        <div id="status" style="margin-top: 10px; font-weight: bold;">Ready to record</div>
        <div id="visualizer" style="margin-top: 10px; height: 50px; background: #f0f0f0; border-radius: 5px;"></div>
    </div>
    
    <script>
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    const startBtn = document.getElementById('startRecord');
    const stopBtn = document.getElementById('stopRecord');
    const status = document.getElementById('status');
    
    startBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
                sendAudioToStreamlit(audioBlob);
            };
            
            mediaRecorder.start(1000); // Collect data every 1 second
            isRecording = true;
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = '🔴 Recording... Speak now!';
            status.style.color = '#dc3545';
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            status.textContent = '❌ Microphone access denied';
            status.style.color = '#dc3545';
        }
    }
    
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            
            startBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = '⏹️ Processing audio...';
            status.style.color = '#007bff';
        }
    }
    
    function sendAudioToStreamlit(audioBlob) {
        // Convert blob to base64 and send to Streamlit
        const reader = new FileReader();
        reader.onloadend = function() {
            const base64data = reader.result.split(',')[1];
            
            // Send to Streamlit via custom event
            window.parent.postMessage({
                type: 'audio_data',
                data: base64data,
                timestamp: Date.now()
            }, '*');
            
            status.textContent = '✅ Audio sent to ADK!';
            status.style.color = '#28a745';
            
            setTimeout(() => {
                status.textContent = 'Ready to record';
                status.style.color = '#000';
            }, 2000);
        };
        reader.readAsDataURL(audioBlob);
    }
    
    // Visual feedback
    function updateVisualizer() {
        // Simple audio visualizer could be added here
        if (isRecording) {
            const visualizer = document.getElementById('visualizer');
            visualizer.style.background = `linear-gradient(90deg, 
                hsl(${Math.random() * 120}, 70%, 50%) 0%, 
                hsl(${Math.random() * 120}, 70%, 50%) 100%)`;
        }
    }
    
    setInterval(updateVisualizer, 100);
    </script>
    """
    
    components.html(webrtc_html, height=200)

def _start_real_voice_streaming(self):
    """Start real ADK voice streaming session."""
    try:
        # Start streaming task
        async def start_streaming():
            voice_agent = st.session_state.interview_manager.voice_agent
            
            async for event in voice_agent.start_voice_streaming():
                # Add event to session state
                st.session_state.voice_events.append(event)
                
                # Limit event history
                if len(st.session_state.voice_events) > 100:
                    st.session_state.voice_events = st.session_state.voice_events[-50:]
        
        # Run streaming in background
        st.session_state.streaming_task = asyncio.create_task(start_streaming())
        st.session_state.voice_streaming_active = True
        
        st.success("🚀 Real-time voice streaming started!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to start voice streaming: {str(e)}")

def _stop_real_voice_streaming(self):
    """Stop real ADK voice streaming session."""
    try:
        # Stop the streaming
        if hasattr(st.session_state, 'interview_manager'):
            st.session_state.interview_manager.voice_agent.stop_voice_streaming()
        
        # Cancel background task
        if st.session_state.streaming_task:
            st.session_state.streaming_task.cancel()
            st.session_state.streaming_task = None
        
        st.session_state.voice_streaming_active = False
        
        st.info("⏹️ Voice streaming stopped.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error stopping voice streaming: {str(e)}")

def _send_text_to_stream(self, text: str):
    """Send text to the live streaming session."""
    try:
        async def send_text():
            voice_agent = st.session_state.interview_manager.voice_agent
            success = await voice_agent.send_text_to_stream(text)
            
            if success:
                # Add user event
                st.session_state.voice_events.append({
                    'event_type': 'user_input',
                    'content': text,
                    'timestamp': time.time()
                })
        
        asyncio.create_task(send_text())
        st.success(f"✅ Sent: {text}")
        
    except Exception as e:
        st.error(f"Failed to send text: {str(e)}")

def _send_audio_to_stream(self, uploaded_audio):
    """Send uploaded audio to the live streaming session."""
    try:
        audio_bytes = uploaded_audio.read()
        
        async def send_audio():
            voice_agent = st.session_state.interview_manager.voice_agent
            success = await voice_agent.send_audio_to_stream(audio_bytes, uploaded_audio.type)
            
            if success:
                # Add user event
                st.session_state.voice_events.append({
                    'event_type': 'user_input',
                    'content': f'Audio file: {uploaded_audio.name}',
                    'timestamp': time.time()
                })
        
        asyncio.create_task(send_audio())
        st.success(f"✅ Sent audio: {uploaded_audio.name}")
        
    except Exception as e:
        st.error(f"Failed to send audio: {str(e)}")

# Add these methods to the SimplifiedInterviewUI class
def add_voice_streaming_methods(ui_class):
    """Add voice streaming methods to the UI class."""
    ui_class.render_real_voice_streaming = render_real_voice_streaming
    ui_class._render_webrtc_interface = _render_webrtc_interface
    ui_class._start_real_voice_streaming = _start_real_voice_streaming
    ui_class._stop_real_voice_streaming = _stop_real_voice_streaming
    ui_class._send_text_to_stream = _send_text_to_stream
    ui_class._send_audio_to_stream = _send_audio_to_stream