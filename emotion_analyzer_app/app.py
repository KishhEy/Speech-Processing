import torch
import librosa
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import logging

# --- SETUP FLASK APP ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logging.basicConfig(level=logging.INFO)

# --- LOAD AI MODEL (once, at startup) ---
# UPDATED: Switched to a more robust model benchmarked for Speech Emotion Recognition.
MODEL_NAME = "superb/wav2vec2-base-superb-er" 
print("Loading model...")
try:
    model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Fatal Error: Could not load model. {e}")
    exit()

def analyze_emotion(file_path):
    """Analyzes the emotion from a given audio file path."""
    try:
        speech, sample_rate = librosa.load(file_path, sr=16000, mono=True)
        inputs = feature_extractor(speech, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        
        # The superb model has a different way of mapping labels
        # We get the scores and find the highest one
        scores = torch.nn.functional.softmax(logits, dim=-1)[0]
        
        # Get the top prediction
        top_prediction = scores.argmax().item()
        predicted_emotion = model.config.id2label[top_prediction]
        
        # The model sometimes outputs 'ang' for angry, 'hap' for happy, etc.
        # Let's map them to full words for a better UI.
        label_mapping = {
            "ang": "angry",
            "hap": "happy",
            "neu": "neutral",
            "sad": "sad"
        }
        
        return label_mapping.get(predicted_emotion, predicted_emotion)

    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        return "Error during analysis"
    finally:
        # Clean up the uploaded file after analysis
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Cleaned up {file_path}")


# --- API ROUTES ---
@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_audio():
    """Handle file upload and emotion analysis."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f"File saved to {filepath}")

        # Analyze the emotion
        emotion = analyze_emotion(filepath)
        
        return jsonify({"emotion": emotion})

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Runs the Flask app. 'debug=True' is for development.
    app.run(debug=True, port=5000)
