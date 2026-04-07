import ffmpeg
import os

def extract_audio(input_video_path: str, output_audio_path: str):
    try:
        (
            ffmpeg
            .input(input_video_path)
            .output(output_audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .run(overwrite_output=True)
        )
        print(f"Audio extraído correctamente: {output_audio_path}")
    except Exception as e:
        print(f"Error extrayendo audio: {e}")


if __name__ == "__main__":
    input_video = "data/raw_videos/video_audiencia.mp4"
    output_audio = "data/audio/audio_audiencia.wav"

    # Crear carpeta si no existe
    os.makedirs("data/audio", exist_ok=True)

    extract_audio(input_video, output_audio)