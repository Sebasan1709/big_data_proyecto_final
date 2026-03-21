import os
import math
import subprocess


def get_audio_duration(input_audio_path: str) -> float:
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_audio_path
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def split_audio(input_audio_path: str, output_dir: str, chunk_length_seconds: int = 180):
    os.makedirs(output_dir, exist_ok=True)

    duration = get_audio_duration(input_audio_path)
    total_chunks = math.ceil(duration / chunk_length_seconds)

    print(f"Duración total: {duration:.2f} segundos")
    print(f"Chunks a generar: {total_chunks}")

    overlap = 30  # segundos

    for i in range(total_chunks):
        start_time = i * (chunk_length_seconds - overlap)
        output_path = os.path.join(output_dir, f"chunk_{i+1:03d}.wav")

        command = [
            "ffmpeg",
            "-y",
            "-i", input_audio_path,
            "-ss", str(start_time),
            "-t", str(chunk_length_seconds),
            output_path
        ]

        print(f"Generando {output_path}...")
        subprocess.run(command, check=True)

    print("División completada correctamente.")


if __name__ == "__main__":
    input_audio = "data/audio/audio_audiencia.wav"
    output_dir = "data/audio/chunks"

    split_audio(input_audio, output_dir, chunk_length_seconds=180)