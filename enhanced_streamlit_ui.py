"""
Enhanced Streamlit App - Complete Natural Voice Integration with Speech Coaching
Latest version with enhanced voice workflow supporting parallel content and delivery analysis.
"""
import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from typing import Dict, List, Any, Optional

import logging
logger = logging.getLogger(__name__)

from core.job_analyzer import JobAnalyzer
from enhanced_streamlit_voice_client import EnhancedStreamlitVoiceClient
from config import APP_NAME, CORE_COMPETENCIES

# Configure page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with speech coaching styles
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .modern-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin: 1rem 0;
    }
    
    .enhanced-feature-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .speech-coaching-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    .delivery-score-card {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #333;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .question-card {
        background: linear-gradient(135deg, #4169e1 0%, #667eea 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .competency-tag {
        display: inline-block;
        background: #f0f8ff;
        color: #4169e1;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
        margin: 0.2rem;
    }
    
    .enhanced-voice-indicator {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .parallel-analysis-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

class EnhancedInterviewApp:
    """Enhanced interview app with speech coaching and parallel analysis."""
    
    def __init__(self):
        """Initialize the enhanced app."""
        # Initialize enhanced voice client
        if 'enhanced_voice_client' not in st.session_state:
            st.session_state.enhanced_voice_client = EnhancedStreamlitVoiceClient()
        self.voice_client = st.session_state.enhanced_voice_client
        
        # Initialize session state
        self.initialize_session_state()
        
        # Check API server status
        self.check_api_server_status()
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        defaults = {
            'job_analyzer': None,
            'job_info': None,
            'current_question': None,
            'current_evaluation': None,
            'evaluation_results': [],
            'practice_test_questions': [],
            'practice_test_answers': {},
            'practice_test_evaluations': {},
            'practice_test_completed': False,
            'chat_history': [],
            'performance_analysis': None,
            'enhanced_workflow_ready': False,
            'speech_coaching_available': False,
            'parallel_analysis_enabled': False,
            'api_server_status': 'unknown'
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def check_api_server_status(self):
        """Check if enhanced API server is running."""
        try:
            import requests
            response = requests.get("http://localhost:8002/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                st.session_state.api_server_status = 'running'
                
                # Check for enhanced features
                features = data.get('features', {})
                st.session_state.speech_coaching_available = features.get('speech_coaching', False)
                st.session_state.parallel_analysis_enabled = features.get('parallel_content_delivery_analysis', False)
            else:
                st.session_state.api_server_status = 'error'
        except:
            st.session_state.api_server_status = 'offline'
    
    def render_header(self):
        """Render enhanced application header."""
        st.markdown(f"""
        <div class="main-header">
            <h1>🎯 {APP_NAME}</h1>
            <p style="font-size: 1.1em; margin: 10px 0; opacity: 0.9;">
                AI-Powered Interview Preparation with Advanced Voice Analysis & Speech Coaching
            </p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    🎤 Enhanced Voice Analysis
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    🎯 Speech Coaching
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    ⚡ Parallel Processing
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">
                    🤖 ADK Powered
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render enhanced sidebar with speech coaching status."""
        with st.sidebar:
            st.title("🎯 Enhanced Interview Dashboard")
            
            # Enhanced server status
            self.render_enhanced_server_status()
            
            # Job status
            self.render_job_status()
            
            # Enhanced progress summary
            self.render_enhanced_progress_summary()
            
            # Speech coaching insights
            self.render_speech_coaching_insights()
            
            # Quick actions
            self.render_quick_actions()
    
    def render_enhanced_server_status(self):
        """Render enhanced server status with speech coaching capabilities."""
        st.markdown("### 🖥️ Enhanced System Status")
        
        if st.session_state.api_server_status == 'running':
            st.success("🟢 Enhanced API Server Online")
            
            # Enhanced features status
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.enhanced_workflow_ready:
                    st.success("🎤 Voice Analysis Ready")
                else:
                    st.info("🎤 Voice Initializing...")
            
            with col2:
                if st.session_state.speech_coaching_available:
                    st.success("🎯 Speech Coaching Ready")
                else:
                    st.info("🎯 Coaching Loading...")
            
            # Parallel analysis status
            if st.session_state.parallel_analysis_enabled:
                st.markdown('<div class="parallel-analysis-badge">⚡ Parallel Analysis Active</div>', unsafe_allow_html=True)
                st.caption("Content + Delivery analyzed simultaneously")
            else:
                st.caption("Sequential analysis mode")
                
        elif st.session_state.api_server_status == 'offline':
            st.error("🔴 Enhanced API Server Offline")
            st.caption("Start server: `python enhanced_voice_server.py`")
        else:
            st.warning("🟡 Checking Enhanced Server...")
        
        if st.button("🔄 Refresh Enhanced Status", use_container_width=True):
            self.check_api_server_status()
            st.rerun()
    
    def render_enhanced_progress_summary(self):
        """Enhanced progress summary with speech coaching metrics."""
        if st.session_state.evaluation_results:
            st.markdown("### 📊 Enhanced Progress Overview")
            
            total_questions = len(st.session_state.evaluation_results)
            avg_score = sum(e['score'] for e in st.session_state.evaluation_results) / total_questions
            
            # Enhanced analysis breakdown
            enhanced_count = sum(1 for e in st.session_state.evaluation_results 
                               if e.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation')
            voice_count = sum(1 for e in st.session_state.evaluation_results 
                            if e.get('transcription_metadata', {}).get('audio_processed', False) or
                               e.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation')
            delivery_coaching_count = sum(1 for e in st.session_state.evaluation_results 
                                        if e.get('enhanced_analysis', {}).get('delivery_analysis_available', False))
            
            # Metrics display
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Questions", total_questions)
                st.metric("Average Score", f"{avg_score:.1f}/10")
            
            with col2:
                st.metric("Voice Responses", voice_count)
                if delivery_coaching_count > 0:
                    st.metric("Speech Coaching", delivery_coaching_count)
            
            # Enhanced features usage
            if enhanced_count > 0:
                enhancement_rate = (enhanced_count / total_questions) * 100
                if enhancement_rate >= 50:
                    st.success(f"🎯 {enhanced_count}/{total_questions} enhanced evaluations ({enhancement_rate:.0f}%)")
                else:
                    st.info(f"🎯 {enhanced_count}/{total_questions} enhanced evaluations ({enhancement_rate:.0f}%)")
            
            # Delivery coaching insights
            if delivery_coaching_count > 0:
                coaching_rate = (delivery_coaching_count / total_questions) * 100
                st.markdown(f'<div class="speech-coaching-badge">🎤 {delivery_coaching_count} Speech Coaching Sessions ({coaching_rate:.0f}%)</div>', unsafe_allow_html=True)
    
    def render_speech_coaching_insights(self):
        """Render speech coaching performance insights."""
        if not st.session_state.evaluation_results:
            return
        
        # Extract delivery scores from enhanced evaluations
        delivery_scores = []
        for eval_data in st.session_state.evaluation_results:
            enhanced_analysis = eval_data.get('enhanced_analysis', {})
            if enhanced_analysis.get('delivery_analysis_available'):
                delivery_score = enhanced_analysis.get('delivery_score', 0)
                if delivery_score > 0:
                    delivery_scores.append(delivery_score)
        
        if delivery_scores:
            st.markdown("### 🎤 Speech Coaching Insights")
            
            avg_delivery = sum(delivery_scores) / len(delivery_scores)
            latest_delivery = delivery_scores[-1] if delivery_scores else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Delivery", f"{avg_delivery:.1f}/10")
            with col2:
                st.metric("Latest Delivery", f"{latest_delivery}/10")
            
            # Delivery trend
            if len(delivery_scores) >= 2:
                trend = delivery_scores[-1] - delivery_scores[0]
                if trend > 0.5:
                    st.success("📈 Delivery improving!")
                elif trend < -0.5:
                    st.warning("📉 Practice delivery skills")
                else:
                    st.info("➡️ Steady delivery performance")
            
            # Speaking tips summary
            recent_evaluations = [e for e in st.session_state.evaluation_results[-3:] 
                                if e.get('enhanced_analysis', {}).get('delivery_analysis_available')]
            
            if recent_evaluations:
                common_tips = []
                for eval_data in recent_evaluations:
                    tips = eval_data.get('enhanced_analysis', {}).get('speaking_tips', [])
                    common_tips.extend(tips)
                
                if common_tips:
                    st.markdown("**🎯 Recent Coaching Tips:**")
                    # Show most recent unique tip
                    unique_tips = list(dict.fromkeys(common_tips))  # Remove duplicates while preserving order
                    for tip in unique_tips[:2]:
                        st.caption(f"💡 {tip}")
    
    def render_main_content(self):
        """Render main content with enhanced features."""
        if not st.session_state.job_info:
            self.render_job_setup()
        else:
            self.render_enhanced_interview_interface()
    
    def render_enhanced_interview_interface(self):
        """Render enhanced interview interface with speech coaching."""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 AI Assistant", 
            "📝 Practice Questions", 
            "🎯 Practice Test", 
            "🎤 Speech Coaching",  # New tab
            "📊 Enhanced Analytics"
        ])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_enhanced_practice_questions()
        
        with tab3:
            self.render_enhanced_practice_test()
        
        with tab4:
            self.render_speech_coaching_tab()
        
        with tab5:
            self.render_enhanced_analytics()
    
    def render_enhanced_practice_questions(self):
        """Render practice questions with voice and coaching options."""
        st.markdown("## 📝 Practice Questions")
        
        # Question generation
        with st.container():
            st.markdown("### 🎯 Generate Question")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                competency = st.selectbox(
                    "Select Competency:",
                    options=st.session_state.job_info.get('competencies', CORE_COMPETENCIES),
                    key="enhanced_practice_competency"
                )
            
            with col2:
                difficulty = st.selectbox(
                    "Difficulty Level:",
                    options=["easy", "balanced", "challenging"],
                    index=1,
                    key="enhanced_practice_difficulty"
                )
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Generate", type="primary", use_container_width=True):
                    self.generate_enhanced_practice_question(competency, difficulty)
                    st.session_state.current_evaluation = None  # Clear previous evaluation
        
        # Features info (keep this, but remove "Enhanced" from heading)
        if st.session_state.speech_coaching_available:
            st.markdown("""
            <div class="enhanced-feature-card">
                <h4>🎯 Voice Analysis Available</h4>
                <p>Get comprehensive feedback on both content quality and speaking delivery!</p>
                <div>
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 10px; margin: 2px;">📝 Content Analysis</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 10px; margin: 2px;">🎤 Delivery Coaching</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 10px; margin: 2px;">⚡ Parallel Processing</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Current question with interface
        if st.session_state.current_question:
            self.render_enhanced_question_interface(
                st.session_state.current_question, 
                "enhanced_practice"
            )
        
        # Evaluation display
        if st.session_state.current_evaluation:
            st.markdown("---")
            st.markdown("### 📊 Evaluation Results")
            self.voice_client.render_enhanced_evaluation(st.session_state.current_evaluation)
    
    def render_enhanced_question_interface(self, question: Dict[str, Any], key_prefix: str, use_parallel_analysis: bool = True):
        """Render question interface with voice and coaching options."""
        self.render_enhanced_question_card(question)
        
        input_mode = self.voice_client.render_enhanced_input_mode_selector(f"{key_prefix}_input_mode")
        
        # Show parallel analysis option only for voice input
        parallel_analysis = False
        if input_mode == "voice" and st.session_state.parallel_analysis_enabled:
            parallel_analysis = st.checkbox(
                "Parallel Analysis",
                value=True,
                help="Analyze content and delivery simultaneously"
            )
        
        # Voice answer input
        answer_data, is_voice = self.voice_client.render_enhanced_answer_input(
            input_mode, 
            question, 
            f"{key_prefix}_answer"
        )
        
        # Show coaching info box ONLY if parallel analysis is checked, and only ONCE
        if input_mode == "voice" and parallel_analysis:
            st.markdown("""
            <div style="background: #166534; color: white; padding: 1.2em 1em; border-radius: 10px; margin-bottom: 1em;">
                <b>🎯 You'll receive coaching on:</b>
                <ul style='margin-bottom: 0;'>
                    <li>Speaking pace and rhythm</li>
                    <li>Clarity and articulation</li>
                    <li>Professional confidence</li>
                    <li>Industry communication style</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Submit button logic
        can_submit = False
        submit_text = ""
        
        if input_mode == "text":
            can_submit = answer_data and answer_data.strip()
            submit_text = "📤 Submit Text Response" if key_prefix.startswith("enhanced_practice") else "➡️ Submit & Continue"
        else:
            can_submit = answer_data is not None
            if st.session_state.speech_coaching_available:
                submit_text = "🎯 Submit for Analysis" if key_prefix.startswith("enhanced_practice") else "🎯 Submit Voice & Continue"
            else:
                submit_text = "🎤 Submit Voice Response" if key_prefix.startswith("enhanced_practice") else "🎤 Submit Voice & Continue"
        
        if can_submit:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(submit_text, type="primary", use_container_width=True):
                    if key_prefix.startswith("enhanced_practice"):
                        self.evaluate_enhanced_practice_answer(question, answer_data, is_voice, parallel_analysis)
                    else:
                        self.submit_enhanced_test_answer(key_prefix, question, answer_data, is_voice, parallel_analysis)
    
    def render_enhanced_question_card(self, question: Dict[str, Any], use_parallel_analysis: bool = True):
        """Render question card with coaching info."""
        competency = question.get('competency', 'General')
        difficulty = question.get('difficulty', 'balanced')
        question_text = question.get('question', 'No question available')
        
        parallel_badge = ""
        if use_parallel_analysis and st.session_state.parallel_analysis_enabled:
            parallel_badge = '<span class="parallel-analysis-badge">⚡ Parallel Analysis</span>'
        
        coaching_badge = ""
        if st.session_state.speech_coaching_available:
            coaching_badge = '<span class="speech-coaching-badge">🎯 Speech Coaching"</span>'
        
        st.markdown(f"""
        <div class="question-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
                <h3 style="margin: 0;">🎯 {competency}</h3>
                <div>
                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 15px; font-size: 0.9em; margin: 2px;">
                        {difficulty.title()}
                    </span>
                    {parallel_badge}
                    {coaching_badge}
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                <p style="font-size: 1.1em; margin: 0; line-height: 1.6;">
                    {question_text}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_speech_coaching_tab(self):
        """Render dedicated speech coaching tab."""
        st.markdown("## 🎤 Speech Coaching & Delivery Analysis")
        
        if not st.session_state.speech_coaching_available:
            st.warning("🎤 Speech coaching features are initializing...")
            st.info("💡 Speech coaching provides detailed feedback on your speaking delivery, pace, clarity, and professional communication style.")
            return
        
        # Speech coaching introduction
        st.markdown("""
        <div class="enhanced-feature-card">
            <h3>🎯 Professional Speech Coaching</h3>
            <p>Get expert feedback on your interview delivery and communication style</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Coaching areas overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Analysis Areas:**
            - Pace & Rhythm
            - Clarity & Articulation
            - Confidence & Authority
            """)
        
        with col2:
            st.markdown("""
            **🎯 Professional Focus:**
            - Industry Communication Style
            - Professional Tone
            - Energy & Engagement
            """)
        
        with col3:
            st.markdown("""
            **💡 Coaching Benefits:**
            - Personalized Improvement Tips
            - Industry-Specific Guidance
            - Speaking Confidence Building
            """)
        
        # Recent delivery performance
        if st.session_state.evaluation_results:
            delivery_scores = []
            recent_coaching_tips = []
            
            for eval_data in st.session_state.evaluation_results:
                enhanced_analysis = eval_data.get('enhanced_analysis', {})
                if enhanced_analysis.get('delivery_analysis_available'):
                    delivery_score = enhanced_analysis.get('delivery_score', 0)
                    if delivery_score > 0:
                        delivery_scores.append(delivery_score)
                    
                    tips = enhanced_analysis.get('speaking_tips', [])
                    recent_coaching_tips.extend(tips)
            
            if delivery_scores:
                st.markdown("### 📈 Your Delivery Progress")
                
                # Delivery score chart
                if len(delivery_scores) > 1:
                    delivery_df = pd.DataFrame({
                        'Session': range(1, len(delivery_scores) + 1),
                        'Delivery Score': delivery_scores
                    })
                    
                    fig = px.line(
                        delivery_df, 
                        x='Session', 
                        y='Delivery Score',
                        title='Speech Delivery Progress',
                        markers=True
                    )
                    fig.update_layout(height=300)
                    fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Target: 7+")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recent coaching insights
                col1, col2 = st.columns(2)
                
                with col1:
                    avg_delivery = sum(delivery_scores) / len(delivery_scores)
                    latest_delivery = delivery_scores[-1]
                    
                    st.metric("Average Delivery Score", f"{avg_delivery:.1f}/10")
                    st.metric("Latest Delivery Score", f"{latest_delivery}/10")
                
                with col2:
                    if recent_coaching_tips:
                        st.markdown("**🎯 Recent Coaching Focus:**")
                        unique_tips = list(dict.fromkeys(recent_coaching_tips[-3:]))
                        for tip in unique_tips:
                            st.caption(f"💡 {tip}")
        
        # Practice delivery analysis
        st.markdown("### 🎤 Practice Delivery Analysis")
        st.info("💡 Record a 30-60 second response to any interview question to get personalized speech coaching!")
        
        if st.session_state.current_question:
            st.markdown("**Practice with your current question:**")
            st.caption(f"🎯 {st.session_state.current_question.get('competency', 'General')}: {st.session_state.current_question.get('question', '')[:100]}...")
            
            if st.button("🎤 Practice Delivery with Current Question", type="primary"):
                # Set focus to voice mode for delivery practice
                st.session_state.enhanced_practice_input_mode = "voice"
                st.info("👆 Switch to Practice Questions tab and use voice mode for delivery coaching!")
        else:
            st.info("💡 Generate a practice question first, then return here for delivery-focused practice!")
    
    def render_enhanced_analytics(self):
        """Render enhanced analytics with speech coaching insights."""
        st.markdown("## 📊 Enhanced Performance Analytics")
        
        if not st.session_state.evaluation_results:
            st.info("💡 Complete some enhanced practice questions to see your comprehensive analytics!")
            return
        
        # Enhanced overview with delivery metrics
        self.render_enhanced_analytics_overview()
        
        # Enhanced charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_enhanced_progress_chart()
        
        with col2:
            self.render_enhanced_competency_breakdown()
        
        # Speech coaching analytics
        self.render_speech_coaching_analytics()
        
        # Enhanced performance analysis
        self.render_enhanced_performance_analysis()
    
    def render_enhanced_analytics_overview(self):
        """Enhanced analytics overview with delivery metrics."""
        evaluations = st.session_state.evaluation_results
        
        if not evaluations:
            return
        
        total_questions = len(evaluations)
        avg_score = sum(e['score'] for e in evaluations) / total_questions
        
        # Enhanced analysis breakdown
        enhanced_evaluations = [e for e in evaluations 
                              if e.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation']
        voice_evaluations = [e for e in evaluations 
                           if e.get('transcription_metadata', {}).get('audio_processed', False) or
                              e.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation']
        delivery_evaluations = [e for e in evaluations 
                              if e.get('enhanced_analysis', {}).get('delivery_analysis_available', False)]
        
        enhanced_count = len(enhanced_evaluations)
        voice_count = len(voice_evaluations)
        delivery_count = len(delivery_evaluations)
        
        # Calculate delivery average
        delivery_scores = [e.get('enhanced_analysis', {}).get('delivery_score', 0) 
                          for e in delivery_evaluations if e.get('enhanced_analysis', {}).get('delivery_score', 0) > 0]
        avg_delivery = sum(delivery_scores) / len(delivery_scores) if delivery_scores else 0
        
        # Enhanced metrics display
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics = [
            ("Total Questions", total_questions, "🎯"),
            ("Average Score", f"{avg_score:.1f}/10", "📊"),
            ("Voice Responses", voice_count, "🎤"),
            ("Enhanced Analysis", enhanced_count, "⚡"),
            ("Speech Coaching", delivery_count, "🎯")
        ]
        
        for col, (label, value, icon) in zip([col1, col2, col3, col4, col5], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em; margin-bottom: 5px;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced performance comparison
        if delivery_count > 0 and voice_count > 0:
            st.markdown("### 📊 Enhanced Analysis Breakdown")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average Content Score", 
                    f"{avg_score:.1f}/10"
                )
            
            with col2:
                if avg_delivery > 0:
                    st.metric(
                        "Average Delivery Score", 
                        f"{avg_delivery:.1f}/10"
                    )
                else:
                    st.metric("Average Delivery Score", "N/A")
            
            with col3:
                if enhanced_count > 0:
                    enhancement_rate = (enhanced_count / total_questions) * 100
                    st.metric(
                        "Enhanced Analysis Rate",
                        f"{enhancement_rate:.0f}%"
                    )
    
    def render_enhanced_progress_chart(self):
        """Enhanced progress chart with delivery scores."""
        st.markdown("#### 📈 Enhanced Score Progression")
        
        # Prepare enhanced data
        enhanced_scores_data = []
        for i, eval_data in enumerate(st.session_state.evaluation_results):
            enhanced_analysis = eval_data.get('enhanced_analysis', {})
            
            data_point = {
                'Question': i+1,
                'Overall Score': eval_data['score'],
                'Competency': eval_data['competency'],
                'Method': '🎤 Voice' if eval_data.get('transcription_metadata', {}).get('audio_processed', False) or
                                        eval_data.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation'
                                    else '⌨️ Text'
            }
            
            # Add delivery score if available
            if enhanced_analysis.get('delivery_analysis_available'):
                delivery_score = enhanced_analysis.get('delivery_score', 0)
                if delivery_score > 0:
                    data_point['Delivery Score'] = delivery_score
                    data_point['Enhanced'] = '⚡ Enhanced'
                else:
                    data_point['Enhanced'] = '📝 Standard'
            else:
                data_point['Enhanced'] = '📝 Standard'
            
            enhanced_scores_data.append(data_point)
        
        scores_df = pd.DataFrame(enhanced_scores_data)
        
        if not scores_df.empty:
            # Create enhanced chart with delivery scores
            fig = px.scatter(
                scores_df,
                x='Question',
                y='Overall Score',
                color='Competency',
                symbol='Enhanced',
                title='Enhanced Score Progression • Content + Delivery Analysis',
                hover_data=['Method', 'Enhanced'],
                size_max=15
            )
            
            # Add delivery score line if available
            delivery_scores = [d.get('Delivery Score') for d in enhanced_scores_data if d.get('Delivery Score')]
            if delivery_scores:
                delivery_questions = [i+1 for i, d in enumerate(enhanced_scores_data) if d.get('Delivery Score')]
                fig.add_scatter(
                    x=delivery_questions,
                    y=delivery_scores,
                    mode='lines+markers',
                    name='Delivery Score',
                    line=dict(color='purple', width=3, dash='dot'),
                    marker=dict(symbol='diamond', size=8)
                )
            
            # Add trend line for overall scores
            fig.add_scatter(
                x=scores_df['Question'],
                y=scores_df['Overall Score'],
                mode='lines',
                name='Overall Trend',
                line=dict(color='rgba(128,128,128,0.3)', width=2),
                showlegend=False
            )
            
            fig.update_layout(
                yaxis_range=[0, 10], 
                height=400,
                showlegend=True
            )
            fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Target: 7+")
            fig.add_hline(y=5, line_dash="dash", line_color="orange", annotation_text="Developing: 5+")
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_speech_coaching_analytics(self):
        """Render speech coaching specific analytics."""
        # Extract delivery data
        delivery_data = []
        for eval_data in st.session_state.evaluation_results:
            enhanced_analysis = eval_data.get('enhanced_analysis', {})
            if enhanced_analysis.get('delivery_analysis_available'):
                delivery_score = enhanced_analysis.get('delivery_score', 0)
                if delivery_score > 0:
                    delivery_data.append({
                        'competency': eval_data.get('competency', 'Unknown'),
                        'delivery_score': delivery_score,
                        'speaking_tips': enhanced_analysis.get('speaking_tips', [])
                    })
        
        if delivery_data:
            st.markdown("### 🎤 Speech Coaching Analytics")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Delivery scores by competency
                delivery_by_comp = {}
                for item in delivery_data:
                    comp = item['competency']
                    if comp not in delivery_by_comp:
                        delivery_by_comp[comp] = []
                    delivery_by_comp[comp].append(item['delivery_score'])
                
                if delivery_by_comp:
                    comp_avg_delivery = {comp: sum(scores)/len(scores) 
                                       for comp, scores in delivery_by_comp.items()}
                    
                    # Create delivery competency chart
                    delivery_df = pd.DataFrame(list(comp_avg_delivery.items()), 
                                             columns=['Competency', 'Average Delivery Score'])
                    
                    fig_delivery = px.bar(
                        delivery_df,
                        x='Competency',
                        y='Average Delivery Score',
                        title='Average Delivery Score by Competency',
                        color='Average Delivery Score',
                        color_continuous_scale='viridis'
                    )
                    fig_delivery.update_layout(height=300, xaxis_tickangle=-45)
                    st.plotly_chart(fig_delivery, use_container_width=True)
            
            with col2:
                # Common coaching themes
                all_tips = []
                for item in delivery_data:
                    all_tips.extend(item['speaking_tips'])
                
                if all_tips:
                    st.markdown("**🎯 Common Coaching Themes:**")
                    
                    # Simple frequency analysis
                    tip_words = {}
                    for tip in all_tips:
                        words = tip.lower().split()
                        for word in words:
                            if len(word) > 4:  # Focus on meaningful words
                                tip_words[word] = tip_words.get(word, 0) + 1
                    
                    # Show top coaching themes
                    sorted_themes = sorted(tip_words.items(), key=lambda x: x[1], reverse=True)
                    for word, count in sorted_themes[:5]:
                        if count > 1:
                            st.caption(f"• {word.title()}: mentioned {count} times")
    
    def evaluate_enhanced_practice_answer(self, question: Dict[str, Any], answer_data: Any, is_voice: bool, use_parallel_analysis: bool = True):
        """Evaluate practice answer using enhanced workflow."""
        if st.session_state.api_server_status != 'running':
            st.error("Enhanced API server is not available.")
            return
        
        # Enhanced processing messages
        if is_voice and st.session_state.speech_coaching_available:
            if use_parallel_analysis:
                process_message = "🎯 Running enhanced parallel analysis (content + delivery)..."
                success_message = "✅ Enhanced analysis complete! Content and delivery evaluated."
            else:
                process_message = "🎤 Processing voice with speech coaching..."
                success_message = "✅ Voice response with coaching evaluated!"
        elif is_voice:
            process_message = "🎤 Processing your voice response..."
            success_message = "✅ Voice answer evaluated!"
        else:
            process_message = "⌨️ Evaluating your text answer..."
            success_message = "✅ Text answer evaluated!"
        
        with st.spinner(process_message):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                if is_voice and st.session_state.enhanced_workflow_ready:
                    # Enhanced voice evaluation
                    evaluation = loop.run_until_complete(
                        self.voice_client.evaluate_voice_answer_enhanced(
                            st.session_state.job_info,
                            question,
                            answer_data,
                            use_parallel_analysis=use_parallel_analysis
                        )
                    )
                elif is_voice:
                    # Fallback to regular voice evaluation
                    evaluation = loop.run_until_complete(
                        self.voice_client.evaluate_voice_answer_direct(
                            st.session_state.job_info,
                            question,
                            answer_data
                        )
                    )
                else:
                    # Regular text evaluation
                    evaluation = loop.run_until_complete(
                        self.voice_client.evaluate_answer_http(
                            st.session_state.job_info,
                            question,
                            answer_data
                        )
                    )
                
                if evaluation and evaluation.get('score', 0) >= 0:
                    st.session_state.current_evaluation = evaluation
                    st.session_state.evaluation_results.append(evaluation)
                    st.success(success_message)
                    
                    # Show enhanced features used
                    enhanced_meta = evaluation.get('enhanced_metadata', {})
                    if enhanced_meta.get('analysis_type') == 'enhanced_voice_evaluation':
                        features_used = enhanced_meta.get('features_used', {})
                        if features_used.get('delivery_analysis'):
                            st.info("🎯 Speech coaching included in analysis!")
                        if features_used.get('parallel_analysis'):
                            st.info("⚡ Parallel analysis completed!")
                    
                    st.rerun()
                else:
                    st.error("Failed to evaluate answer. Please try again.")
            except Exception as e:
                st.error(f"Error evaluating answer: {e}")
    
    def generate_enhanced_practice_question(self, competency: str, difficulty: str):
        """Generate practice question for enhanced workflow."""
        if st.session_state.api_server_status != 'running':
            st.error("Enhanced API server is not available.")
            return
        
        with st.spinner(f"🎯 Generating enhanced {difficulty} {competency} question..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                question = loop.run_until_complete(
                    self.voice_client.generate_question_http(
                        st.session_state.job_info,
                        competency,
                        difficulty
                    )
                )
                
                if question:
                    st.session_state.current_question = question
                    st.session_state.current_evaluation = None
                    st.success(f"✅ Generated enhanced {competency} question!")
                    
                    # Show enhanced features available
                    if st.session_state.speech_coaching_available:
                        st.info("🎯 Speech coaching available for voice responses!")
                    
                    st.rerun()
                else:
                    st.error("Failed to generate question.")
            except Exception as e:
                st.error(f"Error generating question: {e}")
    
    # Continue with other enhanced methods...
    def render_enhanced_practice_test(self):
        """Render enhanced practice test interface."""
        st.markdown("## 🎯 Enhanced Comprehensive Practice Test")
        
        if not st.session_state.practice_test_questions:
            self.render_enhanced_test_setup()
        else:
            self.render_enhanced_test_progress()
    
    def render_enhanced_test_setup(self):
        """Render enhanced test setup with speech coaching options."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Enhanced Test Configuration")
            
            num_questions = st.slider(
                "Number of Questions:",
                min_value=3,
                max_value=10,
                value=6,
                help="Recommended: 6-8 questions for comprehensive assessment"
            )
            
            # Enhanced options
            col1_sub, col2_sub = st.columns(2)
            with col1_sub:
                enable_speech_coaching = st.checkbox(
                    "🎤 Enable Speech Coaching",
                    value=st.session_state.speech_coaching_available,
                    disabled=not st.session_state.speech_coaching_available,
                    help="Get delivery feedback on voice responses"
                )
            
            with col2_sub:
                enable_parallel_analysis = st.checkbox(
                    "⚡ Parallel Analysis",
                    value=st.session_state.parallel_analysis_enabled,
                    disabled=not st.session_state.parallel_analysis_enabled,
                    help="Analyze content and delivery simultaneously"
                )
            
            # Show competencies
            competencies = st.session_state.job_info.get('competencies', CORE_COMPETENCIES)[:num_questions]
            
            st.markdown("**Competencies to be assessed:**")
            for i, comp in enumerate(competencies):
                st.markdown(f"<span class='competency-tag'>{comp}</span>", unsafe_allow_html=True)
            
            if st.button("🚀 Start Enhanced Practice Test", type="primary", use_container_width=True):
                self.start_enhanced_practice_test(num_questions, enable_speech_coaching, enable_parallel_analysis)
        
        with col2:
            self.render_enhanced_test_info_card(num_questions, enable_speech_coaching, enable_parallel_analysis)
    
    def render_enhanced_test_info_card(self, num_questions: int, speech_coaching: bool, parallel_analysis: bool):
        """Render enhanced test information card."""
        estimated_time = f"{num_questions * 3}-{num_questions * 6} minutes"
        if speech_coaching:
            estimated_time = f"{num_questions * 4}-{num_questions * 7} minutes"
        
        features_list = ["🎯 Competency-based questions", "🏢 Industry-specific scenarios"]
        if speech_coaching:
            features_list.extend(["🎤 Speech delivery coaching", "🎯 Professional communication feedback"])
        if parallel_analysis:
            features_list.extend(["⚡ Parallel content + delivery analysis", "📊 Comprehensive evaluation"])
        else:
            features_list.extend(["📝 Content analysis", "📊 Detailed evaluation"])
        
        st.markdown(f"""
        <div class="modern-card">
            <h3>📊 Enhanced Test Overview</h3>
            <div class="metric-card">
                <div class="metric-value">{num_questions}</div>
                <div class="metric-label">Questions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{estimated_time}</div>
                <div class="metric-label">Est. Time</div>
            </div>
            
            <h4>Enhanced features:</h4>
            <ul style="list-style: none; padding: 0;">
                {"".join(f"<li>{feature}</li>" for feature in features_list)}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Add remaining enhanced methods...
    def analyze_job_description(self, job_description: str):
        """Analyze job description and initialize enhanced system."""
        with st.spinner("🔍 Analyzing job description..."):
            if not st.session_state.job_analyzer:
                st.session_state.job_analyzer = JobAnalyzer()
            
            job_info = st.session_state.job_analyzer.analyze_job_description(job_description)
            st.session_state.job_info = job_info
        
        # Defensive: ensure job_info is a dict and has required keys
        required_keys = ["title", "industry", "competencies", "skills", "technologies"]
        if not isinstance(job_info, dict) or not all(k in job_info for k in required_keys):
            st.error("Job information is incomplete or invalid. Please check the job description and try again.")
            return
        
        # Initialize enhanced voice workflow if API server is available
        if st.session_state.api_server_status == 'running':
            with st.spinner("🎤 Initializing enhanced voice workflow with speech coaching..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Create enhanced voice workflow
                    workflow_created = loop.run_until_complete(
                        self.voice_client.create_enhanced_workflow(job_info)
                    )
                    
                    if workflow_created:
                        st.session_state.enhanced_workflow_ready = True
                        
                        # Check available features with fallback
                        try:
                            capabilities = loop.run_until_complete(
                                self.voice_client.get_enhanced_capabilities()
                            )
                            
                            if isinstance(capabilities, dict) and 'capabilities' in capabilities:
                                caps = capabilities['capabilities']
                                components = caps.get('components', {})
                                st.session_state.speech_coaching_available = 'speech_coach_agent' in components
                                st.session_state.parallel_analysis_enabled = caps.get('parallel_analysis', False)
                            else:
                                # Fallback: assume basic features are available
                                st.session_state.speech_coaching_available = True
                                st.session_state.parallel_analysis_enabled = True
                        except Exception as cap_error:
                            logger.warning(f"Could not fetch capabilities: {cap_error}")
                            # Fallback: assume basic features are available
                            st.session_state.speech_coaching_available = True
                            st.session_state.parallel_analysis_enabled = True
                        
                        success_msg = "✅ Enhanced voice workflow ready!"
                        if st.session_state.speech_coaching_available:
                            success_msg += " Speech coaching active!"
                        if st.session_state.parallel_analysis_enabled:
                            success_msg += " Parallel analysis enabled!"
                        
                        st.success(success_msg)
                    else:
                        st.warning("⚠️ Enhanced workflow creation failed - text input still available")
                        st.info("💡 You can still use all text-based features while voice initializes.")
                        
                except Exception as e:
                    st.warning(f"⚠️ Enhanced workflow initialization failed: {e}")
                    st.info("💡 Text input is fully functional. Enhanced voice features can be enabled later.")
        else:
            st.info("💡 Enhanced voice features will be available when the server is running.")
        
        st.success("✅ Enhanced interview preparation system ready!")
        st.rerun()
    
    # Add other necessary methods (chat_interface, job_setup, etc.)
    def render_job_setup(self):
        """Render job description setup."""
        st.markdown("## 📝 Job Description Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Enter Job Description")
            job_description = st.text_area(
                "Paste the complete job description:",
                height=350,
                placeholder="Copy and paste the full job description including requirements, responsibilities, and qualifications...",
                key="job_description_input"
            )
            
            col1_sub, col2_sub = st.columns(2)
            with col1_sub:
                if st.button("📋 Use Sample", type="secondary"):
                    st.session_state.job_description_input = self.get_sample_job_description()
                    st.rerun()
            
            with col2_sub:
                if st.button("🚀 Analyze & Start", type="primary", disabled=not job_description.strip()):
                    if job_description.strip():
                        self.analyze_job_description(job_description)
        
        with col2:
            st.markdown("""
            <div class="modern-card">
                <h3>🔍 Enhanced Analysis Features</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>📊 Industry identification</li>
                    <li>🎯 Key competencies</li>
                    <li>⚙️ Required skills</li>
                    <li>📈 Experience level</li>
                    <li>🔍 Role-specific areas</li>
                </ul>
                
                <h3>🎯 Enhanced Features</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>🎤 Enhanced voice analysis</li>
                    <li>🎯 Speech coaching</li>
                    <li>⚡ Parallel processing</li>
                    <li>📊 Comprehensive tracking</li>
                    <li>📋 Industry optimization</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_chat_interface(self):
        """Render AI chat interface."""
        st.markdown("## 💬 Interview Preparation Assistant")
        
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style="text-align: center; padding: 40px; color: #666;">
                    <h3>👋 Hello! I'm your enhanced interview preparation assistant.</h3>
                    <p>Ask me anything about interview preparation, the STAR method, speech coaching, or get tips for your specific role!</p>
                </div>
                """, unsafe_allow_html=True)
            
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about interview preparation, speech coaching, or delivery tips..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.get_chat_response(prompt)
                st.markdown(response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    def get_chat_response(self, question: str) -> str:
        """Get chat response via HTTP API."""
        if st.session_state.api_server_status != 'running':
            return "Sorry, the enhanced API server is not available. Please check the server status."
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.voice_client.chat_query_http(
                    st.session_state.job_info, 
                    question
                )
            )
            return response
        except Exception as e:
            st.error(f"Error getting response: {e}")
            return "I apologize, but I encountered an error processing your question."
    
    def render_job_status(self):
        """Render job information section."""
        if st.session_state.job_info:
            st.markdown("### 📄 Current Position")
            job_info = st.session_state.job_info
            st.success(f"**{job_info.get('title', 'Unknown Position')}**")
            st.caption(f"Industry: {job_info.get('industry', 'Unknown')}")
            
            # Competencies
            competencies = job_info.get('competencies', [])
            if competencies:
                st.markdown("**Key Competencies:**")
                for comp in competencies[:4]:
                    st.markdown(f"• {comp}")
                if len(competencies) > 4:
                    st.caption(f"...and {len(competencies) - 4} more")
        else:
            st.warning("⚠️ No job description loaded")
    
    def render_quick_actions(self):
        """Render quick action buttons."""
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Reset Everything", use_container_width=True):
            self.reset_application()
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.show_analytics = True
            st.rerun()
    
    def render_enhanced_competency_breakdown(self):
        """Render enhanced competency breakdown."""
        st.markdown("#### 🎯 Competency Performance")
        
        # Calculate competency averages
        competency_scores = {}
        for eval_data in st.session_state.evaluation_results:
            comp = eval_data['competency']
            if comp not in competency_scores:
                competency_scores[comp] = []
            competency_scores[comp].append(eval_data['score'])
        
        if competency_scores:
            for comp, scores in sorted(competency_scores.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
                avg_score = sum(scores) / len(scores)
                attempts = len(scores)
                color = "#22c55e" if avg_score >= 7 else "#f59e0b" if avg_score >= 5 else "#ef4444"
                status = "Strong" if avg_score >= 7 else "Developing" if avg_score >= 5 else "Needs Work"
                
                st.markdown(f"""
                <div style="background: {color}15; border-left: 4px solid {color}; padding: 12px; margin: 8px 0; border-radius: 6px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{comp}</strong><br>
                            <small>{attempts} attempts • {status}</small>
                        </div>
                        <div style="font-size: 1.3em; font-weight: bold; color: {color};">
                            {avg_score:.1f}/10
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_enhanced_performance_analysis(self):
        """Render enhanced AI performance analysis."""
        st.markdown("### 🤖 Enhanced Performance Analysis")
        
        if st.button("🧠 Generate Enhanced Analysis", type="primary"):
            self.generate_enhanced_performance_analysis()
        
        if st.session_state.performance_analysis:
            analysis = st.session_state.performance_analysis
            
            # Overall score
            if analysis.get('overall_score'):
                st.metric("Overall Performance", f"{analysis['overall_score']:.1f}/10")
            
            # Enhanced delivery insights
            if analysis.get('delivery_insights'):
                st.markdown("**🎤 Speaking Performance Insights:**")
                for insight in analysis['delivery_insights']:
                    st.info(f"🎯 {insight}")
            
            # Strengths and areas for improvement
            col1, col2 = st.columns(2)
            
            with col1:
                if analysis.get('strengths'):
                    st.markdown("**💪 Your Strengths**")
                    for strength in analysis['strengths']:
                        st.success(f"✅ {strength}")
            
            with col2:
                if analysis.get('weaknesses'):
                    st.markdown("**📈 Focus Areas**")
                    for weakness in analysis['weaknesses']:
                        st.warning(f"⚠️ {weakness}")
            
            # Enhanced recommendations
            if analysis.get('recommendations'):
                st.markdown("**🎯 Personalized Recommendations**")
                for i, rec in enumerate(analysis['recommendations'], 1):
                    st.info(f"{i}. {rec}")
    
    def submit_enhanced_test_answer(self, key_prefix: str, question: Dict[str, Any], answer_data: Any, is_voice: bool, use_parallel_analysis: bool = True):
        """Submit enhanced test answer with parallel processing."""
        idx = int(key_prefix.split('_')[1])
        
        # Enhanced processing indication
        process_type = "enhanced voice" if is_voice else "text"
        
        with st.spinner(f"🎯 Processing {process_type} answer with enhanced analysis..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                if is_voice and st.session_state.enhanced_workflow_ready:
                    # Enhanced voice evaluation
                    evaluation = loop.run_until_complete(
                        self.voice_client.evaluate_voice_answer_enhanced(
                            st.session_state.job_info,
                            question,
                            answer_data,
                            use_parallel_analysis=use_parallel_analysis
                        )
                    )
                    # Store transcribed text for display
                    enhanced_analysis = evaluation.get('enhanced_analysis', {})
                    if enhanced_analysis.get('content_analysis_available'):
                        transcribed_text = evaluation.get('transcription_metadata', {}).get('original_text', '[Enhanced Voice Response]')
                        st.session_state.practice_test_answers[idx] = transcribed_text
                    else:
                        st.session_state.practice_test_answers[idx] = '[Voice Response]'
                else:
                    # Text evaluation or fallback
                    evaluation = loop.run_until_complete(
                        self.voice_client.evaluate_answer_http(
                            st.session_state.job_info,
                            question,
                            answer_data
                        )
                    )
                    st.session_state.practice_test_answers[idx] = answer_data
                
                if evaluation:
                    st.session_state.practice_test_evaluations[idx] = evaluation
                    st.session_state.evaluation_results.append(evaluation)
                    
                    # Check if test is complete
                    if len(st.session_state.practice_test_evaluations) == len(st.session_state.practice_test_questions):
                        st.session_state.practice_test_completed = True
                    
                    st.rerun()
                else:
                    st.error("Failed to evaluate answer.")
            except Exception as e:
                st.error(f"Error evaluating answer: {e}")
    
    def start_enhanced_practice_test(self, num_questions: int, enable_speech_coaching: bool, enable_parallel_analysis: bool):
        """Start enhanced practice test by generating questions."""
        if st.session_state.api_server_status != 'running':
            st.error("Enhanced API server is not available.")
            return
        
        with st.spinner(f"🎯 Generating {num_questions} enhanced practice questions..."):
            try:
                questions = []
                competencies = st.session_state.job_info.get('competencies', CORE_COMPETENCIES)
                
                # Generate questions for each competency
                for i in range(num_questions):
                    competency = competencies[i % len(competencies)]
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    question = loop.run_until_complete(
                        self.voice_client.generate_question_http(
                            st.session_state.job_info,
                            competency,
                            "balanced"
                        )
                    )
                    
                    if question:
                        questions.append(question)
                
                if questions:
                    st.session_state.practice_test_questions = questions
                    st.session_state.practice_test_answers = {}
                    st.session_state.practice_test_evaluations = {}
                    st.session_state.practice_test_completed = False
                    
                    # Store enhanced test settings
                    st.session_state.test_speech_coaching = enable_speech_coaching
                    st.session_state.test_parallel_analysis = enable_parallel_analysis
                    
                    success_msg = f"✅ Generated {len(questions)} enhanced questions!"
                    if enable_speech_coaching:
                        success_msg += " Speech coaching enabled!"
                    if enable_parallel_analysis:
                        success_msg += " Parallel analysis ready!"
                    
                    st.success(success_msg)
                    st.rerun()
                else:
                    st.error("Failed to generate enhanced practice test questions.")
            except Exception as e:
                st.error(f"Error generating enhanced practice test: {e}")
    
    def render_enhanced_test_progress(self):
        """Render enhanced test progress."""
        questions = st.session_state.practice_test_questions
        total_questions = len(questions)
        completed = len(st.session_state.practice_test_evaluations)
        
        # Enhanced progress bar
        progress = completed / total_questions if total_questions > 0 else 0
        st.progress(progress, text=f"Enhanced Progress: {completed}/{total_questions} questions completed")
        
        # Show enhanced features active
        features_active = []
        if st.session_state.get('test_speech_coaching', False):
            features_active.append("🎤 Speech Coaching")
        if st.session_state.get('test_parallel_analysis', False):
            features_active.append("⚡ Parallel Analysis")
        
        if features_active:
            st.info(f"Enhanced features active: {' • '.join(features_active)}")
        
        if completed < total_questions and not st.session_state.practice_test_completed:
            # Current question
            current_idx = completed
            current_question = questions[current_idx]
            
            st.markdown(f"### Enhanced Question {current_idx + 1} of {total_questions}")
            
            use_parallel = st.session_state.get('test_parallel_analysis', False)
            self.render_enhanced_question_interface(current_question, f"test_{current_idx}", use_parallel)
        
        else:
            # Test completed
            self.render_enhanced_test_results()
    
    def render_enhanced_test_results(self):
        """Render enhanced test results with delivery analysis."""
        st.success("🎉 Enhanced practice test completed!")
        
        evaluations = list(st.session_state.practice_test_evaluations.values())
        if not evaluations:
            return
        
        # Enhanced metrics with delivery breakdown
        avg_score = sum(eval_data['score'] for eval_data in evaluations) / len(evaluations)
        best_score = max(eval_data['score'] for eval_data in evaluations)
        
        # Enhanced analysis counts
        enhanced_count = sum(1 for eval_data in evaluations 
                           if eval_data.get('enhanced_metadata', {}).get('analysis_type') == 'enhanced_voice_evaluation')
        delivery_count = sum(1 for eval_data in evaluations 
                           if eval_data.get('enhanced_analysis', {}).get('delivery_analysis_available', False))
        
        # Calculate average delivery score
        delivery_scores = [eval_data.get('enhanced_analysis', {}).get('delivery_score', 0) 
                          for eval_data in evaluations 
                          if eval_data.get('enhanced_analysis', {}).get('delivery_score', 0) > 0]
        avg_delivery = sum(delivery_scores) / len(delivery_scores) if delivery_scores else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics = [
            ("Overall Score", f"{avg_score:.1f}/10", "📊"),
            ("Best Score", f"{best_score}/10", "🏆"),
            ("Questions", len(evaluations), "🎯"),
            ("Enhanced Analysis", enhanced_count, "⚡"),
            ("Speech Coaching", delivery_count, "🎤")
        ]
        
        for col, (label, value, icon) in zip([col1, col2, col3, col4, col5], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.5em; margin-bottom: 5px;">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Show delivery average if available
        if avg_delivery > 0:
            st.markdown(f'<div class="delivery-score-card"><strong>Average Delivery Score: {avg_delivery:.1f}/10</strong><br>Professional communication analysis</div>', unsafe_allow_html=True)
        
        # Enhanced detailed results
        st.markdown("### 📋 Enhanced Detailed Results")
        
        for i, (question, evaluation) in enumerate(zip(st.session_state.practice_test_questions, evaluations)):
            enhanced_analysis = evaluation.get('enhanced_analysis', {})
            has_delivery = enhanced_analysis.get('delivery_analysis_available', False)
            delivery_score = enhanced_analysis.get('delivery_score', 0) if has_delivery else 0
            
            # Enhanced display
            analysis_type = "⚡ Enhanced" if enhanced_analysis else "📝 Standard"
            delivery_info = f" • Delivery: {delivery_score}/10" if has_delivery and delivery_score > 0 else ""
            
            with st.expander(f"Q{i+1}: {question['competency']} • Content: {evaluation['score']}/10{delivery_info} • {analysis_type}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Question:** {question['question']}")
                    
                    # Show response
                    answer_text = st.session_state.practice_test_answers[i]
                    st.markdown(f"**Your Response:**")
                    st.markdown(f'<div style="background: #e0e7ff; padding: 16px; border-radius: 8px; border: 2px solid #6366f1; font-size: 1.08em; margin-bottom: 8px; color: #222; font-weight: 500;">{answer_text}</div>', unsafe_allow_html=True)
                
                with col2:
                    # Enhanced score display
                    content_score = evaluation['score']
                    color = "#22c55e" if content_score >= 7 else "#f59e0b" if content_score >= 5 else "#ef4444"
                    
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="width: 80px; height: 80px; border-radius: 50%; background: {color}; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: white; font-weight: bold; font-size: 1.2em;">
                            {content_score}/10
                        </div>
                        <div style="margin-top: 10px; font-weight: bold;">Content</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Delivery score if available
                    if has_delivery and delivery_score > 0:
                        delivery_color = "#10b981" if delivery_score >= 7 else "#06b6d4" if delivery_score >= 5 else "#84cc16"
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 15px;">
                            <div style="width: 60px; height: 60px; border-radius: 50%; background: {delivery_color}; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: white; font-weight: bold;">
                                {delivery_score}/10
                            </div>
                            <div style="margin-top: 5px; font-weight: bold; font-size: 0.9em;">Delivery</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Enhanced evaluation display
                self.voice_client.render_enhanced_evaluation(evaluation, use_expander=False)
        
        # Enhanced action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Take New Enhanced Test", type="primary", use_container_width=True, key="take_new_enhanced_test_btn"):
                self.reset_practice_test()
        
        with col2:
            if st.button("📊 View Enhanced Analytics", type="secondary", use_container_width=True, key="view_enhanced_analytics_btn"):
                st.session_state.show_analytics = True
                st.rerun()
    
    def generate_enhanced_performance_analysis(self):
        """Generate enhanced performance analysis with delivery insights."""
        evaluations = st.session_state.evaluation_results
        
        if not evaluations:
            return
        
        # Calculate enhanced metrics
        overall_score = sum(e['score'] for e in evaluations) / len(evaluations)
        
        # Enhanced analysis breakdown
        enhanced_evaluations = [e for e in evaluations 
                              if e.get('enhanced_analysis', {}).get('delivery_analysis_available', False)]
        
        delivery_insights = []
        if enhanced_evaluations:
            delivery_scores = [e.get('enhanced_analysis', {}).get('delivery_score', 0) 
                             for e in enhanced_evaluations if e.get('enhanced_analysis', {}).get('delivery_score', 0) > 0]
            
            if delivery_scores:
                avg_delivery = sum(delivery_scores) / len(delivery_scores)
                delivery_insights.append(f"Average delivery score: {avg_delivery:.1f}/10")
                
                if avg_delivery >= 7:
                    delivery_insights.append("Strong professional communication skills")
                elif avg_delivery >= 5:
                    delivery_insights.append("Good delivery foundation, room for improvement")
                else:
                    delivery_insights.append("Focus on speech delivery and professional communication")
        
        # Identify strengths and weaknesses (enhanced)
        competency_scores = {}
        for eval_data in evaluations:
            comp = eval_data['competency']
            if comp not in competency_scores:
                competency_scores[comp] = []
            competency_scores[comp].append(eval_data['score'])
        
        strengths = []
        weaknesses = []
        
        for comp, scores in competency_scores.items():
            avg = sum(scores) / len(scores)
            if avg >= 7:
                strengths.append(comp)
            elif avg < 5:
                weaknesses.append(comp)
        
        # Enhanced recommendations
        recommendations = []
        if weaknesses:
            recommendations.append(f"Focus on improving {', '.join(weaknesses[:2])} through targeted practice")
        if overall_score < 6:
            recommendations.append("Practice the STAR method structure for more comprehensive answers")
        if len(evaluations) < 10:
            recommendations.append("Take more practice questions to build confidence and identify patterns")
        
        # Enhanced delivery recommendations
        if enhanced_evaluations:
            if len(delivery_scores) < len(evaluations) / 2:
                recommendations.append("Use voice mode more often to benefit from speech coaching")
            elif delivery_scores and sum(delivery_scores) / len(delivery_scores) < 6:
                recommendations.append("Focus on speech delivery: pace, clarity, and professional tone")
        
        analysis = {
            'overall_score': overall_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'delivery_insights': delivery_insights,
            'enhanced_analysis_count': len(enhanced_evaluations),
            'total_evaluations': len(evaluations)
        }
        
        st.session_state.performance_analysis = analysis
        st.rerun()
    
    def reset_practice_test(self):
        """Reset enhanced practice test state."""
        st.session_state.practice_test_questions = []
        st.session_state.practice_test_answers = {}
        st.session_state.practice_test_evaluations = {}
        st.session_state.practice_test_completed = False
        st.session_state.test_speech_coaching = False
        st.session_state.test_parallel_analysis = False
        st.rerun()
    
    def reset_application(self):
        """Reset entire enhanced application state."""
        # Cleanup enhanced voice session
        if st.session_state.enhanced_workflow_ready:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.voice_client.cleanup_enhanced_session())
            except:
                pass
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            if key != 'enhanced_voice_client':  # Keep enhanced voice client instance
                del st.session_state[key]
        
        # Reinitialize
        self.initialize_session_state()
        st.rerun()
    
    def get_sample_job_description(self) -> str:
        """Get sample job description."""
        return """
# Senior Software Engineer - AI/ML Platform

## About Us
We are a fast-growing technology company building cutting-edge AI/ML platforms for enterprise customers. Based in San Francisco with remote work options.

## Responsibilities
- Design and develop scalable AI/ML infrastructure and services
- Build robust APIs and microservices using Python, FastAPI, and cloud technologies
- Collaborate with data scientists to deploy machine learning models at scale
- Implement monitoring, logging, and observability solutions
- Participate in code reviews and maintain high code quality standards
- Mentor junior engineers and contribute to technical decision-making

## Requirements
- 5+ years of software engineering experience
- Strong proficiency in Python and modern web frameworks (FastAPI, Django, Flask)
- Experience with cloud platforms (AWS, GCP, or Azure)
- Knowledge of containerization (Docker) and orchestration (Kubernetes)
- Understanding of machine learning concepts and MLOps practices
- Experience with databases (PostgreSQL, Redis) and message queues

## Benefits
- Competitive salary and equity package
- Comprehensive health, dental, and vision insurance
- Flexible PTO and remote work options
- Professional development budget
- Latest hardware and tools
"""

def main():
    """Main application entry point."""
    app = EnhancedInterviewApp()
    
    # Render enhanced application
    app.render_header()
    app.render_sidebar()
    app.render_main_content()

if __name__ == "__main__":
    main()