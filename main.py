import os
import subprocess
import shutil
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

from config import AppConfig

app = Flask(__name__)
app.config.from_object(AppConfig)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def check_ghostscript():
    """Check if Ghostscript is installed."""
    gs_commands = ['gs', 'gswin64c', 'gswin32c']
    for cmd in gs_commands:
        if shutil.which(cmd):
            return cmd
    return None

def compress_pdf(input_path, output_path, quality='printer'):
    """Compress PDF using Ghostscript."""
    gs_command = check_ghostscript()
    
    if not gs_command:
        raise Exception("Ghostscript not installed")
    
    cmd = [
        gs_command,
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS=/{quality}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        '-dDetectDuplicateImages=true',
        '-dCompressFonts=true',
        '-r150',
        f'-sOutputFile={output_path}',
        input_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Ghostscript error: {result.stderr}")
    
    return True

@app.route('/')
def index():
    quality_hint = app.config['QUALITY_HINT_TEMPLATE'].format(
        recommendation=app.config['QUALITY_RECOMMENDATION_LABEL']
    )
    return render_template(
        'index.html',
        app_name=app.config['APP_NAME'],
        subtitle=app.config['APP_SUBTITLE'],
        quality_options=app.config['QUALITY_OPTIONS'],
        default_quality=app.config['DEFAULT_QUALITY'],
        quality_hint=quality_hint,
        default_output_path=app.config['DEFAULT_OUTPUT_PATH']
    )

@app.route('/compress', methods=['POST'])
def compress():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        quality = request.form.get('quality', app.config['DEFAULT_QUALITY'])
        output_path = request.form.get('output_path', app.config['DEFAULT_OUTPUT_PATH'])
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'File must be a PDF'})
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_file)
        
        # Create output filename
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_compressed.pdf"
        temp_output = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Compress
        compress_pdf(input_file, temp_output, quality)
        
        # Calculate stats
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(temp_output)
        reduction = ((original_size - compressed_size) / original_size) * 100
        saved = original_size - compressed_size
        
        # Copy to output folder if specified
        final_path = temp_output
        if output_path and os.path.isdir(output_path):
            final_path = os.path.join(output_path, output_filename)
            shutil.copy2(temp_output, final_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'original_size': f"{original_size / (1024*1024):.2f} MB",
            'compressed_size': f"{compressed_size / (1024*1024):.2f} MB",
            'reduction': f"{reduction:.2f}",
            'saved': f"{saved / (1024*1024):.2f} MB",
            'save_path': final_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SlimPDF - PDF Compressor Web App Starting...")
    print("="*60)
    print("\n📱 Open in your browser:")
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"   http://{host}:{port}")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host=host, port=port)
