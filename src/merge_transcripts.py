import os
from pathlib import Path


def merge_transcripts(input_dir: str, output_file: str):
    transcript_files = sorted(Path(input_dir).glob("chunk_*.txt"))

    print(f"Archivos encontrados: {len(transcript_files)}")

    full_text = []

    for file in transcript_files:
        print(f"Leyendo {file.name}...")
        
        with open(file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            full_text.append(text)

    merged_text = "\n".join(full_text)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged_text)

    print(f"\n✅ Transcripción completa guardada en: {output_file}")


if __name__ == "__main__":
    input_dir = "data/transcripts/chunks"
    output_file = "data/transcripts/full_transcript.txt"

    merge_transcripts(input_dir, output_file)