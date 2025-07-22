"""
Configuration file for the Interview Preparation Assistant.
UPDATED: Full ADK voice streaming integration with modern UI settings.
"""
import os
import logging.config
from pathlib import Path

# Application Configuration
APP_NAME = "Interview Preparation Assistant"
VERSION = "3.0.0-ADK-VOICE"

# Base Directory
BASE_DIR = Path(__file__).parent

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Model Configuration - ADK Voice Streaming
DEFAULT_MODEL = "gemini-2.0-flash"  # Standard model for text operations
#VOICE_MODEL = DEFAULT_MODEL  # Use the same model for voice
VOICE_MODEL = "gemini-2.0-flash-live-001"

# Vertex AI Configuration (if using Vertex AI instead of Google AI)
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() == "true"

# Voice Streaming Configuration - ADK Integration
VOICE_STREAMING_CONFIG = {
    "enabled": True,
    "server_host": "localhost",
    "server_port": 8002,
    "websocket_url": "ws://localhost:8002",
    "audio_sample_rate": 16000,
    "audio_channels": 1,
    "audio_format": "pcm",
    "mime_type": "audio/pcm",
    "response_modalities": ["AUDIO", "TEXT"],
    "default_modality": "TEXT",
    "websocket_timeout": 30,
    "connection_retry_attempts": 3,
    "connection_retry_delay": 2,
    "session_cleanup_timeout": 300,  # 5 minutes
    "max_concurrent_sessions": 10
}

# ADK Configuration
ADK_CONFIG = {
    "app_name_prefix": "interview_prep",
    "session_service": "InMemorySessionService",
    "runner_type": "InMemoryRunner", 
    "live_streaming_enabled": True,
    "run_config": {
        "response_modalities": ["TEXT", "AUDIO"],
        "default_response_modality": "TEXT"
    },
    "session_management": {
        "auto_cleanup": True,
        "session_timeout": 1800,  # 30 minutes
        "max_sessions_per_user": 3
    }
}

# Core Competencies for Interview Preparation
CORE_COMPETENCIES = [
    "Problem Solving",
    "Technical Expertise", 
    "Project Management",
    "Analytical Thinking",
    "Attention to Detail",
    "Written Communication",
    "Leadership",
    "Teamwork"
]

# Industry Keywords for Job Analysis
INDUSTRY_KEYWORDS = {
    "technology": [
        "software", "engineer", "developer", "programming", "coding", "tech", "IT",
        "data", "machine learning", "AI", "cloud", "DevOps", "frontend", "backend",
        "full stack", "mobile", "web", "API", "database", "python", "java", "javascript"
    ],
    "healthcare": [
        "medical", "healthcare", "hospital", "clinical", "patient", "nurse", "doctor",
        "physician", "therapy", "pharmaceutical", "biotech", "medical device", "health",
        "treatment", "diagnosis", "care", "medicine", "surgery", "emergency"
    ],
    "finance": [
        "financial", "banking", "investment", "trading", "finance", "analyst", "portfolio",
        "risk", "compliance", "audit", "accounting", "fintech", "insurance", "credit",
        "wealth", "capital", "markets", "securities", "derivatives", "treasury"
    ],
    "consulting": [
        "consulting", "consultant", "advisory", "strategy", "management", "business",
        "analysis", "transformation", "optimization", "process", "client", "engagement",
        "project", "stakeholder", "solution", "recommendation", "implementation"
    ],
    "marketing": [
        "marketing", "digital", "campaign", "brand", "advertising", "content", "social media",
        "SEO", "SEM", "analytics", "conversion", "engagement", "customer", "acquisition",
        "retention", "growth", "creative", "design", "copywriting", "communications"
    ]
}

# Scoring Thresholds
SCORE_THRESHOLDS = {
    "excellent": 8,
    "good": 6,
    "needs_improvement": 4,
    "poor": 0
}

