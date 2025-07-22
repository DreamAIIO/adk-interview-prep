"""
Enhanced Streamlit Voice Client - Content + Delivery Analysis
Updated client supporting parallel content and delivery analysis with speech coaching.
"""
import streamlit as st
import aiohttp
import asyncio
import json
import io
from typing import Dict, Any, Optional, Tuple
from audiorecorder import audiorecorder

class EnhancedStreamlitVoiceClient:
    """Enhanced voice client with parallel content and delivery analysis."""
    
    def __init__(self, api_base_url: str = "http://localhost:8002"):
        self.api_base_url = api_base_url
        self.enhanced_session_id: Optional[str] = None
        self.enhanced_workflow_active = False
        self.features_available = {
            "parallel_analysis": False,
            "delivery_analysis": False,
            "speech_coaching": False
        }
    
    async def create_enhanced_workflow(self, job_info: Dict[str, Any]) -> bool:
        """Create enhanced voice workflow session with parallel analysis."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/voice/enhanced/workflow/create",
                    json=job_info,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.enhanced_session_id = data["session_id"]
                        self.enhanced_workflow_active = True
                        self.features_available = data.get("features", {})
                        return True
            return False
        except Exception as e:
            st.error(f"Failed to create enhanced voice workflow: {e}")
            return False
    
    async def evaluate_voice_answer_enhanced(
        self,
        job_info: Dict[str, Any],
        question: Dict[str, Any],
        audio_data: bytes,
        use_parallel_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced voice evaluation with parallel content and delivery analysis.
        
        Args:
            job_info: Job information
            question: Interview question
            audio_data: Raw audio bytes
            use_parallel_analysis: Whether to use full parallel analysis
            
        Returns:
            Enhanced evaluation with content and delivery insights
        """
        # Ensure enhanced session exists
        if not self.enhanced_session_id or not self.enhanced_workflow_active:
            if not await self.create_enhanced_workflow(job_info):
                raise Exception("Failed to create enhanced voice workflow")
        
        # Add job_info to question for session recreation if needed
        enhanced_question = question.copy()
        enhanced_question["job_info"] = job_info
        
        try:
            # Prepare multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.enhanced_session_id)
            form_data.add_field('question_data', json.dumps(enhanced_question))
            form_data.add_field('use_parallel_analysis', str(use_parallel_analysis).lower())
            form_data.add_field(
                'audio_file', 
                io.BytesIO(audio_data),
                filename='response.wav',
                content_type='audio/wav'
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/voice/enhanced/evaluate",
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=120)  # Longer timeout for parallel analysis
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        evaluation = data["evaluation"]
                        
                        # Add metadata about the analysis type
                        evaluation["enhanced_metadata"] = {
                            "analysis_type": "enhanced_voice_evaluation",
                            "parallel_analysis_used": use_parallel_analysis,
                            "features_used": data.get("features_used", {}),
                            "workflow_type": data.get("workflow_type", "unknown"),
                            "session_id": self.enhanced_session_id
                        }
                        
                        return evaluation
                    elif response.status == 404:
                        # Session not found, try to recreate
                        st.warning("🔄 Session expired, recreating enhanced workflow...")
                        self.enhanced_session_id = None
                        self.enhanced_workflow_active = False
                        
                        # Retry once with new session
                        if await self.create_enhanced_workflow(job_info):
                            return await self.evaluate_voice_answer_enhanced(
                                job_info, question, audio_data, use_parallel_analysis
                            )
                        else:
                            raise Exception("Could not recreate enhanced workflow session")
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except aiohttp.ClientConnectorError:
            st.error("Cannot connect to enhanced voice server. Please ensure it's running.")
            return self._fallback_enhanced_evaluation(question, "Server connection failed")
        except asyncio.TimeoutError:
            st.error("Enhanced voice evaluation timed out. Server may be busy.")
            return self._fallback_enhanced_evaluation(question, "Evaluation timed out")
        except Exception as e:
            st.error(f"Error in enhanced voice evaluation: {e}")
            return self._fallback_enhanced_evaluation(question, str(e))
    
    async def analyze_delivery_only(
        self,
        job_info: Dict[str, Any],
        audio_data: bytes,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Pure delivery analysis for speech coaching.
        
        Args:
            job_info: Job information
            audio_data: Raw audio bytes
            context: Analysis context
            
        Returns:
            Speech delivery analysis and coaching recommendations
        """
        if not self.enhanced_session_id:
            if not await self.create_enhanced_workflow(job_info):
                raise Exception("Failed to create enhanced voice workflow")
        
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('session_id', self.enhanced_session_id)
            form_data.add_field('context', json.dumps(context or {}))
            form_data.add_field(
                'audio_file',
                io.BytesIO(audio_data),
                filename='delivery_analysis.wav',
                content_type='audio/wav'
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/voice/delivery/analyze",
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["delivery_analysis"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Delivery analysis failed: HTTP {response.status}: {error_text}")
        except Exception as e:
            st.error(f"Delivery analysis error: {e}")
            return {"error": str(e), "overall_score": 0}
    
    # UI Rendering Methods - Enhanced
    
    def render_enhanced_input_mode_selector(self, key: str = "enhanced_input_mode") -> str:
        """Render enhanced input mode selector with delivery analysis info."""
        st.markdown("### 🎯 Response Method")
        
        col1, col2 = st.columns(2)
        
        with col1:
            text_selected = st.button(
                "✍️ Type Response",
                help="Write your answer using text input",
                use_container_width=True,
                key=f"{key}_text_btn"
            )
        
        with col2:
            voice_selected = st.button(
                "🎤 Speak Response",
                help="Record your answer with voice (includes delivery coaching!)",
                use_container_width=True,
                type="primary" if self.enhanced_workflow_active else "secondary",
                key=f"{key}_voice_btn"
            )
        
        # Enhanced features info
        if self.enhanced_workflow_active and self.features_available.get("delivery_analysis"):
            st.info("🎤 **Voice mode includes speech coaching!** Get feedback on both what you say and how you say it.")
        elif not self.enhanced_workflow_active:
            st.warning("🎤 Enhanced voice features initializing... Text mode fully available.")
        
        # Store selection in session state
        if text_selected:
            st.session_state[key] = "text"
        elif voice_selected:
            st.session_state[key] = "voice"
        
        # Return current selection (default to text)
        return st.session_state.get(key, "text")
    
    def render_enhanced_answer_input(
        self, 
        input_mode: str, 
        question: Dict[str, Any], 
        key: str = "enhanced_answer_input"
    ) -> Tuple[Any, bool]:
        """
        Render enhanced answer input with delivery coaching info.
        Returns: (answer_data, is_voice_mode)
        """
        if input_mode == "text":
            text_answer = self._render_text_input_enhanced(question, key)
            return text_answer, False
        else:
            audio_data = self._render_voice_input_enhanced(question, key)
            return audio_data, True
    
    def _render_text_input_enhanced(self, question: Dict[str, Any], key: str) -> str:
        """Enhanced text input with improved guidance."""
        competency = question.get('competency', 'General')
        
        # Enhanced STAR method guidance
        with st.expander("💡 Enhanced Response Guide", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **📋 STAR Method Structure:**
                
                🎯 **Situation**: Set the context and background
                📋 **Task**: Describe your responsibility or goal  
                ⚡ **Action**: Explain the specific steps you took
                🏆 **Result**: Share the outcome and impact
                """)
            
            with col2:
                st.markdown(f"""
                **🎤 Voice Mode Benefits:**
                
                ✨ **Content Analysis**: STAR method evaluation
                🗣️ **Delivery Coaching**: Speaking style feedback
                📊 **Comprehensive Score**: Content + delivery
                🎯 **Industry-Specific**: {question.get('industry', 'Professional')} standards
                """)
        
        answer = st.text_area(
            f"Your {competency} Answer",
            height=200,
            placeholder=self._get_enhanced_star_placeholder(competency),
            key=key,
            help="💡 Consider using voice mode for additional delivery coaching and comprehensive analysis!"
        )
        
        # Enhanced character count and guidance
        if answer:
            word_count = len(answer.split())
            char_count = len(answer)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"📝 {word_count} words")
            with col2:
                st.caption(f"📄 {char_count} characters")
            with col3:
                if word_count < 50:
                    st.caption("💡 Add more detail")
                elif word_count > 200:
                    st.caption("✂️ Keep focused")
                else:
                    st.caption("✅ Good length")
        
        return answer
    
    def _render_voice_input_enhanced(self, question: Dict[str, Any], key: str) -> Optional[bytes]:
        """Enhanced voice input with delivery coaching preview."""
        st.markdown("### 🎤 Voice Response with Delivery Coaching")
        
        # Enhanced workflow status
        if not self.enhanced_workflow_active:
            st.warning("🔄 Enhanced voice workflow initializing...")
            return None
        
        # Enhanced voice guidance
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
            📋 **Enhanced Voice Recording Tips:**
            - **Speak for at least 30-60 seconds** for comprehensive analysis
            - Use clear, professional tone appropriate for interviews
            - Structure your response using STAR method
            - Speak at a measured pace for technical discussions
            - Include specific examples and quantifiable results
            """)
        
        with col2:
            if not self.features_available.get("delivery_analysis"):
                st.info("**📊 Content analysis ready**\n\nDelivery coaching initializing...")
        
        # Audio recorder
        audio_data = audiorecorder("🎤 Click to record enhanced response", key=f"{key}_enhanced_recorder")
        
        # Handle recorded audio with enhanced validation
        if audio_data is not None and len(audio_data) > 0:
            import io
            wav_io = io.BytesIO()
            audio_data.export(wav_io, format="wav")
            wav_bytes = wav_io.getvalue()
            audio_size_kb = len(wav_bytes) / 1024
            duration_estimate = audio_size_kb / 32  # ~32KB per second
            
            # Enhanced validation for delivery analysis
            if len(wav_bytes) < 1000:
                st.error("⚠️ **Recording too short for enhanced analysis!** Please record for at least 30 seconds.")
                st.info("💡 **Enhanced Tip:** Longer responses provide better delivery coaching insights.")
                return None
            
            # Enhanced recording confirmation
            if duration_estimate >= 30:
                st.success(f"✅ **Excellent recording!** ({audio_size_kb:.1f} KB, ~{duration_estimate:.1f}s) - Perfect for enhanced analysis")
            elif duration_estimate >= 15:
                st.success(f"✅ **Good recording!** ({audio_size_kb:.1f} KB, ~{duration_estimate:.1f}s) - Enhanced analysis ready")
            else:
                st.warning(f"⚠️ **Short recording** ({audio_size_kb:.1f} KB, ~{duration_estimate:.1f}s) - Consider recording longer for better coaching")
            
            # Enhanced preview with delivery insights
            with st.expander("🔍 Enhanced Recording Preview", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.audio(wav_bytes, format='audio/wav')
                    st.caption(f"📊 Size: {audio_size_kb:.1f} KB")
                    st.caption(f"⏱️ Duration: ~{duration_estimate:.1f} seconds")
                
                with col2:
                    st.markdown("**🎯 Enhanced Analysis Preview:**")
                    if duration_estimate >= 30:
                        st.success("✓ Excellent for delivery coaching")
                        st.success("✓ Great for content analysis")
                        st.success("✓ Perfect for comprehensive evaluation")
                    elif duration_estimate >= 15:
                        st.success("✓ Good for delivery coaching")
                        st.success("✓ Good for content analysis")
                        st.info("→ Longer responses = better insights")
                    else:
                        st.warning("→ Brief for delivery coaching")
                        st.success("✓ Adequate for content analysis")
                        st.info("💡 Try 30+ seconds for full coaching")
                
                # Option to re-record
                if st.button("🔄 Record Again", key=f"{key}_re_record_enhanced"):
                    st.rerun()
            
            return wav_bytes
        else:
            st.info("🎙️ **Click the microphone above to record your enhanced response**")
            st.caption("💡 Aim for 30-60 seconds to get the most comprehensive feedback on both content and delivery")
            return None
    
    def render_enhanced_evaluation(self, evaluation: Dict[str, Any], use_expander: bool = True):
        """Render enhanced evaluation with content and delivery insights."""
        if not evaluation:
            return
        
        enhanced_meta = evaluation.get('enhanced_metadata', {})
        enhanced_analysis = evaluation.get('enhanced_analysis', {})
        
        # Check analysis types available
        has_content = enhanced_analysis.get('content_analysis_available', False)
        has_delivery = enhanced_analysis.get('delivery_analysis_available', False)
        parallel_used = enhanced_meta.get('parallel_analysis_used', False)
        
        # Enhanced score display
        overall_score = evaluation.get('score', 0)
        content_score = enhanced_analysis.get('content_score', 0)
        delivery_score = enhanced_analysis.get('delivery_score', 0)
        competency = evaluation.get('competency', 'Assessment')
        
        # Modern enhanced score visualization
        if has_content and has_delivery:
            # Full enhanced evaluation display
            st.markdown("### 🎯 Enhanced Interview Evaluation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                self._render_score_card(overall_score, "Overall Score", "🎯", "combined")
            with col2:
                self._render_score_card(content_score, "Content", "📝", "content")
            with col3:
                self._render_score_card(delivery_score, "Delivery", "🎤", "delivery")
            
            # Analysis type indicator
            analysis_type = "🔄 Parallel Analysis" if parallel_used else "⚡ Enhanced Analysis"
            st.info(f"{analysis_type} • Content + Delivery • Speech Coaching Included")
            
        else:
            # Fallback display for partial analysis
            col1, col2 = st.columns([2, 1])
            with col1:
                self._render_score_card(overall_score, f"{competency} Assessment", "🎯", "overall")
            with col2:
                if has_delivery:
                    st.success("🎤 Delivery analysis included")
                else:
                    st.info("📝 Content analysis completed")
        
        # Enhanced assessment
        if evaluation.get('overall_assessment'):
            st.markdown("### 📋 Comprehensive Assessment")
            st.info(evaluation['overall_assessment'])
        
        # Enhanced insights tabs
        if has_content and has_delivery:
            tab1, tab2, tab3 = st.tabs(["🎯 Key Insights", "📝 Content Analysis", "🎤 Delivery Coaching"])
            
            with tab1:
                self._render_combined_insights(evaluation, enhanced_analysis)
            
            with tab2:
                self._render_content_analysis_tab(evaluation)
            
            with tab3:
                self._render_delivery_coaching_tab(enhanced_analysis)
        else:
            # Single analysis view
            if has_delivery:
                self._render_delivery_coaching_section(enhanced_analysis)
            self._render_content_analysis_section(evaluation)
    
    def _render_score_card(self, score: float, title: str, icon: str, type: str):
        """Render individual score card with color coding."""
        colors = {
            "combined": {"high": "#22c55e", "med": "#f59e0b", "low": "#ef4444"},
            "content": {"high": "#3b82f6", "med": "#6366f1", "low": "#8b5cf6"},
            "delivery": {"high": "#10b981", "med": "#06b6d4", "low": "#84cc16"}
        }
        
        color_set = colors.get(type, colors["combined"])
        color = color_set["high"] if score >= 7 else color_set["med"] if score >= 5 else color_set["low"]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: {color}15; border: 2px solid {color}; border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 2.2em; font-weight: bold; color: {color}; margin-bottom: 5px;">
                {score}/10
            </div>
            <div style="font-size: 1em; color: #666; font-weight: 500;">
                {title}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_combined_insights(self, evaluation: Dict[str, Any], enhanced_analysis: Dict[str, Any]):
        """Render combined insights from both content and delivery."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💪 Combined Strengths")
            strengths = evaluation.get('strengths', [])
            for strength in strengths[:4]:
                st.success(f"✓ {strength}")
            
            # Add delivery strengths
            delivery_strengths = enhanced_analysis.get('delivery_strengths', [])
            for strength in delivery_strengths[:2]:
                st.success(f"🎤 {strength}")
        
        with col2:
            st.markdown("#### 📈 Priority Improvements")
            improvements = evaluation.get('improvements', [])
            for improvement in improvements[:4]:
                st.warning(f"→ {improvement}")
            
            # Add delivery improvements
            delivery_improvements = enhanced_analysis.get('delivery_improvements', [])
            for improvement in delivery_improvements[:2]:
                st.warning(f"🎤 {improvement}")
        
        # Industry-specific delivery advice
        if enhanced_analysis.get('industry_delivery_advice'):
            st.markdown("#### 🎯 Industry Communication Guidance")
            st.info(enhanced_analysis['industry_delivery_advice'])
    
    def _render_content_analysis_tab(self, evaluation: Dict[str, Any]):
        """Render detailed content analysis."""
        st.markdown("#### 📝 Content Quality Analysis")
        
        # STAR analysis
        star_analysis = evaluation.get('star_analysis', {})
        if any(star_analysis.values()):
            st.markdown("**⭐ STAR Method Evaluation:**")
            
            star_cols = st.columns(4)
            star_components = [
                ("Situation", star_analysis.get('situation', '')),
                ("Task", star_analysis.get('task', '')),
                ("Action", star_analysis.get('action', '')),
                ("Result", star_analysis.get('result', ''))
            ]
            
            for col, (component, feedback) in zip(star_cols, star_components):
                with col:
                    st.markdown(f"**{component}**")
                    if feedback and "good" in feedback.lower():
                        st.success(f"✓ {feedback}")
                    elif feedback:
                        st.warning(f"→ {feedback}")
                    else:
                        st.caption("Could be more detailed")
        
        # Content strengths and improvements
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💡 Content Strengths:**")
            content_strengths = [s for s in evaluation.get('strengths', []) if not s.startswith('Speaking:')]
            if content_strengths:
                for strength in content_strengths:
                    st.success(f"✓ {strength}")
            else:
                for strength in evaluation.get('strengths', [])[:3]:
                    st.success(f"✓ {strength}")
        
        with col2:
            st.markdown("**📈 Content Improvements:**")
            content_improvements = [i for i in evaluation.get('improvements', []) if not i.startswith('Delivery:')]
            if content_improvements:
                for improvement in content_improvements:
                    st.warning(f"→ {improvement}")
            else:
                for improvement in evaluation.get('improvements', [])[:3]:
                    st.warning(f"→ {improvement}")
        
        # Missing elements
        if evaluation.get('missing_elements'):
            st.markdown("**🔍 Missing Elements:**")
            for element in evaluation.get('missing_elements', [])[:3]:
                st.info(f"💭 {element}")
        
        # Detailed improvement advice - RESTORED
        if evaluation.get('advice'):
            st.markdown("**💡 Detailed Improvement Advice:**")
            st.info(evaluation['advice'])
        
        # Sample strong answer - RESTORED
        if evaluation.get('sample_answer'):
            st.markdown("**📝 Example Strong Answer:**")
            st.success(evaluation['sample_answer'])
    
    def _render_delivery_coaching_tab(self, enhanced_analysis: Dict[str, Any]):
        """Render detailed delivery coaching analysis."""
        st.markdown("#### 🎤 Speech Delivery Coaching")
        
        delivery_score = enhanced_analysis.get('delivery_score', 0)
        
        # Delivery score breakdown (if available from detailed analysis)
        st.markdown("**📊 Delivery Performance Breakdown:**")
        
        delivery_aspects = [
            ("Pace & Rhythm", "🎵"),
            ("Clarity & Articulation", "🗣️"),
            ("Confidence & Authority", "💪"),
            ("Professional Tone", "👔"),
            ("Energy & Engagement", "⚡"),
            ("Speech Patterns", "🔄")
        ]
        
        cols = st.columns(3)
        for i, (aspect, emoji) in enumerate(delivery_aspects):
            with cols[i % 3]:
                # Mock scoring for display (would come from detailed analysis)
                score = delivery_score + (i % 3) - 1  # Slight variation for demo
                color = "#22c55e" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: {color}15; border: 1px solid {color}; border-radius: 8px; margin: 5px 0;">
                    <div style="font-size: 1.2em;">{emoji}</div>
                    <div style="font-weight: bold; color: {color};">{score}/10</div>
                    <div style="font-size: 0.8em; color: #666;">{aspect}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Speaking tips and coaching
        col1, col2 = st.columns(2)
        
        with col1:
            speaking_tips = enhanced_analysis.get('speaking_tips', [])
            if speaking_tips:
                st.markdown("**🎯 Speaking Tips:**")
                for tip in speaking_tips:
                    st.info(f"💡 {tip}")
        
        with col2:
            delivery_strengths = enhanced_analysis.get('delivery_strengths', [])
            if delivery_strengths:
                st.markdown("**🌟 Delivery Strengths:**")
                for strength in delivery_strengths:
                    st.success(f"✓ {strength}")
    
    def _render_delivery_coaching_section(self, enhanced_analysis: Dict[str, Any]):
        """Render delivery coaching as a section (for single analysis view)."""
        st.markdown("### 🎤 Speech Delivery Coaching")
        
        delivery_score = enhanced_analysis.get('delivery_score', 0)
        st.metric("Delivery Score", f"{delivery_score}/10")
        
        col1, col2 = st.columns(2)
        
        with col1:
            speaking_tips = enhanced_analysis.get('speaking_tips', [])
            if speaking_tips:
                st.markdown("**🎯 Speaking Improvement Tips:**")
                for tip in speaking_tips[:3]:
                    st.info(f"💡 {tip}")
        
        with col2:
            delivery_strengths = enhanced_analysis.get('delivery_strengths', [])
            if delivery_strengths:
                st.markdown("**🌟 Delivery Strengths:**")
                for strength in delivery_strengths[:3]:
                    st.success(f"✓ {strength}")
    
    def _render_content_analysis_section(self, evaluation: Dict[str, Any]):
        """Render content analysis as a section."""
        if evaluation.get('star_analysis'):
            st.markdown("### ⭐ Content Analysis")
            
            # Simplified STAR display
            star_analysis = evaluation.get('star_analysis', {})
            if any(star_analysis.values()):
                for component in ["situation", "task", "action", "result"]:
                    feedback = star_analysis.get(component, '')
                    if feedback:
                        st.caption(f"**{component.title()}**: {feedback}")
        
        # Add missing detailed sections for single analysis view
        col1, col2 = st.columns(2)
        
        with col1:
            if evaluation.get('advice'):
                st.markdown("**💡 Improvement Advice:**")
                st.info(evaluation['advice'])
        
        with col2:
            if evaluation.get('sample_answer'):
                st.markdown("**📝 Example Answer:**")
                st.success(evaluation['sample_answer'])
    
    def _get_enhanced_star_placeholder(self, competency: str) -> str:
        """Get enhanced STAR method placeholder with delivery hints."""
        base_template = f"""Situation: Describe a specific {competency.lower()} challenge you faced...

Task: Explain your responsibilities and what needed to be accomplished...

Action: Detail the specific steps you took (speak clearly about your role)...

Result: Share measurable outcomes and impact (quantify when possible)...

💡 Voice Tip: When recording, speak at a measured pace and use specific examples that demonstrate your expertise clearly."""
        
        return base_template
    
    def _fallback_enhanced_evaluation(self, question: Dict[str, Any], error_msg: str = "") -> Dict[str, Any]:
        """Generate fallback evaluation for enhanced workflow failures."""
        return {
            "score": 0,
            "overall_assessment": f"Enhanced voice analysis encountered an issue. Please try recording again with clear audio. Error: {error_msg}",
            "competency": question.get("competency", "Unknown"),
            "strengths": [],
            "improvements": [
                "Try recording again with clearer audio",
                "Ensure stable internet connection",
                "Speak for at least 30 seconds for full analysis",
                "Consider using text input as alternative"
            ],
            "enhanced_analysis": {
                "content_analysis_available": False,
                "delivery_analysis_available": False,
                "error": error_msg
            },
            "enhanced_metadata": {
                "analysis_type": "enhanced_voice_evaluation_failed",
                "parallel_analysis_used": False,
                "error": error_msg
            }
        }
    
    async def cleanup_enhanced_session(self):
        """Cleanup enhanced voice session."""
        if self.enhanced_session_id:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.delete(f"{self.api_base_url}/api/voice/enhanced/workflow/{self.enhanced_session_id}")
            except:
                pass
            finally:
                self.enhanced_session_id = None
                self.enhanced_workflow_active = False
                self.features_available = {
                    "parallel_analysis": False,
                    "delivery_analysis": False,
                    "speech_coaching": False
                }
    
    async def get_enhanced_capabilities(self) -> Dict[str, Any]:
        """Get enhanced workflow capabilities."""
        if not self.enhanced_session_id:
            return {"error": "No enhanced session active"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/api/voice/enhanced/capabilities/{self.enhanced_session_id}"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": "Could not fetch capabilities"}
        except Exception as e:
            return {"error": str(e)}
    
    # HTTP API methods (from original client)
    async def generate_question_http(self, job_info: Dict[str, Any], competency: str, difficulty: str = "balanced") -> Dict[str, Any]:
        """Generate question via HTTP API (non-streaming)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/interview/question/generate",
                    json={
                        "job_info": job_info,
                        "competency": competency,
                        "difficulty": difficulty
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["question"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except Exception as e:
            st.error(f"Error generating question: {e}")
            return {}
    
    async def evaluate_answer_http(self, job_info: Dict[str, Any], question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Evaluate answer via HTTP API (non-streaming)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/interview/answer/evaluate",
                    json={
                        "job_info": job_info,
                        "question": question,
                        "answer": answer
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["evaluation"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except Exception as e:
            st.error(f"Error evaluating answer: {e}")
            return {}
    
    async def chat_query_http(self, job_info: Dict[str, Any], question: str, context: str = "") -> str:
        """Handle chat query via HTTP API (non-streaming)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/interview/chat",
                    json={
                        "job_info": job_info,
                        "question": question,
                        "context": context
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["response"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        except Exception as e:
            st.error(f"Error processing chat: {e}")
            return f"Sorry, I encountered an error: {e}"
    
    # Legacy methods for backward compatibility
    async def create_voice_workflow(self, job_info: Dict[str, Any]) -> bool:
        """Legacy method - redirects to enhanced workflow."""
        return await self.create_enhanced_workflow(job_info)
    
    async def evaluate_voice_answer_direct(
        self,
        job_info: Dict[str, Any],
        question: Dict[str, Any],
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Legacy method - uses enhanced evaluation with streamlined mode."""
        return await self.evaluate_voice_answer_enhanced(
            job_info, question, audio_data, use_parallel_analysis=False
        )
    
    def render_input_mode_selector(self, key: str = "input_mode") -> str:
        """Legacy method - redirects to enhanced selector."""
        return self.render_enhanced_input_mode_selector(key)
    
    def render_answer_input(self, input_mode: str, question: Dict[str, Any], key: str = "answer_input") -> Tuple[Any, bool]:
        """Legacy method - redirects to enhanced input."""
        return self.render_enhanced_answer_input(input_mode, question, key)
    
    def render_clean_evaluation(self, evaluation: Dict[str, Any], use_expander: bool = True):
        """Legacy method - redirects to enhanced evaluation."""
        return self.render_enhanced_evaluation(evaluation, use_expander)