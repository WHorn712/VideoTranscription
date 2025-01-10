import cv2
import os
import numpy as np
import imageio
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines[:2]  # Retorna no máximo duas linhas


def process_video(initial_transcricao, input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"Error: The file {input_path} does not exist.")
        return

    video = VideoFileClip(input_path)
    x = int(video.size[0] * 0.1)  # 10% da largura
    y = int(video.size[1] * 0.8)  # 80% da altura
    max_width = int(video.size[0] * 0.8)  # 80% da largura do vídeo

    font_size = 40  # Ajuste conforme necessário

    state = {
        'current_word_time': 0,
        'text': "",
        'transcricao': initial_transcricao
    }

    def get_new_text(font, max_width, transcricao, current_word_time):
        print(current_word_time, transcricao)
        text = ""
        last_word_time = current_word_time
        new_transcricao = transcricao.copy()

        line1 = ""
        line2 = ""

        for word, time in transcricao:
            # Try adding the word to the first line
            test_line1 = line1 + word + " "
            bbox1 = font.getbbox(test_line1.strip())
            width1 = bbox1[2] - bbox1[0]

            if width1 <= max_width and not line2:
                line1 = test_line1
                last_word_time = float(time)
            else:
                # If first line is full or there's already content in second line, add to second line
                test_line2 = line2 + word + " "
                bbox2 = font.getbbox(test_line2.strip())
                width2 = bbox2[2] - bbox2[0]

                if width2 <= max_width:
                    line2 = test_line2
                    last_word_time = float(time)
                else:
                    # If it doesn't fit on the second line, we're done
                    break

            # Remove the word from transcricao
            new_transcricao = new_transcricao[1:]

        # Combine the two lines
        text = (line1.strip() + "\n" + line2.strip()).strip()

        return text, last_word_time, new_transcricao

    def add_text(frame, t):
        # Criar uma imagem PIL a partir do frame
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Carregar a fonte
        font = ImageFont.truetype("ArchivoBlack-Regular.ttf", font_size)

        if state['current_word_time'] <= t:
            state['text'], state['current_word_time'], state['transcricao'] = get_new_text(
                font, max_width, state['transcricao'], state['current_word_time']
            )


        # Desenhar o texto
        lines = wrap_text(state['text'], font, max_width)
        line_height = font_size + 5  # Espaçamento entre linhas
        for i, line in enumerate(lines):
            draw.text((x, y + i * line_height), line, font=font, fill=(0, 255, 255))

        # Converter de volta para o formato OpenCV
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    video_with_text = video.fl(lambda gf, t: add_text(gf(t), t))

    # Verificação da duração para debug
    print(f"Duração do vídeo: {video.duration}")
    print(f"Duração final processada: {video_with_text.duration}")

    if output_path:
        video_with_text.write_videofile(output_path, codec='libx264', audio_codec='aac')
    else:
        video_with_text.preview()

    video.close()
    video_with_text.close()