import os
from pydub import AudioSegment
from pydub.effects import normalize
import whisper
import numpy as np
from scipy.signal import butter, filtfilt
from deep_translator import GoogleTranslator

def get_language_name(language_code):
    language_dict = {
        'en': 'Inglês',
        'pt': 'Português',
        'es': 'Espanhol',
        'fr': 'Francês',
        'de': 'Alemão',
        'it': 'Italiano',
        'ja': 'Japonês',
        'ko': 'Coreano',
        'zh': 'Chinês',
        'ru': 'Russo',
        'ar': 'Árabe',
        'hi': 'Hindi',
        'tr': 'Turco',
        'pl': 'Polonês',
        'nl': 'Holandês',
        'vi': 'Vietnamita',
        'th': 'Tailandês',
        'id': 'Indonésio',
        'sv': 'Sueco',
        'da': 'Dinamarquês',
        'fi': 'Finlandês',
        'no': 'Norueguês',
        'cs': 'Tcheco',
        'hu': 'Húngaro',
        'el': 'Grego',
        'he': 'Hebraico',
        'ro': 'Romeno',
        'bn': 'Bengali',
        'uk': 'Ucraniano',
        'fa': 'Persa',
    }
    return language_dict.get(language_code, f'Idioma desconhecido (código: {language_code})')

def apply_noise_reduction(audio_segment):
    """Aplica redução de ruído usando filtro passa-banda."""
    samples = np.array(audio_segment.get_array_of_samples())
    sample_rate = audio_segment.frame_rate

    nyquist = sample_rate / 2
    low_cutoff = 100 / nyquist
    high_cutoff = 3000 / nyquist
    b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
    filtered_samples = filtfilt(b, a, samples)

    filtered_audio = audio_segment._spawn(filtered_samples.astype(np.int16))
    return filtered_audio

def enhance_audio(audio_segment):
    """Apply various audio enhancement techniques."""
    audio_segment = normalize(audio_segment)
    audio_segment = apply_noise_reduction(audio_segment)
    audio_segment = audio_segment + 3  # Aumenta 3dB
    return audio_segment

def prepare_audio_for_transcription(video_path):
    """Prepare the audio for transcription with better quality."""
    audio = AudioSegment.from_file(video_path, format="mp4")

    if audio.channels > 1:
        audio = audio.set_channels(1)

    audio = audio.set_frame_rate(16000)
    enhanced_audio = enhance_audio(audio)

    temp_path = "temp_processed_audio.wav"
    enhanced_audio.export(temp_path, format="wav")

    return temp_path

def print_audio_info_and_transcribe(video_path):
    video_path = os.path.abspath(video_path)

    if not os.path.exists(video_path):
        print(f"O arquivo {video_path} não foi encontrado.")
        return []

    processed_audio_path = None
    try:
        print("Iniciando processamento do áudio...")

        processed_audio_path = prepare_audio_for_transcription(video_path)
        audio = AudioSegment.from_file(video_path, format="mp4")

        print(f"\nInformações do áudio original:")
        print(f"Duração do áudio: {len(audio) / 1000:.2f} segundos")
        print(f"Canais: {audio.channels}")
        print(f"Taxa de amostragem: {audio.frame_rate} Hz")
        print(f"Bits por amostra: {audio.sample_width * 8}")

        print("\nPrimeiros 10 valores de amplitude:")
        samples = audio.get_array_of_samples()[:10]
        for i, sample in enumerate(samples):
            print(f"Amostra {i}: {sample}")

        print("\nIniciando transcrição do áudio aprimorado...")

        model = whisper.load_model("base")

        transcription_options = {
            "fp16": False,
            "language": None,
            "task": "transcribe",
            "beam_size": 5,
            "best_of": 5,
            "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "word_timestamps": True
        }

        result = model.transcribe(processed_audio_path, **transcription_options)

        detected_language = result.get("language", "desconhecido")

        print(f"\nIdioma detectado: {get_language_name(detected_language)}")

        transcricao = []
        for segment in result.get('segments', []):
            for word_info in segment.get('words', []):
                palavra = word_info['word'].strip()
                tempo = word_info['start']
                transcricao.append((palavra, tempo))

        print("\nTranscrição completa:")
        transcription_text = result["text"]
        print(transcription_text)


        if detected_language != 'pt':
            print("\nTradução para português:")
            try:
                translator = GoogleTranslator(source=detected_language, target='pt')
                translated_text = translator.translate(transcription_text)
                print(translated_text)
            except Exception as e:
                print(f"Erro na tradução: {str(e)}")

        if "language_probability" in result:
            confidence = result["language_probability"] * 100
            print(f"\nConfiança na detecção do idioma: {confidence:.2f}%")

        os.remove(processed_audio_path)

        return transcricao

    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {str(e)}")
        if processed_audio_path and os.path.exists(processed_audio_path):
            os.remove(processed_audio_path)
        return []

# Exemplo de uso
if __name__ == "__main__":
    video_path = r"C:\Users\welli\Downloads\video 1.mp4"
    transcricao = print_audio_info_and_transcribe(video_path)
