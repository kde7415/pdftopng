from flask import Flask, request, send_from_directory, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import uuid
import fitz  # PyMuPDF
import zipfile

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
        doc = fitz.open(filepath)
        image_filenames = []
        zip_id = uuid.uuid4().hex
        zip_folder = os.path.join(app.config['OUTPUT_FOLDER'], zip_id)
        os.makedirs(zip_folder, exist_ok=True)

        # 모든 페이지를 이미지로 변환
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=200)
            img_filename = f"page_{i + 1}.png"
            img_path = os.path.join(zip_folder, img_filename)
            pix.save(img_path)
            image_filenames.append(img_path)

        # ZIP 파일로 압축
        zip_filename = f"{zip_id}.zip"
        zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in image_filenames:
                arcname = os.path.basename(img_path)
                zipf.write(img_path, arcname=arcname)

        return jsonify({'download_url': f'/download/{zip_filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
