from faster_whisper import WhisperModel
from pathlib import Path
import os


def transcribe_one_chunk(
    input_audio_path: str,
    output_text_path: str,
):
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

    print("Cargando modelo...")
    model = WhisperModel(
        "medium",          
        device="cpu",      
        compute_type="int8"
    )

    print("Transcribiendo...")
    segments, info = model.transcribe(
        input_audio_path,
        language="es",
        task="transcribe",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
        word_timestamps=False
    )

    full_text = []
    for segment in segments:
        line = segment.text.strip()
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {line}")
        full_text.append(line)

    transcript = "\n".join(full_text)

    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Idioma detectado: {info.language}")
    print(f"Guardado en: {output_text_path}")


if __name__ == "__main__":
    input_audio = "data/audio/chunks/chunk_008.wav"
    output_text = "data/transcripts/chunk_008_medium.txt"

    transcribe_one_chunk(input_audio, output_text)