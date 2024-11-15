
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

def get_translator_for_pt(result):

    # Detecta idioma
    detected_language = result.get("language", "desconhecido")
    print(f"\nIdioma detectado: {get_language_name(detected_language)}")

    transcription_text = result["text"]

    # Tradução para português se necessário
    if detected_language != 'pt':
        print("\nTradução para português:")
        try:
            translator = GoogleTranslator(source=detected_language, target='pt')
            translated_text = translator.translate(transcription_text)
            print(translated_text)
            return translated_text
        except Exception as e:
            print(f"Erro na tradução: {str(e)}")
            return None

    return transcription_text