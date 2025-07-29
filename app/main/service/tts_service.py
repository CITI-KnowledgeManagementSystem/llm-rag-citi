import requests
import os
import re
from uuid import uuid4
from typing import Optional, Dict, Any, List, Tuple
from ..response import HTTPRequestException
from ..constant.tts import (
    TTS_SERVER_URL,
    DEFAULT_VOICE_MODE,
    DEFAULT_PREDEFINED_VOICE_ID,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_SPLIT_TEXT,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TEMPERATURE,
    DEFAULT_EXAGGERATION,
    DEFAULT_CFG_WEIGHT,
    DEFAULT_SPEED_FACTOR,
    DEFAULT_LANGUAGE,
    AUDIO_DIR,
    OPENAI_MODEL,
    OPENAI_VOICE,
    OPENAI_RESPONSE_FORMAT,
    OPENAI_SPEED,
    PODCAST_SPEAKERS,
    SILENCE_DURATION,
    AUDIO_FADE_DURATION
)


def generate_speech(
    text: str,
    voice_mode: str = DEFAULT_VOICE_MODE,
    predefined_voice_id: str = DEFAULT_PREDEFINED_VOICE_ID,
    reference_audio_filename: Optional[str] = None,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    split_text: bool = DEFAULT_SPLIT_TEXT,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    temperature: float = DEFAULT_TEMPERATURE,
    exaggeration: float = DEFAULT_EXAGGERATION,
    cfg_weight: float = DEFAULT_CFG_WEIGHT,
    seed: Optional[int] = None,
    speed_factor: float = DEFAULT_SPEED_FACTOR,
    language: str = DEFAULT_LANGUAGE
) -> str:
    """
    Generate speech from text using the TTS server.
    Returns the path to the saved audio file.
    """
    if not text:
        raise HTTPRequestException(message="Text is required for TTS generation", status_code=400)
    
    if not TTS_SERVER_URL:
        raise HTTPRequestException(message="TTS server URL not configured", status_code=500)
    
    # Prepare request payload
    payload = {
        "text": text,
        "voice_mode": voice_mode,
        "predefined_voice_id": predefined_voice_id,
        "output_format": output_format,
        "split_text": split_text,
        "chunk_size": chunk_size,
        "temperature": temperature,
        "exaggeration": exaggeration,
        "cfg_weight": cfg_weight,
        "speed_factor": speed_factor,
        "language": language
    }
    
    # Add reference audio if provided
    if reference_audio_filename:
        payload["reference_audio_filename"] = reference_audio_filename
    
    # Add seed if provided
    if seed is not None:
        payload["seed"] = seed
    
    try:
        # Make request to TTS server
        response = requests.post(
            f"{TTS_SERVER_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Save audio file
            audio_filename = f"tts_{uuid4().hex}.{output_format}"
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            
            # Create audio directory if it doesn't exist
            os.makedirs(AUDIO_DIR, exist_ok=True)
            
            # Save audio content
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return audio_path
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            raise HTTPRequestException(
                message=f"TTS generation failed: {error_detail}",
                status_code=response.status_code
            )
    
    except requests.exceptions.RequestException as e:
        raise HTTPRequestException(
            message=f"Failed to connect to TTS server: {str(e)}",
            status_code=500
        )


def generate_speech_openai_compatible(
    text: str,
    model: str = OPENAI_MODEL,
    voice: str = OPENAI_VOICE,
    response_format: str = OPENAI_RESPONSE_FORMAT,
    speed: float = OPENAI_SPEED,
    seed: Optional[int] = None
) -> str:
    """
    Generate speech using OpenAI-compatible endpoint.
    Returns the path to the saved audio file.
    """
    if not text:
        raise HTTPRequestException(message="Text is required for TTS generation", status_code=400)
    
    if not TTS_SERVER_URL:
        raise HTTPRequestException(message="TTS server URL not configured", status_code=500)
    
    # Prepare request payload
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
        "speed": speed
    }
    
    # Add seed if provided
    if seed is not None:
        payload["seed"] = seed
    
    try:
        # Make request to OpenAI-compatible endpoint
        response = requests.post(
            f"{TTS_SERVER_URL}/v1/audio/speech",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            # Save audio file
            audio_filename = f"tts_openai_{uuid4().hex}.{response_format}"
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            
            # Create audio directory if it doesn't exist
            os.makedirs(AUDIO_DIR, exist_ok=True)
            
            # Save audio content
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return audio_path
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            raise HTTPRequestException(
                message=f"TTS generation failed: {error_detail}",
                status_code=response.status_code
            )
    
    except requests.exceptions.RequestException as e:
        raise HTTPRequestException(
            message=f"Failed to connect to TTS server: {str(e)}",
            status_code=500
        )


def parse_podcast_script(script_text: str) -> List[Tuple[str, str]]:
    """
    Parse podcast script and extract speaker segments.
    Returns list of tuples: (speaker, text)
    """
    segments = []
    
    # Split by lines and process each line
    lines = script_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match patterns like "HOST_A: text" or "HOST_B: text"
        match = re.match(r'^(HOST_[AB]):\s*(.+)$', line, re.IGNORECASE)
        if match:
            speaker = match.group(1).upper()
            text = match.group(2).strip()
            segments.append((speaker, text))
    
    return segments


def concatenate_audio_files(audio_files: List[str], output_filename: str) -> str:
    """
    Concatenate multiple audio files with silence between them.
    Returns the path to the concatenated audio file.
    
    Note: This is a placeholder implementation. In production, you would use
    a library like pydub to handle audio concatenation properly.
    """
    try:
        # For now, we'll use a simple approach
        # In production, you should use pydub or similar library
        import subprocess
        
        output_path = os.path.join(AUDIO_DIR, output_filename)
        
        # Create a temporary file list for ffmpeg
        file_list_path = os.path.join(AUDIO_DIR, f"temp_filelist_{uuid4().hex}.txt")
        
        with open(file_list_path, 'w') as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
        
        # Use ffmpeg to concatenate
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', file_list_path,
            '-c', 'copy', output_path, '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        os.remove(file_list_path)
        
        if result.returncode != 0:
            raise HTTPRequestException(
                message=f"Audio concatenation failed: {result.stderr}",
                status_code=500
            )
        
        return output_path
        
    except FileNotFoundError:
        # ffmpeg not available, return first audio file as fallback
        if audio_files:
            return audio_files[0]
        raise HTTPRequestException(
            message="Audio concatenation failed: ffmpeg not available",
            status_code=500
        )
    except Exception as e:
        raise HTTPRequestException(
            message=f"Audio concatenation failed: {str(e)}",
            status_code=500
        )


async def generate_conversational_podcast(
    question: str,
    user_id: str,
    speaker_voices: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate a conversational podcast with two speakers using RAG + TTS.
    Returns information about the generated podcast.
    """
    from .llm_service import question_answer
    from ...main import generation_llm
    from ..constant.llm import PODCAST_SCRIPT_TEMPLATE
    
    if not question or not user_id:
        raise HTTPRequestException(message="Question and user_id are required", status_code=400)
    
    try:
        # Step 1: Generate content using existing RAG system
        rag_response = await question_answer(
            question=question,
            user_id=user_id,
            conversations_history=[],
            hyde=True,
            reranking=True
        )
        
        content = rag_response.get('answer', '')
        if not content:
            raise HTTPRequestException(message="No content generated from RAG system", status_code=500)
        
        # Step 2: Generate conversational script
        script_prompt = PODCAST_SCRIPT_TEMPLATE.format(
            content=content,
            question=question
        )
        
        script_response = generation_llm.complete(script_prompt)
        script_text = script_response.text
        
        # Step 3: Parse script into speaker segments
        segments = parse_podcast_script(script_text)
        
        if not segments:
            raise HTTPRequestException(message="Failed to parse podcast script", status_code=500)
        
        # Step 4: Use provided speaker voices or defaults
        if speaker_voices is None:
            speaker_voices = PODCAST_SPEAKERS
        
        # Step 5: Generate audio for each segment
        audio_files = []
        segment_info = []
        
        for i, (speaker, text) in enumerate(segments):
            speaker_config = speaker_voices.get(speaker, PODCAST_SPEAKERS.get(speaker, PODCAST_SPEAKERS['HOST_A']))
            
            # Generate audio for this segment
            audio_path = generate_speech(
                text=text,
                voice_mode=speaker_config.get('voice_mode', DEFAULT_VOICE_MODE),
                predefined_voice_id=speaker_config.get('predefined_voice_id', DEFAULT_PREDEFINED_VOICE_ID),
                temperature=speaker_config.get('temperature', DEFAULT_TEMPERATURE),
                exaggeration=speaker_config.get('exaggeration', DEFAULT_EXAGGERATION),
                speed_factor=speaker_config.get('speed_factor', DEFAULT_SPEED_FACTOR),
                output_format='wav'
            )
            
            audio_files.append(audio_path)
            segment_info.append({
                'speaker': speaker,
                'text': text,
                'audio_path': audio_path,
                'segment_index': i
            })
        
        # Step 6: Concatenate all audio files
        final_audio_filename = f"podcast_{uuid4().hex}.wav"
        final_audio_path = concatenate_audio_files(audio_files, final_audio_filename)
        
        return {
            "question": question,
            "script": script_text,
            "segments": segment_info,
            "final_audio_path": final_audio_path,
            "user_id": user_id,
            "sources": rag_response.get('sources', []),
            "segment_count": len(segments)
        }
        
    except Exception as e:
        raise HTTPRequestException(
            message=f"Conversational podcast generation failed: {str(e)}",
            status_code=500
        )


async def generate_podcast_from_rag(
    question: str,
    user_id: str,
    voice_options: Optional[Dict[str, Any]] = None,
    use_openai_compatible: bool = False
) -> Dict[str, Any]:
    """
    Generate a podcast by combining RAG content generation with TTS.
    Returns information about the generated podcast.
    """
    from .llm_service import question_answer
    
    if not question or not user_id:
        raise HTTPRequestException(message="Question and user_id are required", status_code=400)
    
    try:
        # Generate content using existing RAG system
        rag_response = await question_answer(
            question=question,
            user_id=user_id,
            conversations_history=[],
            hyde=True,  # Use HyDE for better content generation
            reranking=True  # Use reranking for better quality
        )
        
        # Extract text content from RAG response
        podcast_text = rag_response.get('answer', '')
        
        if not podcast_text:
            raise HTTPRequestException(message="No content generated from RAG system", status_code=500)
        
        # Set default voice options if not provided
        if voice_options is None:
            voice_options = {}
        
        # Generate speech
        if use_openai_compatible:
            audio_path = generate_speech_openai_compatible(
                text=podcast_text,
                **voice_options
            )
        else:
            audio_path = generate_speech(
                text=podcast_text,
                **voice_options
            )
        
        return {
            "question": question,
            "content": podcast_text,
            "audio_path": audio_path,
            "user_id": user_id,
            "sources": rag_response.get('sources', [])
        }
        
    except Exception as e:
        raise HTTPRequestException(
            message=f"Podcast generation failed: {str(e)}",
            status_code=500
        )