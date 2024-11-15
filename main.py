
import Transcription_
import Legenda


# Exemplo de uso
if __name__ == "__main__":
    video_path = r"C:\Users\welli\Downloads\video 1.mp4"
    output_video = "C:/Users/welli/Downloads/processed_video.mp4"
    transcricao, transcription_text = Transcription_.print_audio_info_and_transcribe(video_path)
    transcricao = [(word, str(time)) for word, time in transcricao]
    print(transcricao)
    Legenda.process_video(transcricao, video_path, output_video)
