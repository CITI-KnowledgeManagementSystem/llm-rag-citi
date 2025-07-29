from flask import request, send_file
from ..service.tts_service import generate_speech, generate_speech_openai_compatible, generate_podcast_from_rag, generate_conversational_podcast
from ..response import HTTPRequestException, HTTPRequestSuccess
from ...main import semaphore
import json
import os


async def generate_tts():
    """Generate TTS audio from text using custom endpoint"""
    semaphore.acquire()
    
    try:
        body = request.get_json()
        
        # Extract required parameters
        text = body.get('text')
        if not text:
            raise HTTPRequestException(message="Text is required", status_code=400)
        
        # Extract optional parameters
        voice_mode = body.get('voice_mode', 'predefined')
        predefined_voice_id = body.get('predefined_voice_id', 'default')
        reference_audio_filename = body.get('reference_audio_filename')
        output_format = body.get('output_format', 'wav')
        split_text = body.get('split_text', True)
        chunk_size = body.get('chunk_size', 120)
        temperature = body.get('temperature', 0.7)
        exaggeration = body.get('exaggeration', 0.0)
        cfg_weight = body.get('cfg_weight', 1.0)
        seed = body.get('seed')
        speed_factor = body.get('speed_factor', 1.0)
        language = body.get('language', 'en')
        
        # Generate speech
        audio_path = generate_speech(
            text=text,
            voice_mode=voice_mode,
            predefined_voice_id=predefined_voice_id,
            reference_audio_filename=reference_audio_filename,
            output_format=output_format,
            split_text=split_text,
            chunk_size=chunk_size,
            temperature=temperature,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            seed=seed,
            speed_factor=speed_factor,
            language=language
        )
        
        return HTTPRequestSuccess(
            message="TTS generation successful",
            status_code=200,
            payload={"audio_path": audio_path}
        ).to_response()
        
    except HTTPRequestException as e:
        return e.to_response()
    except Exception as e:
        return HTTPRequestException(
            message=f"TTS generation failed: {str(e)}",
            status_code=500
        ).to_response()
    finally:
        semaphore.release()


async def generate_tts_openai():
    """Generate TTS audio using OpenAI-compatible endpoint"""
    semaphore.acquire()
    
    try:
        body = request.get_json()
        
        # Extract required parameters
        text = body.get('input')
        if not text:
            raise HTTPRequestException(message="Input text is required", status_code=400)
        
        # Extract optional parameters
        model = body.get('model', 'tts-1')
        voice = body.get('voice', 'alloy')
        response_format = body.get('response_format', 'wav')
        speed = body.get('speed', 1.0)
        seed = body.get('seed')
        
        # Generate speech
        audio_path = generate_speech_openai_compatible(
            text=text,
            model=model,
            voice=voice,
            response_format=response_format,
            speed=speed,
            seed=seed
        )
        
        return HTTPRequestSuccess(
            message="TTS generation successful",
            status_code=200,
            payload={"audio_path": audio_path}
        ).to_response()
        
    except HTTPRequestException as e:
        return e.to_response()
    except Exception as e:
        return HTTPRequestException(
            message=f"TTS generation failed: {str(e)}",
            status_code=500
        ).to_response()
    finally:
        semaphore.release()


async def generate_podcast():
    """Generate podcast using RAG + TTS"""
    semaphore.acquire()
    
    try:
        body = request.get_json()
        
        # Extract required parameters
        question = body.get('question')
        user_id = body.get('user_id')
        
        if not question or not user_id:
            raise HTTPRequestException(message="Question and user_id are required", status_code=400)
        
        # Extract optional parameters
        voice_options = body.get('voice_options', {})
        use_openai_compatible = body.get('use_openai_compatible', False)
        
        # Generate podcast
        podcast_result = await generate_podcast_from_rag(
            question=question,
            user_id=user_id,
            voice_options=voice_options,
            use_openai_compatible=use_openai_compatible
        )
        
        return HTTPRequestSuccess(
            message="Podcast generation successful",
            status_code=200,
            payload=podcast_result
        ).to_response()
        
    except HTTPRequestException as e:
        return e.to_response()
    except Exception as e:
        return HTTPRequestException(
            message=f"Podcast generation failed: {str(e)}",
            status_code=500
        ).to_response()
    finally:
        semaphore.release()


async def generate_conversational_podcast_endpoint():
    """Generate conversational podcast with two speakers (NotebookLM style)"""
    semaphore.acquire()
    
    try:
        body = request.get_json()
        
        # Extract required parameters
        question = body.get('question')
        user_id = body.get('user_id')
        
        if not question or not user_id:
            raise HTTPRequestException(message="Question and user_id are required", status_code=400)
        
        # Extract optional parameters
        speaker_voices = body.get('speaker_voices')  # Custom voice configurations
        
        # Generate conversational podcast
        podcast_result = await generate_conversational_podcast(
            question=question,
            user_id=user_id,
            speaker_voices=speaker_voices
        )
        
        return HTTPRequestSuccess(
            message="Conversational podcast generation successful",
            status_code=200,
            payload=podcast_result
        ).to_response()
        
    except HTTPRequestException as e:
        return e.to_response()
    except Exception as e:
        return HTTPRequestException(
            message=f"Conversational podcast generation failed: {str(e)}",
            status_code=500
        ).to_response()
    finally:
        semaphore.release()


def download_audio():
    """Download audio file by filename"""
    try:
        filename = request.args.get('filename')
        if not filename:
            raise HTTPRequestException(message="Filename is required", status_code=400)
        
        from ..constant.tts import AUDIO_DIR
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            raise HTTPRequestException(message="Audio file not found", status_code=404)
        
        return send_file(audio_path, as_attachment=True)
        
    except HTTPRequestException as e:
        return e.to_response()
    except Exception as e:
        return HTTPRequestException(
            message=f"File download failed: {str(e)}",
            status_code=500
        ).to_response()