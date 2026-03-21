from faster_whisper import WhisperModel
import os
from pathlib import Path


def transcribe_chunks(
    input_dir: str,
    output_dir: str,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8"
):
    os.makedirs(output_dir, exist_ok=True)

    print("Cargando modelo...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # chunk_files = sorted(Path(input_dir).glob("chunk_*.wav"))
    chunk_files = [Path(input_dir) / "chunk_001.wav"]

    print(f"Chunks encontrados: {len(chunk_files)}")

    for chunk_file in chunk_files:
        output_file = Path(output_dir) / f"{chunk_file.stem}.txt"

        print(f"Transcribiendo {chunk_file.name}...")

        segments, info = model.transcribe(str(chunk_file), language="es")

        full_text = []
        for segment in segments:
            full_text.append(segment.text.strip())

        transcript = " ".join(full_text)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"Guardado: {output_file.name}")

    print("Transcripción de chunks completada.")


if __name__ == "__main__":
    input_dir = "data/audio/chunks"
    output_dir = "data/transcripts/chunks"

    transcribe_chunks(
        input_dir=input_dir,
        output_dir=output_dir,
        model_size="tiny",
        device="cpu",
        compute_type="int8"
    )