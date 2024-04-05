from piper.voice import PiperVoice
from pathlib import Path
import wave
import json
import numpy as np
import sounddevice as sd

base_path = Path(__file__).parent.parent

def generate_audio(text, model, output_filepath, speaker=None):
    model_filepath = find_model_path(model)
    voice = PiperVoice.load(model_filepath)
    speaker_id = None
    if speaker:
        id_map = get_speaker_id_map(model)
        speaker_id = id_map[speaker]
    with wave.open(output_filepath, "w") as wav_file:
        voice.synthesize(text, wav_file, speaker_id=speaker_id)


def stream_audio(text, model, speaker=None):
    model_filepath = find_model_path(model)
    voice = PiperVoice.load(model_filepath)
    speaker_id = None
    if speaker:
        id_map = get_speaker_id_map(model)
        speaker_id = id_map[speaker]
    stream = sd.OutputStream(
        samplerate=voice.config.sample_rate, channels=1, dtype="int16"
    )
    stream.start()
    for audio_bytes in voice.synthesize_stream_raw(text, speaker_id=speaker_id):
        int_data = np.frombuffer(audio_bytes, dtype=np.int16)
        stream.write(int_data)
    stream.stop()
    stream.close()


def list_models():
    models = Path(f"{base_path}/models/").rglob("*.onnx")
    available_models = [
        Path(i).stem for i in models if Path(i).with_suffix(".onnx.json").exists()
    ]
    return available_models

def find_model_path(model_name):
    models = Path(f"{base_path}/models/").rglob("*.onnx")
    for model in models:
        if model.stem == model_name:
            return str(model)
    return None

def get_speaker_id_map(model):
    model_filepath = Path(find_model_path(model)).with_suffix(".onnx.json")
    with open(model_filepath) as file:
        data = json.load(file)
    return data['speaker_id_map']