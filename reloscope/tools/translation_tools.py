"""Translation tools — Google Cloud Translation API.

Translates text into Indian regional languages for accessibility.
"""

from google.cloud import translate_v2 as translate


def translate_text(text: str, target_language: str = "hi") -> dict:
    """Translate text to a target language.

    Supports all major Indian languages. Use this when the user requests
    output in a regional language.

    Args:
        text: The text to translate.
        target_language: ISO 639-1 language code. Supported Indian languages:
            'hi' — Hindi
            'ta' — Tamil
            'te' — Telugu
            'kn' — Kannada
            'ml' — Malayalam
            'bn' — Bengali
            'mr' — Marathi
            'gu' — Gujarati
            'pa' — Punjabi
            'ur' — Urdu
            'or' — Odia
            'as' — Assamese

    Returns:
        A dictionary with the translated text, source language detected,
        and target language used.
    """
    try:
        client = translate.Client()
        result = client.translate(text, target_language=target_language)
        return {
            "translated_text": result["translatedText"],
            "source_language": result.get("detectedSourceLanguage", "en"),
            "target_language": target_language,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
