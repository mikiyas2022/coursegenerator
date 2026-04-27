FROM python:3.11-slim

# System deps: ffmpeg, LaTeX (basic), fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-noto \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    pkg-config python3-dev \
    build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python deps
COPY agent_core/requirements.txt ./agent_core_requirements.txt
COPY video_compiler/requirements.txt ./compiler_requirements.txt

RUN pip install --no-cache-dir \
    manim==0.20.1 \
    manim-voiceover \
    langchain langchain-openai langchain-community langgraph \
    langchain-huggingface faiss-cpu \
    fastapi uvicorn[standard] pydantic \
    deep-translator requests pydub \
    python-dotenv sympy \
    && pip install --no-cache-dir -r agent_core_requirements.txt || true \
    && pip install --no-cache-dir -r compiler_requirements.txt || true

# Copy source
COPY . .

# Create required directories
RUN mkdir -p logs Local_Video_Output

# Environment defaults
ENV OLLAMA_BASE_URL=http://ollama:11434/v1
ENV TTS_SERVER_URL=http://tts:8102
ENV ORCHESTRATOR_PORT=8205
ENV AUTO_APPROVE=true
ENV HF_HOME=/tmp/huggingface_cache

EXPOSE 8205

CMD ["python", "-m", "uvicorn", "agent_core.orchestrator:app", \
     "--host", "0.0.0.0", "--port", "8205", "--log-level", "info"]
