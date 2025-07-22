"""
Enhanced Voice Server - Parallel Content and Delivery Analysis
Updated voice server supporting the new enhanced workflow with speech coaching.
"""
import asyncio
import logging
import json
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import enhanced workflow agents
from agents.enhanced_voice_workflow_agent import EnhancedVoiceWorkflowAgent, StreamlinedEnhancedWorkflow
from agents.interview_manager import InterviewManager
from audio_handler import AudioProcessor

logger = logging.getLogger(__name__)

class EnhancedVoiceWorkflowManager:
    """Manages enhanced voice workflow sessions with parallel content and delivery analysis."""
    
    def __init__(self):
        self.enhanced_workflows: Dict[str, EnhancedVoiceWorkflowAgent] = {}
        self.streamlined_workflows: Dict[str, StreamlinedEnhancedWorkflow] = {}
        self.audio_processor = AudioProcessor()
        
        # Performance metrics
        self.metrics = {
            "total_sessions": 0,
            "enhanced_analyses": 0,
            "parallel_successes": 0,
            "content_only_fallbacks": 0,
            "delivery_only_analyses": 0
        }
        
        logger.info("Enhanced Voice Workflow Manager initialized")
    
    def create_enhanced_workflow(self, session_id: str, job_info: Dict[str, Any]) -> bool:
        """Create new enhanced voice workflow session with proper error handling."""
        try:
            logger.info(f"Creating enhanced workflow components for session: {session_id}")
            
            # Ensure job_info has all required fields with defaults
            job_info.setdefault("title", "Professional Position")
            job_info.setdefault("industry", "technology")
            job_info.setdefault("competencies", ["Problem Solving", "Technical Expertise"])
            job_info.setdefault("skills", ["Communication", "Analysis"])
            job_info.setdefault("technologies", ["Professional Tools"])
            job_info.setdefault("experience_level", "mid-level")
            
            # Create both workflow types with error handling
            try:
                self.enhanced_workflows[session_id] = EnhancedVoiceWorkflowAgent(job_info)
                logger.info(f"Enhanced workflow agent created for session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to create enhanced workflow agent: {e}")
                # Continue without enhanced workflow
                self.enhanced_workflows[session_id] = None
            
            try:
                self.streamlined_workflows[session_id] = StreamlinedEnhancedWorkflow(job_info)
                logger.info(f"Streamlined workflow created for session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to create streamlined workflow: {e}")
                # This is more critical - try to create a basic fallback
                self.streamlined_workflows[session_id] = None
                return False
            
            self.metrics["total_sessions"] += 1
            logger.info(f"Enhanced voice workflow session created successfully: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced workflow {session_id}: {e}")
            # Cleanup any partial creations
            if session_id in self.enhanced_workflows:
                del self.enhanced_workflows[session_id]
            if session_id in self.streamlined_workflows:
                del self.streamlined_workflows[session_id]
            return False
    
    def get_enhanced_workflow(self, session_id: str) -> Optional[EnhancedVoiceWorkflowAgent]:
        """Get enhanced workflow by session ID."""
        return self.enhanced_workflows.get(session_id)
    
    def get_streamlined_workflow(self, session_id: str) -> Optional[StreamlinedEnhancedWorkflow]:
        """Get streamlined workflow by session ID."""
        return self.streamlined_workflows.get(session_id)
    
    async def cleanup_enhanced_workflow(self, session_id: str):
        """Cleanup enhanced workflow session."""
        if session_id in self.enhanced_workflows:
            await self.enhanced_workflows[session_id].cleanup()
            del self.enhanced_workflows[session_id]
        
        if session_id in self.streamlined_workflows:
            del self.streamlined_workflows[session_id]
        
        logger.info(f"Cleaned up enhanced workflow session: {session_id}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            **self.metrics,
            "active_enhanced_sessions": len(self.enhanced_workflows),
            "active_streamlined_sessions": len(self.streamlined_workflows)
        }

