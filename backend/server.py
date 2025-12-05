import os
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from generator import run_narration_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

# Configuration
# Use absolute paths to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '../uploaded_pdfs')
OUTPUT_FOLDER = os.path.join(BASE_DIR, '../output/videos')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the front-end application."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """
    API Endpoint to handle video generation requests.
    """
    if 'manga-file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['manga-file']
    voice_model = request.form.get('voice-select')
    custom_prompt = request.form.get('personality-prompt')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logging.info(f"File uploaded: {filename}")
        logging.info(f"Starting generation task with voice: {voice_model}")

        try:
            # Call the pipeline
            # Pass OUTPUT_FOLDER so generator knows where to save
            output_filename = run_narration_pipeline(filepath, voice_model, custom_prompt, app.config['OUTPUT_FOLDER'])
            
            download_url = f"/download/{output_filename}"
            
            logging.info(f"Video generated: {output_filename}")
            
            return jsonify({
                'message': 'Video generation initiated successfully.',
                'filename': output_filename,
                'download_url': download_url
            }), 200

        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type. Only PDF allowed.'}), 400

@app.route('/download/<path:filename>')
def download_file(filename):
    """Serve generated video files."""
    logging.info(f"Download requested for: {filename}")
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    except Exception as e:
        logging.error(f"Download failed for {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/demo/<path:filename>')
def serve_demo(filename):
    """Serve demo files."""
    demo_folder = os.path.join(BASE_DIR, '../Demo')
    return send_from_directory(demo_folder, filename)

if __name__ == '__main__':
    # Development server
    app.run(debug=True, port=5000)
