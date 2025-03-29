from flask import Flask, request, send_from_directory, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import uuid
import fitz  # PyMuPDF

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 폴더가 없으면 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # PDF 열기
        doc = fitz.open(filepath)
        page = doc.load_page(0)  # 첫 페이지만 이미지로 변환
        pix = page.get_pixmap(dpi=200)  # 해상도 조정 가능

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        pix.save(output_path)

        return jsonify({'download_url': f'/download/{output_filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
