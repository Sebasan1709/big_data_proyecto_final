from faster_whisper import WhisperModel
import os


def transcribe_audio(input_audio_path: str, output_text_path: str):
    try:
        print("🔄 Cargando modelo Whisper (tiny)...")
        
        model = WhisperModel(
            "tiny",            
            device="cpu",      
            compute_type="int8"
        )

        print("🎧 Iniciando transcripción...")

        segments, info = model.transcribe(
            input_audio_path,
            language="es"
        )

        full_text = []

        for segment in segments:
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
            full_text.append(segment.text.strip())

        transcript = " ".join(full_text)

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        print("\n✅ Transcripción completada")
        print(f"🌎 Idioma detectado: {info.language}")
        print(f"💾 Guardado en: {output_text_path}")

    except Exception as e:
        print(f"❌ Error en transcripción: {e}")


if __name__ == "__main__":
    input_audio = "data/audio/audio_short.wav.wav"
    output_text = "data/transcripts/text_short.txt"

    transcribe_audio(input_audio, output_text)