# 🎯 AI-Powered Interview Preparation Assistant

> **Built with Google's Agent Development Kit (ADK)** 

An intelligent interview preparation system that analyzes both **what you say** (content) and **how you say it** (delivery) using multi-agent AI architecture.

## ✨ Features

- 🎤 **Parallel Voice Analysis**: Simultaneous content and speech delivery evaluation
- 🎯 **Industry-Specific Coaching**: Tailored feedback for different industries
- 📊 **Comprehensive Scoring**: Separate scores for content quality and speaking delivery
- 🏢 **Job Description Analysis**: Auto-generates questions based on specific roles
- 📈 **Progress Tracking**: Monitor improvement across multiple competencies
- 🤖 **Multi-Agent Architecture**: Specialized AI agents for different aspects of interview prep

## 🏗️ Architecture

Built using Google's Agent Development Kit with specialized agents:

- **🎙️ Transcription Agent**: Industry-aware audio transcription
- **🎯 Speech Coach Agent**: Delivery and communication style analysis
- **📝 Content Evaluator**: STAR method and competency assessment
- **🔄 Interview Manager**: Orchestrates the entire workflow
- **📋 Job Analyzer**: Extracts requirements from job descriptions

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google AI API key ([Get yours here](https://aistudio.google.com/app/apikey))
- UV package manager (recommended) - [Install UV](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/DreamAIIO/adk-interview-prep.git
cd adk-interview-prep
```

2. **Set up environment**:
```bash
# Create virtual environment with UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

3. **Configure environment**:
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Google AI API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

4. **Run the application**:
```bash
# Start the voice server (Terminal 1)
python enhanced_voice_server.py

# In a new terminal, start the Streamlit app (Terminal 2)
streamlit run enhanced_streamlit_ui.py
```

5. **Open your browser** to `http://localhost:8501`

## 🎯 How It Works

1. **📋 Paste a job description** - The system analyzes industry, competencies, and requirements
2. **❓ Generate practice questions** - AI creates role-specific interview questions  
3. **🎤 Record or type your answer** - Use voice for comprehensive analysis including delivery coaching
4. **📊 Get detailed feedback** - Receive separate scores for content quality and speaking delivery
5. **📈 Track your progress** - Monitor improvement across all competencies over time

## 🎤 Voice Analysis Deep Dive

### What Makes This Special

Unlike traditional interview prep tools that only analyze text, this system provides **parallel processing**:

- **Content Analysis**: STAR method compliance, competency demonstration, industry relevance
- **Delivery Analysis**: Speaking pace, clarity, confidence, professional tone, filler words
- **Synthesis**: Combined insights that neither analysis could provide alone

### Industry-Specific Coaching

The Speech Coach Agent understands different communication styles:

- **Technology**: Clear technical explanations, collaborative tone
- **Finance**: Precise and analytical, trustworthy delivery
- **Consulting**: Persuasive and strategic, confident advisory style
- **Healthcare**: Compassionate authority, clear patient communication

## 🛠️ Technology Stack

- **🤖 Google ADK**: Multi-agent orchestration framework
- **🎙️ Gemini 2.0**: Multimodal AI for voice and text processing
- **🚀 FastAPI**: Backend API server with async processing
- **🎨 Streamlit**: Interactive web interface
- **🐍 Python 3.9+**: Core application language
- **📦 UV**: Fast Python package manager

## 🏗️ Development Story

This project evolved through three major iterations:

1. **Iteration 1**: Hybrid mess (mixing ADK with Streamlit) - Failed
2. **Iteration 2**: Proper separation + Transcription Agent discovery
3. **Iteration 3**: Speech Coach Agent breakthrough + Parallel processing

Read the full technical deep dive: [Building Multi-Agent AI with Google's ADK](link-to-your-blog-post)

## 📁 Project Structure

```
adk-interview-prep/
├── agents/                          # ADK agent implementations
│   ├── competency_agent.py         # Specialized competency evaluators
│   ├── interview_manager.py        # Main orchestration agent
│   ├── speech_coach_agent.py       # Voice delivery analysis
│   └── enhanced_voice_workflow_agent.py  # Parallel processing coordinator
├── core/                           # Core utilities
│   └── job_analyzer.py            # Job description analysis
├── enhanced_streamlit_ui.py        # Main Streamlit interface
├── enhanced_voice_server.py        # FastAPI voice processing server
├── enhanced_streamlit_voice_client.py  # Voice client integration
├── config.py                       # Configuration and settings
├── audio_handler.py               # Audio processing utilities
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## 🎯 Core Competencies Analyzed

- **Problem Solving**: Analytical approach, solution methodology
- **Technical Expertise**: Implementation skills, best practices
- **Project Management**: Planning, organization, stakeholder management
- **Analytical Thinking**: Data interpretation, logical reasoning
- **Attention to Detail**: Quality assurance, error prevention
- **Written Communication**: Clarity, structure, audience awareness
- **Leadership**: Team management, influence, strategic thinking
- **Teamwork**: Collaboration, communication, team contribution

## 🚀 Advanced Features

### Parallel Content + Delivery Analysis
```python
# Simultaneous processing for comprehensive feedback
content_task = analyze_content(transcription)
delivery_task = analyze_speech_delivery(audio)
synthesis = combine_insights(content_result, delivery_result)
```

### Model Flexibility
```python
# Use different LLMs for different agents
CONTENT_MODEL = "claude-3-5-sonnet"     # Superior reasoning
AUDIO_MODEL = "gemini-2.0-flash"        # Multimodal capabilities
TRANSCRIPTION_MODEL = "whisper-api"     # Specialized transcription
```

### Industry Context Awareness
```python
# Adapts coaching based on industry expectations
if industry == "technology":
    coaching_style = "collaborative_technical"
elif industry == "finance":
    coaching_style = "precise_analytical"
```


### Development Setup

```bash
# Install development dependencies
uv pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
isort .
```

## 📊 Performance Metrics

- **Content Analysis**: ~2-3 seconds
- **Voice Analysis**: ~3-5 seconds  
- **Parallel Processing**: ~3-5 seconds total (vs ~8-10 sequential)
- **Question Generation**: ~1-2 seconds
- **Job Analysis**: ~2-3 seconds

## 🐛 Troubleshooting

### Common Issues

**Voice server won't start**:
```bash
# Check if port 8002 is available
lsof -i :8002
# Kill any existing process and restart
```

**Audio recording not working**:
- Ensure microphone permissions are granted
- Check browser compatibility (Chrome/Firefox recommended)
- Verify audio input device in system settings

**API key errors**:
- Verify your Google AI API key is valid
- Check .env file formatting (no quotes around the key)
- Ensure you have quota remaining

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=True
python enhanced_voice_server.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **Google's Agent Development Kit team** for the incredible framework
- **The open-source community** for inspiration and tools
- **Beta testers** who provided valuable feedback on the voice analysis features

## 🔗 Links

- [Google Agent Development Kit Documentation](https://google.github.io/adk-docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [UV Package Manager](https://docs.astral.sh/uv/)

---

**⭐ If this project helped you ace your interviews or learn about multi-agent AI, please star the repository!**

**💬 Questions?** Open an issue or start a discussion. We love talking about ADK and multi-agent systems!

**🚀 Want to build something similar?** Check out the technical deep dive blog post for the complete development journey.
