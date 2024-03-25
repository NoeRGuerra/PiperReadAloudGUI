from piper.voice import PiperVoice
import wave

def generate_audio(text, model, output_filepath):
    model_filepath = f"models/{model}.onnx"
    voice = PiperVoice.load(model_filepath)
    wav_file = wave.open(output_filepath, 'w')
    voice.synthesize(text, wav_file)
    wav_file.close()
    return