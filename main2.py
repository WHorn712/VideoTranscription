import os
import numpy as np
import whisper
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize
from scipy import signal
from deep_translator import GoogleTranslator


def get_language_name(language_code):
    """Returns the language of the transcription passed as a parameter."""
    language_dict = {
        'en': 'Inglês', 'pt': 'Português', 'es': 'Espanhol', 'fr': 'Francês',
        'de': 'Alemão', 'it': 'Italiano', 'ja': 'Japonês', 'ko': 'Coreano',
        'zh': 'Chinês', 'ru': 'Russo', 'ar': 'Árabe', 'hi': 'Hindi',
        'tr': 'Turco', 'pl': 'Polonês', 'nl': 'Holandês', 'vi': 'Vietnamita',
        'th': 'Tailandês', 'id': 'Indonésio', 'sv': 'Sueco', 'da': 'Dinamarquês',
        'fi': 'Finlandês', 'no': 'Norueguês', 'cs': 'Tcheco', 'hu': 'Húngaro',
        'el': 'Grego', 'he': 'Hebraico', 'ro': 'Romeno', 'bn': 'Bengali',
        'uk': 'Ucraniano', 'fa': 'Persa',
    }
    return language_dict.get(language_code, f'Idioma desconhecido (código: {language_code})')


def advanced_noise_reduction(audio_segment):
    """Advanced noise reduction using noisereduce."""
    try:
        # Converte o AudioSegment para numpy array
        samples = np.array(audio_segment.get_array_of_samples())
        sample_rate = audio_segment.frame_rate

        # Redução de ruído usando noisereduce
        reduced_noise = nr.reduce_noise(
            y=samples,
            sr=sample_rate,
            prop_decrease=0.7,  # Ajuste a redução de ruído
            n_std_thresh_stationary=1.5,
            stationary=True
        )

        # Converte de volta para AudioSegment
        denoised_audio = audio_segment._spawn(reduced_noise.astype(np.int16))

        return denoised_audio
    except Exception as e:
        print(f"Erro na redução de ruído: {e}")
        return audio_segment


def adaptive_equalization(audio_segment):
    """Adaptive audio equalization with error handling."""
    try:
        # Converte o AudioSegment para numpy array
        samples = np.array(audio_segment.get_array_of_samples())
        sample_rate = audio_segment.frame_rate

        # Normaliza as frequências de corte
        nyquist = sample_rate / 2
        low_freq = 100 / nyquist
        high_freq = 3000 / nyquist

        # Verifica se as frequências estão dentro do intervalo válido
        if 0 < low_freq < 1 and 0 < high_freq < 1:
            # Projeto do filtro
            sos = signal.butter(10, [low_freq, high_freq], btype='band', output='sos')

            # Aplicação do filtro
            equalized = signal.sosfilt(sos, samples)

            # Converte de volta para AudioSegment
            equalized_audio = audio_segment._spawn(equalized.astype(np.int16))
            return equalized_audio
        else:
            print("Frequências de corte inválidas. Pulando equalização.")
            return audio_segment

    except Exception as e:
        print(f"Erro na equalização: {e}")
        return audio_segment


def advanced_audio_processing(audio_segment):
    """Advanced audio processing with error handling."""
    try:
        # Normalização
        normalized = normalize(audio_segment)

        # Redução de ruído avançada
        denoised = advanced_noise_reduction(normalized)

        # Equalização adaptativa
        equalized = adaptive_equalization(denoised)

        # Ajuste de ganho dinâmico
        dynamic_audio = equalized + 3  # Aumento de 3dB

        return dynamic_audio

    except Exception as e:
        print(f"Erro no processamento de áudio: {e}")
        return audio_segment


def prepare_audio_for_transcription(video_path):
    """Prepare audio for transcription with advanced processing."""
    try:
        # Carrega o áudio
        audio = AudioSegment.from_file(video_path, format="mp4")

        # Converte para mono se necessário
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Ajusta taxa de amostragem
        audio = audio.set_frame_rate(16000)

        # Processamento avançado
        enhanced_audio = advanced_audio_processing(audio)

        # Exporta áudio processado
        temp_path = "temp_processed_audio.wav"
        enhanced_audio.export(temp_path, format="wav")

        return temp_path

    except Exception as e:
        print(f"Erro na preparação do áudio: {e}")
        return None


def print_audio_info_and_transcribe(video_path):
    """Main function."""
    video_path = os.path.abspath(video_path)

    if not os.path.exists(video_path):
        print(f"O arquivo {video_path} não foi encontrado.")
        return []

    processed_audio_path = None
    try:
        print("Iniciando processamento do áudio...")

        # Prepara o áudio
        processed_audio_path = prepare_audio_for_transcription(video_path)


        if processed_audio_path is None:
            print("Falha na preparação do áudio.")
            return []

        audio = AudioSegment.from_file(video_path, format="mp4")

        # Imprime informações do áudio original
        print(f"\nInformações do áudio original:")
        print(f"Duração do áudio: {len(audio) / 1000:.2f} segundos")
        print(f"Canais: {audio.channels}")
        print(f"Taxa de amostragem: {audio.frame_rate} Hz")
        print(f"Bits por amostra: {audio.sample_width * 8}")

        # Imprime primeiras amostras
        print("\nPrimeiros 10 valores de amplitude:")
        samples = audio.get_array_of_samples()[:10]
        for i, sample in enumerate(samples):
            print(f"Amostra {i}: {sample}")

        print("\nIniciando transcrição do áudio aprimorado...")

        model = whisper.load_model("base")

        # Opções de transcrição avançadas (removido log_prob_threshold)
        transcription_options = {
            "fp16": False,
            "language": None,
            "task": "transcribe",
            "beam_size": 5,
            "best_of": 5,
            "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "word_timestamps": True,
            "condition_on_previous_text": True,
            "compression_ratio_threshold": 2.4,
            "no_speech_threshold": 0.6
        }

        # Realiza transcrição
        result = model.transcribe(processed_audio_path, **transcription_options)

        # Detecta idioma
        detected_language = result.get("language", "desconhecido")
        print(f"\nIdioma detectado: {get_language_name(detected_language)}")

        # Processa transcrição por palavras
        transcricao = []
        for segment in result.get('segments', []):
            for word_info in segment.get('words', []):
                palavra = word_info['word'].strip()
                tempo = word_info['start']
                transcricao.append((palavra, tempo))

        # Imprime transcrição
        print("\nTranscrição completa:")
        transcription_text = result["text"]
        print(transcription_text)

        # Tradução para português se não for português
        if detected_language != 'pt':
            print("\nTradução para português:")
            try:
                translator = GoogleTranslator(source=detected_language, target='pt')
                translated_text = translator.translate(transcription_text)
                print(translated_text)
            except Exception as e:
                print(f"Erro na tradução: {str(e)}")

        # Imprime confiança na detecção de idioma
        if "language_probability" in result:
            confidence = result["language_probability"] * 100
            print(f"\nConfiança na detecção do idioma: {confidence:.2f}%")

        # Remove arquivo temporário
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