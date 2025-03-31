from flask import Flask, render_template, request, jsonify
import whisper
import epitran
import json
from gtts import gTTS
import os
import random

app = Flask(__name__)
model = whisper.load_model('base')  # Load Whisper model
epi = epitran.Epitran('eng-Latn')   # English IPA converter

# Load sentences
with open('sentences.json', 'r') as f:
    sentences_data = json.load(f)
    sentences = sentences_data['beginner'] + sentences_data['intermediate'] + sentences_data['advanced']

@app.route('/')
def index():
    sentence = random.choice(sentences)
    return render_template('index.html', sentence=sentence)

@app.route('/analyze', methods=['POST'])
def analyze():
    audio_file = request.files['audio']
    audio_file.save('temp.wav')
    target_text = request.form['target_text'].lower()
    
    # Whisper transcription
    result = model.transcribe('temp.wav')
    user_text = result['text'].lower()
    
    # IPA analysis
    target_ipa = epi.transliterate(target_text)
    user_ipa = epi.transliterate(user_text)
    min_len = min(len(target_ipa), len(user_ipa))
    score = sum(a == b for a, b in zip(target_ipa, user_ipa[:min_len])) / len(target_ipa) * 100
    
    # Feedback
    feedback = "Excellent!" if score > 90 else "Good effort!" if score > 70 else "Practice more!"
    if 'th' in target_text and 'th' not in user_text:
        feedback += " Try 'th' with your tongue between your teeth."
    elif len(user_text.split()) < len(target_text.split()):
        feedback += " You missed some words—speak slowly."
    
    # Native audio
    audio_path = 'static/native_audio.mp3'
    tts = gTTS(text=target_text, lang='en')
    tts.save(audio_path)
    
    os.remove('temp.wav')  # Cleanup
    return jsonify({
        'score': round(score, 2),
        'feedback': feedback,
        'target_ipa': target_ipa,
        'user_ipa': user_ipa,
        'audio': '/static/native_audio.mp3',
        'spoken_text': user_text
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)