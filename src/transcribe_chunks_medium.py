from faster_whisper import WhisperModel
import os
from pathlib import Path


def transcribe_chunks(
    input_dir: str,
    output_dir: str,
    model_size: str = "medium",
    device: str = "cpu",
    compute_type: str = "int8"
):
    os.makedirs(output_dir, exist_ok=True)

    print("Cargando modelo...")
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type
    )

    chunk_files = sorted(Path(input_dir).glob("chunk_*.wav"))
    print(f"Chunks encontrados: {len(chunk_files)}")

    for chunk_file in chunk_files:
        output_file = Path(output_dir) / f"{chunk_file.stem}.txt"

        print(f"\nTranscribiendo {chunk_file.name}...")

        segments, info = model.transcribe(
            str(chunk_file),
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

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"Guardado: {output_file.name}")
        print(f"Idioma detectado: {info.language}")

    print("\nTranscripción de chunks completada.")


if __name__ == "__main__":
    input_dir = "data/audio/chunks"
    output_dir = "data/transcripts/chunks"

    transcribe_chunks(
        input_dir=input_dir,
        output_dir=output_dir,
        model_size="medium",
        device="cpu",
        compute_type="int8"
    )