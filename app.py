from flask import Flask, render_template, request, jsonify
import epitran
import json
from gtts import gTTS
import os
import random

app = Flask(__name__)
epi = epitran.Epitran('eng-Latn')  # English IPA converter

# Load sentences
with open('sentences.json', 'r') as f:
    sentences_data = json.load(f)
    sentences = sentences_data['beginner'] + sentences_data['intermediate'] + sentences_data['advanced']

@app.route('/')
def index():
    sentence = random.choice(sentences)  # Random sentence for practice
    return render_template('index.html', sentence=sentence)

@app.route('/analyze', methods=['POST'])
def analyze():
    user_text = request.json['spoken_text'].lower()
    target_text = request.json['target_text'].lower()
    
    # Convert to IPA
    target_ipa = epi.transliterate(target_text)
    user_ipa = epi.transliterate(user_text)
    
    # Calculate score (phoneme similarity)
    min_len = min(len(target_ipa), len(user_ipa))
    score = sum(a == b for a, b in zip(target_ipa, user_ipa[:min_len])) / len(target_ipa) * 100
    
    # Generate feedback
    feedback = "Great job!" if score > 80 else "Keep practicing!"
    if 'th' in target_text and 'th' not in user_text:
        feedback = "Focus on 'th'—place your tongue between your teeth."
    elif len(user_text.split()) < len(target_text.split()):
        feedback = "You missed some words—try again slowly."
    
    # Generate native audio
    audio_path = 'static/native_audio.mp3'
    tts = gTTS(text=target_text, lang='en', slow=False)
    tts.save(audio_path)
    
    return jsonify({
        'score': round(score, 2),
        'feedback': feedback,
        'target_ipa': target_ipa,
        'user_ipa': user_ipa,
        'audio': '/static/native_audio.mp3'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)