"""
Complete Enhanced Streamlit UI with seamless voice integration.
FULLY REWRITTEN: Complete implementation with all features.
"""
import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Any, Optional

from core.job_analyzer import JobAnalyzer
from agents.interview_manager import InterviewManager
from enhanced_streamlit_voice_client import DynamicVoiceComponent
from config import APP_NAME, CORE_COMPETENCIES

# Configure Streamlit page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .competency-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #17a2b8; font-weight: bold; }
    .score-needs-work { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    
    .voice-enabled-indicator {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85em;
        display: inline-block;
        margin: 0.25rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .question-card {
        background: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4169e1;
        margin: 1rem 0;
    }
    
    .evaluation-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class CompleteInterviewUI:
    """Complete UI with seamless voice integration for practice questions and tests."""
    
    def __init__(self):
        """Initialize the complete UI."""
        self.voice_component = DynamicVoiceComponent()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        defaults = {
            'job_analyzer': None,
            'interview_manager': None,
            'job_info': None,
            'current_question': None,
            'current_answer': '',
            'current_evaluation': None,
            'evaluation_results': [],
            'practice_sessions': [],
            'chat_history': [],
            'voice_enabled': True,  # Enable by default
            'practice_test_questions': [],
            'practice_test_answers': {},
            'practice_test_evaluations': {},
            'practice_test_current_index': 0,
            'practice_test_completed': False,
            'progress_data': {},
            'performance_analysis': None,
            'voice_transcript_cache': {}  # Cache for voice transcripts
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def render_header(self):
        """Render the main application header."""
        st.markdown(f"""
        <div class="main-header">
            <h1>🎯 {APP_NAME}</h1>
            <p>AI-Powered Interview Preparation with Voice & Text Input</p>
            <div class="voice-enabled-indicator">
                🎤 Voice Input Enabled
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with navigation and settings."""
        with st.sidebar:
            st.title("Navigation")
            
            # Job status
            if st.session_state.job_info:
                st.success(f"✅ Analyzing: {st.session_state.job_info.get('title', 'Unknown Position')}")
                st.info(f"Industry: {st.session_state.job_info.get('industry', 'Unknown')}")
            else:
                st.warning("⚠️ No job description loaded")
            
            # Voice settings
            st.subheader("🎙️ Voice Settings")
            voice_enabled = st.checkbox("Enable Voice Input", value=st.session_state.voice_enabled)
            st.session_state.voice_enabled = voice_enabled
            
            if voice_enabled:
                st.success("🟢 Voice Input Ready")
                st.markdown("""
                **Voice Features:**
                - Real-time speech recognition
                - Works in practice questions
                - Works in practice tests
                - Browser-based (no downloads)
                """)
            else:
                st.info("🔘 Voice Input Disabled")
            
            # Progress overview
            if st.session_state.evaluation_results:
                st.subheader("📊 Quick Progress")
                progress_summary = self._get_progress_summary()
                for comp, score in list(progress_summary.items())[:5]:
                    score_class = self._get_score_class(score)
                    st.markdown(f"**{comp}**: <span class='{score_class}'>{score:.1f}/10</span>", 
                              unsafe_allow_html=True)
                
                st.markdown(f"**Total Questions:** {len(st.session_state.evaluation_results)}")
                
                # Voice usage stats
                voice_count = sum(1 for e in st.session_state.evaluation_results if e.get('was_voice_input', False))
                st.markdown(f"**🎤 Voice Used:** {voice_count} times")
            
            # Reset button
            if st.button("🔄 Reset Application", type="secondary"):
                self._reset_application()
    
    def render_main_content(self):
        """Render the main content area with tabs."""
        if not st.session_state.job_info:
            self.render_job_setup()
        else:
            self.render_interview_tabs()
    
    def render_job_setup(self):
        """Render the job description setup interface."""
        st.header("📝 Job Description Setup")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Enter Job Description")
            job_description = st.text_area(
                "Paste the complete job description here:",
                height=400,
                placeholder="Copy and paste the full job description including requirements, responsibilities, and qualifications...",
                key="job_description_input"
            )
            
            # Sample job description
            if st.button("📋 Use Sample Job Description"):
                sample_job = self._get_sample_job_description()
                st.session_state.job_description_input = sample_job
                st.rerun()
        
        with col2:
            st.subheader("What We'll Analyze")
            st.info("""
            🔍 **Job Analysis Includes:**
            - Industry identification
            - Key competencies extraction
            - Required skills & technologies
            - Experience level assessment
            - Role-specific focus areas
            
            🎯 **Enhanced Preparation:**
            - Custom practice questions
            - **Voice OR text input for answers**
            - Industry-specific scenarios
            - Competency-based evaluation
            - Progress tracking with input method analytics
            """)
        
        # Analyze button
        if st.button("🚀 Start Interview Preparation", type="primary", disabled=not job_description.strip()):
            if job_description.strip():
                self._analyze_job_description(job_description)
    
    def render_interview_tabs(self):
        """Render the main interview preparation interface with tabs."""
        # REMOVED: Voice Practice tab - voice is now integrated into other tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "💬 Chat Assistant", 
            "📝 Practice Questions", 
            "🎯 Practice Test", 
            "📊 Progress & Reports"
        ])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_enhanced_practice_questions()
        
        with tab3:
            self.render_enhanced_practice_test()
        
        with tab4:
            self.render_progress_reports()
    
    def render_enhanced_practice_questions(self):
        """Render practice questions with integrated voice input."""
        st.header("📝 Practice Questions with Voice Input")
        
        # Voice status indicator
        if st.session_state.voice_enabled:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #28a745, #20c997); color: white; 
                        padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                🎤 <strong>Voice Input Active</strong> - You can speak or type your answers!
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎯 Question Settings")
            
            # Competency selection
            competency = st.selectbox(
                "Select Competency:",
                options=list(st.session_state.job_info.get('competencies', CORE_COMPETENCIES)),
                key="practice_competency"
            )
            
            # Difficulty selection
            difficulty = st.selectbox(
                "Difficulty Level:",
                options=["easy", "balanced", "challenging"],
                index=1,
                key="practice_difficulty"
            )
            
            # Generate question button
            if st.button("🔄 Generate New Question", type="primary"):
                self._generate_practice_question(competency, difficulty)
        
        with col2:
            st.subheader("ℹ️ Voice & Text Tips")
            st.info(f"""
            **Input Methods:**
            - 🎤 **Voice**: Click microphone and speak naturally
            - ⌨️ **Text**: Type in the text area
            - 🔄 **Switch**: Use either method anytime
            
            **STAR Method Reminder:**
            - **Situation**: Set the context
            - **Task**: Describe your responsibility  
            - **Action**: Explain what you did
            - **Result**: Share the outcome
            
            **For {competency}:**
            Focus on specific examples demonstrating this competency.
            """)
        
        # Display current question with voice-enabled input
        if st.session_state.current_question:
            st.markdown("---")
            
            question_data = st.session_state.current_question
            
            # Enhanced question display with voice capability
            answer = self.voice_component.render_practice_question_with_voice(
                question=question_data,
                answer_key="practice_answer"
            )
            
            # Submit answer button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 Submit Answer for Evaluation", type="primary", disabled=not answer.strip()):
                    # Detect if answer was likely from voice
                    was_voice = self._detect_voice_input(answer) if st.session_state.voice_enabled else False
                    
                    self._evaluate_practice_answer(question_data, answer, was_voice)
        
        # Display evaluation results
        if hasattr(st.session_state, 'current_evaluation') and st.session_state.current_evaluation:
            st.markdown("---")
            was_voice = st.session_state.current_evaluation.get('was_voice_input', False)
            self.voice_component.render_evaluation_with_voice_context(
                st.session_state.current_evaluation, 
                was_voice
            )
    
    def render_enhanced_practice_test(self):
        """Render practice test with integrated voice input."""
        st.header("🎯 Comprehensive Practice Test with Voice")
        
        # Voice status indicator
        if st.session_state.voice_enabled:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #4169e1, #667eea); color: white; 
                        padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                🎤 <strong>Voice & Text Ready</strong> - Answer each question using your preferred method!
            </div>
            """, unsafe_allow_html=True)
        
        if not st.session_state.practice_test_questions:
            # Test setup
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📋 Test Configuration")
                
                num_questions = st.slider(
                    "Number of Questions:",
                    min_value=3,
                    max_value=10,
                    value=6,
                    help="Recommended: 6-8 questions for a comprehensive test"
                )
                
                st.markdown("**Test will cover these competencies:**")
                competencies = st.session_state.job_info.get('competencies', CORE_COMPETENCIES)[:num_questions]
                
                for i, comp in enumerate(competencies, 1):
                    st.markdown(f"{i}. {comp}")
                
                if st.button("🚀 Start Practice Test", type="primary"):
                    self._start_practice_test(num_questions)
            
            with col2:
                st.subheader("📊 Test Information")
                st.info(f"""
                **What to expect:**
                - {num_questions} competency-based questions
                - Questions tailored to: {st.session_state.job_info.get('title', 'your role')}
                - Industry-specific scenarios: {st.session_state.job_info.get('industry', 'technology')}
                - **Voice OR text input for each answer**
                - Comprehensive evaluation and feedback
                - Progress tracking and recommendations
                
                **Estimated time:** {num_questions * 3}-{num_questions * 5} minutes
                """)
        
        else:
            # Test in progress or completed
            self._render_enhanced_practice_test_questions()
    
    def render_chat_interface(self):
        """Render the chat interface for general questions."""
        st.header("💬 Interview Preparation Chat")
        
        # Display chat history
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about interview preparation..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Use proper async handling
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        st.session_state.interview_manager.answer_question(prompt)
                    )
                st.markdown(response)
            
            # Add assistant response
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    def render_progress_reports(self):
        """Render progress tracking and reports interface."""
        st.header("📊 Progress & Performance Reports")
        
        if not st.session_state.evaluation_results:
            st.info("💡 Complete some practice questions or tests to see your progress here!")
            return
        
        # Voice input statistics
        voice_count = sum(1 for eval_data in st.session_state.evaluation_results 
                         if eval_data.get('was_voice_input', False))
        text_count = len(st.session_state.evaluation_results) - voice_count
        
        # Overall metrics including voice stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_questions = len(st.session_state.evaluation_results)
        avg_score = sum(eval_data['score'] for eval_data in st.session_state.evaluation_results) / total_questions
        
        with col1:
            st.metric("Total Questions", total_questions)
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}/10")
        with col3:
            st.metric("🎤 Voice Answers", voice_count)
        with col4:
            st.metric("⌨️ Text Answers", text_count)
        
        # Input method analysis
        if voice_count > 0 and text_count > 0:
            st.subheader("📊 Input Method Performance")
            
            voice_scores = [eval_data['score'] for eval_data in st.session_state.evaluation_results 
                           if eval_data.get('was_voice_input', False)]
            text_scores = [eval_data['score'] for eval_data in st.session_state.evaluation_results 
                          if not eval_data.get('was_voice_input', False)]
            
            if voice_scores and text_scores:
                voice_avg = sum(voice_scores) / len(voice_scores)
                text_avg = sum(text_scores) / len(text_scores)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🎤 Voice Average", f"{voice_avg:.1f}/10")
                with col2:
                    st.metric("⌨️ Text Average", f"{text_avg:.1f}/10")
                
                # Performance insight
                if abs(voice_avg - text_avg) > 0.5:
                    better_method = "voice" if voice_avg > text_avg else "text"
                    st.info(f"💡 **Insight**: You perform {abs(voice_avg - text_avg):.1f} points better with {better_method} input!")
        
        # Progress charts and analysis
        self._render_progress_charts()
        
        # Detailed analysis
        st.subheader("🔍 Detailed Analysis")
        
        # Performance analysis
        if st.button("🧠 Generate AI Performance Analysis"):
            self._generate_performance_analysis()
        
        if st.session_state.performance_analysis:
            self._display_performance_analysis()
        
        # Export options
        st.subheader("📤 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Export Progress Report"):
                report_data = self._generate_progress_report()
                st.download_button(
                    "⬇️ Download Report",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"interview_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Export to CSV"):
                csv_data = self._generate_csv_export()
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"interview_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("🎯 Create Study Plan"):
                study_plan = self._generate_study_plan()
                st.success("Study plan generated!")
                st.json(study_plan)
    
    def _render_enhanced_practice_test_questions(self):
        """Render the enhanced practice test questions interface with voice."""
        questions = st.session_state.practice_test_questions
        total_questions = len(questions)
        
        # Progress bar
        completed = len(st.session_state.practice_test_evaluations)
        progress = completed / total_questions if total_questions > 0 else 0
        
        st.progress(progress, text=f"Progress: {completed}/{total_questions} questions completed")
        
        if completed < total_questions and not st.session_state.practice_test_completed:
            # Current question
            current_idx = completed
            current_question = questions[current_idx]
            
            st.subheader(f"Question {current_idx + 1} of {total_questions}")
            
            # Enhanced question with voice input
            answer = self.voice_component.render_practice_question_with_voice(
                question=current_question,
                answer_key=f"test_answer_{current_idx}"
            )
            
            # Submit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("➡️ Submit & Continue", type="primary", disabled=not answer.strip()):
                    # Detect if answer was likely from voice
                    was_voice = (self._detect_voice_input(answer) 
                               if st.session_state.voice_enabled else False)
                    
                    self._submit_test_answer(current_idx, current_question, answer, was_voice)
        
        else:
            # Test completed
            st.success("🎉 Practice test completed!")
            self._display_enhanced_test_results()
    
    def _display_enhanced_test_results(self):
        """Display comprehensive test results with voice input analysis."""
        evaluations = list(st.session_state.practice_test_evaluations.values())
        
        if not evaluations:
            return
        
        # Overall score and input method stats
        avg_score = sum(eval_data['score'] for eval_data in evaluations) / len(evaluations)
        voice_answers = sum(1 for eval_data in evaluations if eval_data.get('was_voice_input', False))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{avg_score:.1f}/10")
        with col2:
            best_score = max(eval_data['score'] for eval_data in evaluations)
            st.metric("Best Score", f"{best_score}/10")
        with col3:
            st.metric("🎤 Voice Used", f"{voice_answers}/{len(evaluations)}")
        with col4:
            completion_time = f"{len(evaluations) * 3}-{len(evaluations) * 4} min"
            st.metric("Time Taken", completion_time)
        
        # Results by question with input method indicators
        st.subheader("📋 Detailed Results")
        
        for i, (question, evaluation) in enumerate(zip(st.session_state.practice_test_questions, evaluations)):
            with st.expander(f"Q{i+1}: {question['competency']} - Score: {evaluation['score']}/10"):
                
                # Input method indicator
                input_method = "🎤 Voice" if evaluation.get('was_voice_input', False) else "⌨️ Text"
                st.markdown(f"**Input Method:** {input_method}")
                
                st.markdown(f"**Question:** {question['question']}")
                st.markdown(f"**Your Answer:** {st.session_state.practice_test_answers[i]}")
                st.markdown("---")
                
                # Use voice-aware evaluation display
                self.voice_component.render_evaluation_with_voice_context(
                    evaluation, 
                    evaluation.get('was_voice_input', False)
                )
        
        # New test button
        st.markdown("---")
        if st.button("🔄 Start New Practice Test", type="primary"):
            self._reset_practice_test()
    
    def _render_progress_charts(self):
        """Render progress charts and analysis."""
        # Progress charts implementation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Score Progression")
            
            # Create score progression chart with input method
            scores_df = pd.DataFrame([
                {
                    'Question': i+1,
                    'Score': eval_data['score'],
                    'Competency': eval_data['competency'],
                    'Input Method': '🎤 Voice' if eval_data.get('was_voice_input', False) else '⌨️ Text'
                }
                for i, eval_data in enumerate(st.session_state.evaluation_results)
            ])
            
            if not scores_df.empty:
                fig = px.scatter(
                    scores_df,
                    x='Question',
                    y='Score',
                    color='Input Method',
                    symbol='Competency',
                    title='Score Progression by Input Method',
                    hover_data=['Competency']
                )
                fig.update_layout(yaxis_range=[0, 10])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Competency Breakdown")
            
            # Competency average scores
            competency_scores = {}
            for eval_data in st.session_state.evaluation_results:
                comp = eval_data['competency']
                if comp not in competency_scores:
                    competency_scores[comp] = []
                competency_scores[comp].append(eval_data['score'])
            
            if competency_scores:
                comp_df = pd.DataFrame([
                    {
                        'Competency': comp,
                        'Average Score': sum(scores) / len(scores),
                        'Attempts': len(scores)
                    }
                    for comp, scores in competency_scores.items()
                ])
                
                fig = px.bar(
                    comp_df,
                    x='Average Score',
                    y='Competency',
                    orientation='h',
                    title='Average Score by Competency',
                    color='Average Score',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_range=[0, 10])
                st.plotly_chart(fig, use_container_width=True)
    
    # Helper methods for practice questions and tests
    def _generate_practice_question(self, competency: str, difficulty: str):
        """Generate a single practice question."""
        with st.spinner(f"🎯 Generating {difficulty} {competency} question..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                question = loop.run_until_complete(
                    st.session_state.interview_manager.generate_practice_question(
                        competency, difficulty=difficulty
                    )
                )
                st.session_state.current_question = question
                st.success(f"✅ Generated {competency} question!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating question: {str(e)}")
    
    def _evaluate_practice_answer(self, question: Dict[str, Any], answer: str, was_voice: bool = False):
        """Evaluate a practice answer with voice input context."""
        with st.spinner("🤖 Evaluating your answer..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                evaluation = loop.run_until_complete(
                    st.session_state.interview_manager.evaluate_answer(question, answer)
                )
                
                # Add voice input context to evaluation
                evaluation['was_voice_input'] = was_voice
                evaluation['input_method'] = '🎤 Voice' if was_voice else '⌨️ Text'
                
                st.session_state.current_evaluation = evaluation
                st.session_state.evaluation_results.append(evaluation)
                st.success("✅ Answer evaluated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error evaluating answer: {str(e)}")
    
    def _start_practice_test(self, num_questions: int):
        """Start a comprehensive practice test."""
        with st.spinner(f"🎯 Generating {num_questions} practice questions..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                questions = loop.run_until_complete(
                    st.session_state.interview_manager.generate_practice_test(num_questions)
                )
                st.session_state.practice_test_questions = questions
                st.session_state.practice_test_answers = {}
                st.session_state.practice_test_evaluations = {}
                st.session_state.practice_test_current_index = 0
                st.session_state.practice_test_completed = False
                st.success(f"✅ Generated {len(questions)} questions!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating practice test: {str(e)}")
    
    def _submit_test_answer(self, idx: int, question: Dict[str, Any], answer: str, was_voice: bool = False):
        """Submit a test answer with voice input context."""
        with st.spinner("Evaluating answer..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                evaluation = loop.run_until_complete(
                    st.session_state.interview_manager.evaluate_answer(question, answer)
                )
                
                # Add voice input context
                evaluation['was_voice_input'] = was_voice
                evaluation['input_method'] = '🎤 Voice' if was_voice else '⌨️ Text'
                
                st.session_state.practice_test_answers[idx] = answer
                st.session_state.practice_test_evaluations[idx] = evaluation
                st.session_state.evaluation_results.append(evaluation)
                
                # Check if test is completed
                if len(st.session_state.practice_test_evaluations) == len(st.session_state.practice_test_questions):
                    st.session_state.practice_test_completed = True
                
                st.rerun()
            except Exception as e:
                st.error(f"Error evaluating answer: {str(e)}")
    
    def _reset_practice_test(self):
        """Reset practice test state."""
        st.session_state.practice_test_questions = []
        st.session_state.practice_test_answers = {}
        st.session_state.practice_test_evaluations = {}
        st.session_state.practice_test_current_index = 0
        st.session_state.practice_test_completed = False
        st.rerun()
    
    def _detect_voice_input(self, answer: str) -> bool:
        """Detect if answer was likely from voice input based on characteristics."""
        if not answer or len(answer.strip()) < 10:
            return False
        
        # Voice input indicators from config
        voice_indicators = [
            "um", "uh", "er", "ah", "you know", "like", "so", "well",
            "I mean", "basically", "actually", "kind of", "sort of"
        ]
        
        # Check for voice-like characteristics
        words = answer.split()
        word_count = len(words)
        filler_count = sum(1 for indicator in voice_indicators if indicator.lower() in answer.lower())
        
        # Heuristic: if answer has many filler words relative to length, likely voice
        filler_ratio = filler_count / max(word_count, 1)
        
        # Also check for natural speech patterns
        has_repetition = len(set(words)) < len(words) * 0.8  # Some word repetition
        has_contractions = any(word for word in words if "'" in word)  # Natural contractions
        
        # Voice detection threshold
        return (filler_ratio > 0.02 or  # 2% filler words
                (filler_ratio > 0.01 and has_contractions) or
                (filler_count > 2 and has_repetition))
    
    def _generate_performance_analysis(self):
        """Generate AI-powered performance analysis."""
        with st.spinner("🧠 Analyzing your performance..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                analysis = loop.run_until_complete(
                    st.session_state.interview_manager.analyze_performance(st.session_state.evaluation_results)
                )
                st.session_state.performance_analysis = analysis
                st.success("✅ Performance analysis completed!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating analysis: {str(e)}")
    
    def _display_performance_analysis(self):
        """Display the performance analysis results."""
        analysis = st.session_state.performance_analysis
        
        if not analysis:
            return
        
        st.subheader("🧠 AI Performance Analysis")
        
        # Overall score
        if analysis.get('overall_score'):
            st.metric("Overall Performance", f"{analysis['overall_score']:.1f}/10")
        
        # Competency breakdown
        if analysis.get('competency_breakdown'):
            st.subheader("📊 Competency Breakdown")
            
            breakdown_data = []
            for comp, data in analysis['competency_breakdown'].items():
                breakdown_data.append({
                    'Competency': comp,
                    'Average Score': data['average_score'],
                    'Attempts': data['attempts'],
                    'Latest Score': data['latest_score'],
                    'Improvement': data.get('improvement', 0)
                })
            
            if breakdown_data:
                df = pd.DataFrame(breakdown_data)
                st.dataframe(df, use_container_width=True)
        
        # Strengths and weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            if analysis.get('strengths'):
                st.subheader("💪 Your Strengths")
                for strength in analysis['strengths']:
                    st.success(f"✅ {strength}")
        
        with col2:
            if analysis.get('weaknesses'):
                st.subheader("📈 Areas to Focus On")
                for weakness in analysis['weaknesses']:
                    st.warning(f"⚠️ {weakness}")
        
        # Recommendations
        if analysis.get('recommendations'):
            st.subheader("🎯 Personalized Recommendations")
            for i, rec in enumerate(analysis['recommendations'], 1):
                st.markdown(f"{i}. {rec}")
        
        # Progress trend
        if analysis.get('progress_trend'):
            trend = analysis['progress_trend']
            if trend == 'improving':
                st.success("📈 You're improving! Keep up the great work!")
            elif trend == 'declining':
                st.warning("📉 Consider reviewing fundamentals and practicing more")
            else:
                st.info("➡️ Your performance is stable")
    
    def _generate_progress_report(self) -> Dict[str, Any]:
        """Generate exportable progress report."""
        voice_count = sum(1 for e in st.session_state.evaluation_results if e.get('was_voice_input', False))
        text_count = len(st.session_state.evaluation_results) - voice_count
        
        return {
            "report_date": datetime.now().isoformat(),
            "candidate_info": {
                "target_role": st.session_state.job_info.get('title', 'Unknown'),
                "industry": st.session_state.job_info.get('industry', 'Unknown')
            },
            "performance_summary": {
                "total_questions": len(st.session_state.evaluation_results),
                "average_score": sum(e['score'] for e in st.session_state.evaluation_results) / len(st.session_state.evaluation_results) if st.session_state.evaluation_results else 0,
                "latest_score": st.session_state.evaluation_results[-1]['score'] if st.session_state.evaluation_results else 0,
                "voice_answers": voice_count,
                "text_answers": text_count,
                "competency_breakdown": self._get_progress_summary()
            },
            "input_method_analysis": {
                "voice_usage_percentage": (voice_count / len(st.session_state.evaluation_results) * 100) if st.session_state.evaluation_results else 0,
                "voice_average_score": sum(e['score'] for e in st.session_state.evaluation_results if e.get('was_voice_input', False)) / max(voice_count, 1),
                "text_average_score": sum(e['score'] for e in st.session_state.evaluation_results if not e.get('was_voice_input', False)) / max(text_count, 1)
            },
            "detailed_results": st.session_state.evaluation_results,
            "practice_test_history": {
                "completed_tests": 1 if st.session_state.practice_test_completed else 0,
                "total_practice_questions": len(st.session_state.evaluation_results)
            }
        }
    
    def _generate_csv_export(self) -> str:
        """Generate CSV export of results."""
        df = pd.DataFrame([
            {
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Question_ID': i+1,
                'Competency': eval_data['competency'],
                'Score': eval_data['score'],
                'Input_Method': 'Voice' if eval_data.get('was_voice_input', False) else 'Text',
                'Overall_Assessment': eval_data.get('overall_assessment', ''),
                'Key_Strengths': '; '.join(eval_data.get('strengths', [])),
                'Improvement_Areas': '; '.join(eval_data.get('improvements', []))
            }
            for i, eval_data in enumerate(st.session_state.evaluation_results)
        ])
        return df.to_csv(index=False)
    
    def _generate_study_plan(self) -> Dict[str, Any]:
        """Generate personalized study plan."""
        # Analyze weak areas
        competency_scores = self._get_progress_summary()
        weak_areas = [comp for comp, score in competency_scores.items() if score < 6]
        strong_areas = [comp for comp, score in competency_scores.items() if score >= 7]
        
        # Voice vs text analysis
        voice_scores = [e['score'] for e in st.session_state.evaluation_results if e.get('was_voice_input', False)]
        text_scores = [e['score'] for e in st.session_state.evaluation_results if not e.get('was_voice_input', False)]
        
        voice_avg = sum(voice_scores) / len(voice_scores) if voice_scores else 0
        text_avg = sum(text_scores) / len(text_scores) if text_scores else 0
        
        preferred_method = "voice" if voice_avg > text_avg else "text" if text_avg > voice_avg else "both"
        
        return {
            "study_plan_date": datetime.now().isoformat(),
            "assessment": {
                "strong_competencies": strong_areas,
                "focus_competencies": weak_areas[:3],
                "overall_readiness": "Developing" if len(weak_areas) > 3 else "Good",
                "preferred_input_method": preferred_method,
                "voice_performance": voice_avg,
                "text_performance": text_avg
            },
            "weekly_schedule": {
                "week_1": {
                    "focus": "STAR method fundamentals",
                    "practice_sessions": 3,
                    "competencies": weak_areas[:2] if weak_areas else ["Problem Solving"],
                    "recommended_input": preferred_method
                },
                "week_2": {
                    "focus": "Industry-specific scenarios", 
                    "practice_sessions": 4,
                    "competencies": weak_areas[2:4] if len(weak_areas) > 2 else ["Technical Expertise"],
                    "recommended_input": "practice both methods"
                },
                "week_3": {
                    "focus": "Mock interviews",
                    "practice_sessions": 3,
                    "competencies": "All competencies",
                    "recommended_input": "voice practice for realism"
                },
                "week_4": {
                    "focus": "Final preparation",
                    "practice_sessions": 2,
                    "competencies": "Review weak areas",
                    "recommended_input": preferred_method
                }
            },
            "goals": {
                "target_overall_score": 8.0,
                "target_weak_area_score": 6.5,
                "recommended_practice_questions": 20,
                "estimated_readiness_weeks": 4,
                "voice_text_balance": "60/40" if preferred_method == "voice" else "40/60" if preferred_method == "text" else "50/50"
            },
            "resources": {
                "star_method_guide": "Focus on Situation, Task, Action, Result structure",
                "industry_research": f"Research {st.session_state.job_info.get('industry', 'your industry')} trends and challenges",
                "company_preparation": "Research the specific company and role",
                "voice_tips": "Practice speaking clearly and at a steady pace" if preferred_method == "voice" else None,
                "text_tips": "Focus on clear, structured writing" if preferred_method == "text" else None
            }
        }
    
    # Utility methods
    def _get_sample_job_description(self) -> str:
        """Return a sample job description."""
        return """
# Senior Software Engineer - AI/ML Platform

## About Us
We are a fast-growing technology company building cutting-edge AI/ML platforms for enterprise customers. Based in San Francisco with remote work options, we're looking for exceptional engineers to join our platform team.

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
    
    def _analyze_job_description(self, job_description: str):
        """Analyze job description and initialize interview manager."""
        with st.spinner("🔍 Analyzing job description..."):
            # Initialize job analyzer
            if not st.session_state.job_analyzer:
                st.session_state.job_analyzer = JobAnalyzer()
            
            # Analyze job
            job_info = st.session_state.job_analyzer.analyze_job_description(job_description)
            st.session_state.job_info = job_info
        
        with st.spinner("🤖 Initializing AI interview coach with voice integration..."):
            # Initialize interview manager
            st.session_state.interview_manager = InterviewManager(job_info)
        
        st.success("✅ Interview preparation system ready with voice & text input!")
        st.rerun()
    
    def _get_progress_summary(self) -> Dict[str, float]:
        """Get progress summary for sidebar and reports."""
        summary = {}
        for eval_data in st.session_state.evaluation_results:
            competency = eval_data['competency']
            if competency not in summary:
                summary[competency] = []
            summary[competency].append(eval_data['score'])
        
        # Calculate averages
        return {comp: sum(scores) / len(scores) for comp, scores in summary.items()}
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score styling."""
        if score >= 8:
            return "score-excellent"
        elif score >= 6:
            return "score-good"
        elif score >= 4:
            return "score-needs-work"
        else:
            return "score-poor"
    
    def _reset_application(self):
        """Reset the entire application state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    """Main application entry point."""
    ui = CompleteInterviewUI()
    
    # Render UI components
    ui.render_header()
    ui.render_sidebar()
    ui.render_main_content()

if __name__ == "__main__":
    main()