import noisereduce as nr
import numpy as np
from scipy import signal
from pydub.effects import normalize
from pydub import AudioSegment


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