from piper.voice import PiperVoice
from pathlib import Path
import wave
import numpy as np
import sounddevice as sd


def generate_audio(text, model, output_filepath):
    model_filepath = find_model_path(model)
    voice = PiperVoice.load(model_filepath)
    with wave.open(output_filepath, "w") as wav_file:
        voice.synthesize(text, wav_file)


def stream_audio(text, model):
    model_filepath = find_model_path(model)
    voice = PiperVoice.load(model_filepath)
    stream = sd.OutputStream(
        samplerate=voice.config.sample_rate, channels=1, dtype="int16"
    )
    stream.start()
    for audio_bytes in voice.synthesize_stream_raw(text):
        int_data = np.frombuffer(audio_bytes, dtype=np.int16)
        stream.write(int_data)
    stream.stop()
    stream.close()


def list_models():
    models = Path("models/").rglob("*.onnx")
    available_models = [
        Path(i).stem for i in models if Path(i).with_suffix(".onnx.json").exists()
    ]
    return available_models

def find_model_path(model_name):
    models = Path("models/").rglob("*.onnx")
    for model in models:
        if model.stem == model_name:
            return str(model)
    return None