# Global enhanced manager
enhanced_manager = EnhancedVoiceWorkflowManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting Enhanced Voice Workflow Server...")
    yield
    logger.info("Shutting down enhanced voice server...")
    # Cleanup all enhanced workflows
    for session_id in list(enhanced_manager.enhanced_workflows.keys()):
        await enhanced_manager.cleanup_enhanced_workflow(session_id)

# FastAPI app
app = FastAPI(
    title="Enhanced Voice Workflow Server",
    description="ADK-powered parallel content and delivery analysis workflow",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Voice Workflow API Endpoints

@app.post("/api/voice/enhanced/workflow/create")
async def create_enhanced_workflow(job_info: Dict[str, Any]):
    """Create new enhanced voice workflow session."""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        success = enhanced_manager.create_enhanced_workflow(session_id, job_info)
        if success:
            return {
                "session_id": session_id,
                "status": "created",
                "workflow_type": "enhanced_voice_analysis",
                "features": {
                    "parallel_analysis": True,
                    "content_analysis": True,
                    "delivery_analysis": True,
                    "speech_coaching": True,
                    "industry_optimization": job_info.get("industry", "general")
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create enhanced workflow")
    except Exception as e:
        logger.error(f"Error creating enhanced workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/enhanced/evaluate")
async def evaluate_voice_response_enhanced(
    session_id: str = Form(...),
    question_data: str = Form(...),  # JSON string
    audio_file: UploadFile = File(...),
    use_parallel_analysis: bool = Form(default=True)
):
    """
    Enhanced voice evaluation: Audio → Parallel Content+Delivery Analysis → Synthesis.
    Returns comprehensive evaluation with both content and delivery insights.
    """
    try:
        import json
        
        logger.info(f"Enhanced voice evaluation requested for session: {session_id}")
        
        # Parse question data
        try:
            question = json.loads(question_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid question data JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid question data JSON")
        
        # Log available sessions for debugging
        logger.info(f"Available enhanced sessions: {list(enhanced_manager.enhanced_workflows.keys())}")
        logger.info(f"Available streamlined sessions: {list(enhanced_manager.streamlined_workflows.keys())}")
        
        # Get appropriate workflow with fallback logic
        workflow = None
        workflow_type = "unknown"
        
        if use_parallel_analysis:
            workflow = enhanced_manager.get_enhanced_workflow(session_id)
            if workflow:
                workflow_type = "full_enhanced"
            else:
                logger.warning(f"Enhanced workflow not found for session {session_id}, trying streamlined")
                workflow = enhanced_manager.get_streamlined_workflow(session_id)
                workflow_type = "streamlined_enhanced"
                use_parallel_analysis = False  # Downgrade to streamlined
        else:
            workflow = enhanced_manager.get_streamlined_workflow(session_id)
            workflow_type = "streamlined_enhanced"
        
        # If no workflow found, try to recreate session
        if not workflow:
            logger.error(f"No workflow found for session {session_id}, attempting to recreate")
            
            # Try to extract job_info from question or use defaults
            job_info = question.get('job_info', {
                "title": "Professional Position",
                "industry": "technology",
                "competencies": ["Problem Solving", "Technical Expertise"]
            })
            
            # Recreate session
            success = enhanced_manager.create_enhanced_workflow(session_id, job_info)
            if success:
                workflow = enhanced_manager.get_streamlined_workflow(session_id)
                workflow_type = "recreated_streamlined"
                logger.info(f"Successfully recreated session {session_id}")
            else:
                logger.error(f"Failed to recreate session {session_id}")
                raise HTTPException(status_code=404, detail=f"Enhanced workflow session not found and could not be recreated: {session_id}")
        
        # Read and validate audio data
        audio_data = await audio_file.read()
        if len(audio_data) < 1000:  # 1KB minimum
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file too small ({len(audio_data)} bytes). Please record for at least 3-5 seconds."
            )
        
        # Determine mime type
        mime_type = audio_file.content_type or "audio/wav"
        
        logger.info(f"Processing {len(audio_data)} bytes of {mime_type} audio using {workflow_type}")
        
        # Process through enhanced workflow
        try:
            if use_parallel_analysis and hasattr(workflow, 'process_voice_question_response'):
                # Full enhanced workflow with parallel analysis
                evaluation = await workflow.process_voice_question_response(
                    question, audio_data, mime_type
                )
                enhanced_manager.metrics["enhanced_analyses"] += 1
                if evaluation.get("status") == "success":
                    enhanced_manager.metrics["parallel_successes"] += 1
            else:
                # Streamlined enhanced workflow
                evaluation = await workflow.audio_to_enhanced_evaluation(
                    question, audio_data, mime_type
                )
                enhanced_manager.metrics["enhanced_analyses"] += 1
        except Exception as eval_error:
            logger.error(f"Evaluation processing failed: {eval_error}")
            raise HTTPException(status_code=500, detail=f"Evaluation processing failed: {str(eval_error)}")
        
        logger.info(f"Enhanced voice evaluation completed for session {session_id} using {workflow_type}")
        
        return {
            "evaluation": evaluation,
            "workflow_type": workflow_type,
            "features_used": {
                "parallel_analysis": use_parallel_analysis,
                "content_analysis": True,
                "delivery_analysis": evaluation.get("enhanced_analysis", {}).get("delivery_analysis_available", False),
                "speech_coaching": True
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Enhanced voice evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/delivery/analyze")
async def analyze_delivery_only(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    context: str = Form(default="")  # JSON string with context
):
    """
    Delivery-only analysis: Focus purely on speaking delivery and coaching.
    """
    try:
        # Get enhanced workflow
        workflow = enhanced_manager.get_enhanced_workflow(session_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Enhanced workflow session not found")
        
        # Read audio data
        audio_data = await audio_file.read()
        if len(audio_data) < 1000:
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file too small ({len(audio_data)} bytes). Please record for at least 3-5 seconds."
            )
        
        # Parse context
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except:
                context_data = {"note": context}
        
        # Determine mime type
        mime_type = audio_file.content_type or "audio/wav"
        
        # Analyze delivery only
        delivery_analysis = await workflow.speech_coach_agent.analyze_speech_delivery(
            audio_data, mime_type, context_data
        )
        
        enhanced_manager.metrics["delivery_only_analyses"] += 1
        
        return {
            "delivery_analysis": delivery_analysis,
            "analysis_type": "delivery_only",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Delivery analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/enhanced/capabilities/{session_id}")
async def get_enhanced_capabilities(session_id: str):
    """Get enhanced workflow capabilities and status."""
    try:
        workflow = enhanced_manager.get_enhanced_workflow(session_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Enhanced workflow not found")
        
        capabilities = await workflow.get_workflow_capabilities()
        
        return {
            "session_id": session_id,
            "capabilities": capabilities,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Capabilities check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/voice/enhanced/workflow/{session_id}")
async def cleanup_enhanced_workflow(session_id: str):
    """Cleanup enhanced voice workflow session."""
    try:
        await enhanced_manager.cleanup_enhanced_workflow(session_id)
        return {
            "session_id": session_id, 
            "status": "cleaned_up",
            "workflow_type": "enhanced"
        }
    except Exception as e:
        logger.error(f"Enhanced cleanup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy Voice API (Backward Compatibility)

@app.post("/api/voice/workflow/create")
async def create_voice_workflow(job_info: Dict[str, Any]):
    """Create legacy voice workflow - redirects to enhanced."""
    logger.info("Legacy workflow creation redirected to enhanced workflow")
    return await create_enhanced_workflow(job_info)

@app.post("/api/voice/evaluate")
async def evaluate_voice_response(
    session_id: str = Form(...),
    question_data: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """Legacy voice evaluation - uses streamlined enhanced workflow."""
    logger.info("Legacy voice evaluation using enhanced workflow")
    return await evaluate_voice_response_enhanced(
        session_id, question_data, audio_file, use_parallel_analysis=False
    )

# Traditional HTTP API (unchanged)

@app.post("/api/interview/question/generate")
async def generate_question(request: Dict[str, Any]):
    """Generate practice question (non-streaming)."""
    try:
        job_info = request["job_info"]
        competency = request["competency"]
        difficulty = request.get("difficulty", "balanced")
        
        manager = InterviewManager(job_info)
        question = await manager.generate_practice_question(competency, difficulty=difficulty)
        
        return {"question": question}
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/answer/evaluate")
async def evaluate_answer(request: Dict[str, Any]):
    """Evaluate answer (non-streaming)."""
    try:
        job_info = request["job_info"]
        question = request["question"]
        answer = request["answer"]
        
        manager = InterviewManager(job_info)
        evaluation = await manager.evaluate_answer(question, answer)
        
        return {"evaluation": evaluation}
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/chat")
async def chat_query(request: Dict[str, Any]):
    """Handle chat query (non-streaming)."""
    try:
        job_info = request["job_info"]
        question = request["question"]
        context = request.get("context", "")
        
        manager = InterviewManager(job_info)
        response = await manager.answer_question(question, context)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Status and Health Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "enhanced_workflows": len(enhanced_manager.enhanced_workflows),
        "streamlined_workflows": len(enhanced_manager.streamlined_workflows),
        "service": "enhanced_voice_workflow_server",
        "version": "3.0.0",
        "features": {
            "parallel_content_delivery_analysis": True,
            "speech_coaching": True,
            "industry_optimization": True,
            "adk_powered": True
        }
    }

@app.get("/api/voice/enhanced/metrics")
async def get_enhanced_metrics():
    """Get enhanced workflow performance metrics."""
    metrics = enhanced_manager.get_metrics()
    
    # Calculate success rates
    total_analyses = metrics.get("enhanced_analyses", 0)
    if total_analyses > 0:
        parallel_success_rate = metrics.get("parallel_successes", 0) / total_analyses
        metrics["parallel_success_rate"] = round(parallel_success_rate * 100, 2)
    
    return {
        "metrics": metrics,
        "performance_insights": {
            "enhanced_analysis_available": True,
            "parallel_processing_capability": True,
            "speech_coaching_integration": True,
            "industry_specific_optimization": True
        }
    }

@app.get("/api/voice/enhanced/features")
async def get_enhanced_features():
    """Get available enhanced features."""
    return {
        "enhanced_voice_analysis": {
            "parallel_processing": True,
            "content_analysis": {
                "transcription": True,
                "star_method_evaluation": True,
                "competency_assessment": True,
                "industry_specific": True
            },
            "delivery_analysis": {
                "speech_coaching": True,
                "pace_rhythm_analysis": True,
                "clarity_assessment": True,
                "confidence_evaluation": True,
                "professional_tone_analysis": True,
                "industry_communication_standards": True
            },
            "synthesis_evaluation": {
                "weighted_scoring": True,
                "comprehensive_feedback": True,
                "prioritized_improvements": True,
                "interview_readiness_assessment": True
            }
        },
        "supported_audio_formats": [
            "audio/wav",
            "audio/mp3", 
            "audio/webm",
            "audio/ogg",
            "audio/m4a"
        ],
        "industry_optimizations": [
            "technology",
            "healthcare", 
            "finance",
            "consulting",
            "marketing",
            "sales",
            "education"
        ],
        "workflow_options": {
            "full_parallel_analysis": "Complete parallel content and delivery analysis with synthesis",
            "streamlined_enhanced": "Faster enhanced analysis maintaining compatibility",
            "delivery_only": "Pure speech coaching and delivery analysis"
        }
    }

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("Starting Enhanced Voice Workflow Server on port 8002")
    uvicorn.run(app, host="localhost", port=8002)