import os
import whisper
from pydub import AudioSegment
import Audio
import Translator


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
        processed_audio_path = Audio.prepare_audio_for_transcription(video_path)


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

        # Processa transcrição por palavras
        transcricao = []
        for segment in result.get('segments', []):
            for word_info in segment.get('words', []):
                palavra = word_info['word'].strip()
                tempo = word_info['start']
                transcricao.append((palavra, tempo))



        # Processa transcrição por palavras
        transcricao = []
        for segment in result.get('segments', []):
            for word_info in segment.get('words', []):
                palavra = word_info['word'].strip()
                tempo = word_info['start']
                transcricao.append((palavra, tempo))

        transcription_text = result["text"]

        # Tradução para português se necessário
        transcription_text = Translator.get_translator_for_pt(result)

        # Imprime confiança na detecção de idioma
        if "language_probability" in result:
            confidence = result["language_probability"] * 100

        # Remove arquivo temporário
        os.remove(processed_audio_path)

        return transcricao, transcription_text

    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {str(e)}")
        if processed_audio_path and os.path.exists(processed_audio_path):
            os.remove(processed_audio_path)
        return [], []