# Modern UI Configuration
UI_CONFIG = {
    "theme": "modern",
    "input_mode_style": "toggle",  # Modern toggle switch
    "evaluation_style": "clean",   # Clean evaluations without input method indicators
    "color_scheme": {
        "primary": "#667eea",
        "secondary": "#764ba2", 
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#3b82f6"
    },
    "spacing": {
        "card_padding": "1.5rem",
        "section_margin": "2rem",
        "component_gap": "1rem"
    },
    "animations": {
        "enabled": True,
        "transition_duration": "0.3s",
        "hover_effects": True
    },
    "responsive": {
        "mobile_breakpoint": "768px",
        "tablet_breakpoint": "1024px",
        "desktop_breakpoint": "1200px"
    },
    "voice_ui": {
        "show_input_method_badges": False,  # Don't show voice/text indicators
        "show_mode_toggle": True,           # Show the modern toggle
        "clean_evaluations": True,          # Clean evaluation display
        "modern_voice_controls": True       # Modern voice control styling
    }
}

# Input Method Configuration
INPUT_METHOD_CONFIG = {
    "default_mode": "text",  # text, voice
    "allow_switching": True,
    "voice_detection": {
        "enabled": False,  # No longer detecting voice vs text automatically
        "confidence_threshold": 0.7,
        "filler_word_ratio": 0.02
    },
    "text_input": {
        "placeholder_templates": True,
        "star_method_hints": True,
        "competency_specific_guidance": True
    },
    "voice_input": {
        "real_time_transcript": True,
        "confidence_display": True,
        "auto_submit": False,
        "manual_controls": True
    }
}

# API Configuration - Updated for Voice Streaming
API_CONFIG = {
    "timeout_seconds": 30,
    "max_retries": 3,
    "retry_delay_seconds": 1,
    "request_rate_limit": 100,
    "concurrent_requests": 10,
    "voice_streaming": {
        "enabled": True,
        "websocket_ping_interval": 20,
        "websocket_ping_timeout": 10,
        "max_message_size": 1024 * 1024,  # 1MB
        "compression": True
    },
    "endpoints": {
        "google_ai": "https://generativelanguage.googleapis.com",
        "vertex_ai": "https://us-central1-aiplatform.googleapis.com",
        "voice_server": "http://localhost:8002"
    },
    "headers": {
        "user_agent": f"{APP_NAME}/{VERSION}",
        "accept": "application/json",
        "content_type": "application/json"
    }
}

# Audio Processing Configuration
AUDIO_CONFIG = {
    "input": {
        "sample_rate": 16000,
        "channels": 1,
        "bit_depth": 16,
        "format": "pcm",
        "encoding": "int16",
        "chunk_size": 1024,
        "buffer_duration": 0.1  # 100ms chunks
    },
    "output": {
        "sample_rate": 24000,
        "channels": 1,
        "format": "pcm",
        "encoding": "int16"
    },
    "processing": {
        "noise_suppression": True,
        "echo_cancellation": True,
        "auto_gain_control": True,
        "voice_activity_detection": True
    },
    "streaming": {
        "real_time": True,
        "low_latency": True,
        "buffer_management": "automatic"
    }
}

# Development Configuration
DEV_CONFIG = {
    "debug_mode": os.getenv("DEBUG", "False").lower() == "true",
    "hot_reload": True,
    "verbose_logging": True,
    "voice_debug_mode": True,
    "adk_debug_mode": True,
    "websocket_debug": True,
    "development_tools": {
        "api_inspector": True,
        "performance_monitor": True,
        "error_tracker": True,
        "voice_stream_monitor": True
    },
    "mock_services": {
        "mock_voice_streaming": False,  # Use real ADK voice streaming
        "mock_evaluations": False,
        "mock_progress_tracking": False
    }
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "async_enabled": True,
    "connection_pooling": True,
    "request_batching": True,
    "lazy_loading": True,
    "caching_strategy": "moderate",
    "memory_optimization": True,
    "voice_streaming_optimization": {
        "buffer_size": 4096,
        "max_concurrent_streams": 5,
        "stream_timeout": 30,
        "auto_cleanup": True,
        "memory_limit": "100MB"
    },
    "ui_optimization": {
        "component_caching": True,
        "lazy_chart_rendering": True,
        "efficient_state_management": True
    }
}

# Security Configuration
SECURITY_CONFIG = {
    "encryption_enabled": True,
    "data_anonymization": True,
    "session_security": True,
    "api_key_rotation": True,
    "audit_logging": True,
    "voice_data_handling": {
        "no_audio_storage": True,        # Never store raw audio
        "transcript_only": True,         # Only keep text transcripts
        "real_time_processing": True,    # Process and discard immediately
        "privacy_first": True,           # Privacy by design
        "secure_websockets": True        # Use secure WebSocket connections in production
    },
    "cors": {
        "allowed_origins": ["http://localhost:8501"],  # Add production domains
        "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
        "allowed_headers": ["*"],
        "allow_credentials": True
    }
}

# Feature Flags - Updated
FEATURE_FLAGS = {
    "adk_voice_streaming": True,        # NEW: Full ADK voice streaming
    "modern_ui": True,                  # NEW: Modern UI with clean design
    "real_time_evaluation": True,
    "progress_tracking": True,
    "competency_analysis": True,
    "job_analysis": True,
    "practice_mode": True,
    "mock_interview": True,
    "feedback_system": True,
    "clean_evaluations": True,          # NEW: Clean evaluation display
    "input_mode_toggle": True,          # NEW: Modern input mode switching
    "websocket_voice": True,            # NEW: WebSocket-based voice streaming
    # REMOVED: Legacy voice features
    "analytics_dashboard": True,
    "multi_language": False,            # Future feature
    "team_mode": False,                 # Future feature
}

# Monitoring Configuration
MONITORING = {
    "metrics_enabled": True,
    "error_tracking": True,
    "performance_monitoring": True,
    "voice_streaming_metrics": True,    # NEW: Voice streaming monitoring
    "websocket_metrics": True,          # NEW: WebSocket connection monitoring
    "system_metrics": True,
    "custom_metrics": {
        "interview_sessions_total": True,
        "voice_streaming_usage": True,  # NEW
        "websocket_connections": True,  # NEW
        "evaluation_accuracy": True,
        "question_generation_time": True,
        "response_latency": True,
        "voice_transcription_accuracy": True  # NEW
    },
    "alert_thresholds": {
        "error_rate": 0.05,
        "response_time_ms": 5000,
        "memory_usage": 0.8,
        "cpu_usage": 0.8,
        "voice_streaming_failures": 0.1,   # NEW
        "websocket_disconnections": 0.15,  # NEW
        "adk_api_failures": 0.05
    }
}

# Deployment Configuration
DEPLOYMENT = {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "voice_server_port": int(os.getenv("VOICE_SERVER_PORT", "8002")),
    "streamlit_port": int(os.getenv("STREAMLIT_PORT", "8501")),
    "host": os.getenv("HOST", "localhost"),
    "workers": int(os.getenv("WORKERS", "1")),
    "memory_limit": os.getenv("MEMORY_LIMIT", "2G"),
    "cpu_limit": os.getenv("CPU_LIMIT", "1"),
    "health_check_enabled": True,
    "voice_streaming_enabled": True,
    "websocket_support": True,
    "containerization": {
        "docker_enabled": True,
        "docker_image": f"{APP_NAME.lower().replace(' ', '-')}:{VERSION}",
        "auto_scaling": True,
        "resource_limits": {
            "memory": "2Gi",
            "cpu": "1000m",
            "storage": "5Gi"
        }
    }
}

# Logging Configuration - Updated for Voice Streaming
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(BASE_DIR / "logs" / "app.log"),
            "maxBytes": 10485760,
            "backupCount": 5
        },
        "voice_streaming": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(BASE_DIR / "logs" / "voice_streaming.log"),
            "maxBytes": 5242880,
            "backupCount": 3
        },
        "websocket": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", 
            "formatter": "detailed",
            "filename": str(BASE_DIR / "logs" / "websocket.log"),
            "maxBytes": 5242880,
            "backupCount": 3
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "agents": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "voice_streaming": {
            "handlers": ["console", "voice_streaming"],
            "level": "DEBUG",
            "propagate": False
        },
        "websocket": {
            "handlers": ["console", "websocket"],
            "level": "DEBUG",
            "propagate": False
        },
        "adk": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "fastapi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "streamlit": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        }
    }
}

# Initialize logging
if not (BASE_DIR / "logs").exists():
    (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info(f"Configuration loaded for {APP_NAME} v{VERSION}")
logger.info(f"ADK Voice Streaming: {VOICE_STREAMING_CONFIG['enabled']}")
logger.info(f"Modern UI: {UI_CONFIG['theme']}")
logger.info(f"Features: ADK Voice, Modern UI, Clean Evaluations, WebSocket Streaming")