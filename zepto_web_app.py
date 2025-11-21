#!/usr/bin/env python3
"""
Zepto Compression/Decompression Web Interface
Modern Flask application with dark mode design for Zepto SPR compression and decompression.
"""

import os
import json
import time
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Zepto compression functions
try:
    from Three_PointO_ArchE.zepto_spr_processor import compress_to_zepto, decompress_from_zepto
    ZEPTO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import Zepto compression module: {e}")
    ZEPTO_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions - expanded to support more formats
ALLOWED_EXTENSIONS = {
    # Text formats
    'txt', 'md', 'markdown', 'text',
    # JSON formats
    'json', 'jsonl',
    # Code formats
    'py', 'js', 'jsx', 'ts', 'tsx', 'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt',
    # Web formats
    'html', 'htm', 'css', 'scss', 'sass', 'xml', 'xhtml',
    # Data formats
    'csv', 'tsv', 'log',
    # Document formats
    'doc', 'docx', 'rtf', 'odt',
    # Other text-based formats
    'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf', 'properties',
    'sh', 'bash', 'zsh', 'fish', 'ps1',
    'sql', 'r', 'm', 'pl', 'pm', 'lua', 'vim', 'vimrc',
    # Configuration and data
    'env', 'gitignore', 'dockerfile', 'makefile', 'cmake',
    # Markup and structured
    'tex', 'latex', 'bib', 'rst', 'org',
    # No extension (treat as text)
    ''
}


def allowed_file(filename):
    """Check if file extension is allowed."""
    if not filename or '.' not in filename:
        # Allow files without extension (treat as text)
        return True
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path, filename):
    """
    Extract text content from various file formats.
    Handles both text and binary formats.
    """
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Try reading as UTF-8 text first (for most text formats)
    if ext in {'txt', 'md', 'markdown', 'text', 'json', 'jsonl', 'py', 'js', 'jsx', 'ts', 'tsx',
               'html', 'htm', 'css', 'xml', 'csv', 'tsv', 'log', 'yaml', 'yml', 'toml', 'ini',
               'cfg', 'conf', 'properties', 'sh', 'bash', 'sql', 'r', 'tex', 'latex', 'rst',
               'env', 'gitignore', 'dockerfile', 'makefile', 'cmake', 'vim', 'vimrc', ''}:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except (UnicodeDecodeError, Exception):
                    continue
            raise ValueError(f"Could not decode file with UTF-8 or common encodings")
    
    # Handle JSONL (JSON Lines) - read line by line
    elif ext == 'jsonl':
        try:
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    lines.append(line.strip())
            return '\n'.join(lines)
        except Exception as e:
            raise ValueError(f"Error reading JSONL file: {e}")
    
    # Handle DOCX files
    elif ext == 'docx':
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)
        except ImportError:
            raise ValueError("python-docx library required for .docx files. Install with: pip install python-docx")
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {e}")
    
    # Handle DOC files (legacy Word format - requires additional libraries)
    elif ext == 'doc':
        try:
            # Try using python-docx2txt or textract
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except ImportError:
                try:
                    import textract
                    return textract.process(file_path).decode('utf-8')
                except ImportError:
                    raise ValueError("Library required for .doc files. Install with: pip install docx2txt or pip install textract")
        except Exception as e:
            raise ValueError(f"Error reading DOC file: {e}")
    
    # Handle RTF files
    elif ext == 'rtf':
        try:
            import striprtf
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                rtf_content = f.read()
            return striprtf.striprtf.StripRtf(rtf_content).get_text()
        except ImportError:
            # Fallback: try to read as text (RTF is text-based)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading RTF file: {e}")
    
    # Handle ODT files
    elif ext == 'odt':
        try:
            from odf import text, teletype
            from odf.opendocument import load
            doc = load(file_path)
            paragraphs = []
            for para in doc.getElementsByType(text.P):
                paragraphs.append(teletype.extractText(para))
            return '\n'.join(paragraphs)
        except ImportError:
            raise ValueError("odfpy library required for .odt files. Install with: pip install odfpy")
        except Exception as e:
            raise ValueError(f"Error reading ODT file: {e}")
    
    # Default: try to read as text
    else:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Could not read file: {e}")


@app.route('/')
def index():
    """Main page with combined interface."""
    return render_template('index.html', mode='combined')


@app.route('/compress')
def compress_page():
    """Compression-only page."""
    return render_template('index.html', mode='compress')


@app.route('/decompress')
def decompress_page():
    """Decompression-only page."""
    return render_template('index.html', mode='decompress')


@app.route('/api/compress', methods=['POST'])
def api_compress():
    """API endpoint for compression."""
    if not ZEPTO_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Zepto compression module not available'
        }), 500

    try:
        # Get file or text input
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Save file temporarily to extract text
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp_file:
                    file.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                try:
                    # Extract text using the file extraction function
                    content = extract_text_from_file(tmp_path, filename)
                except Exception as e:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    return jsonify({
                        'success': False,
                        'error': f'Error extracting text from file: {str(e)}'
                    }), 400
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
            else:
                return jsonify({
                    'success': False,
                    'error': 'File type not allowed'
                }), 400
        elif 'text' in request.form:
            content = request.form['text']
            filename = 'text_input.txt'
        else:
            return jsonify({
                'success': False,
                'error': 'No file or text provided'
            }), 400

        # Get target stage
        target_stage = request.form.get('target_stage', 'Zepto')
        valid_stages = ['Concise', 'Nano', 'Micro', 'Pico', 'Femto', 'Atto', 'Zepto']
        if target_stage not in valid_stages:
            target_stage = 'Zepto'

        # Compress
        start_time = time.time()
        result = compress_to_zepto(content, target_stage=target_stage)
        compression_time = time.time() - start_time

        if result.error:
            return jsonify({
                'success': False,
                'error': result.error
            }), 500

        # Get the full codex from the processor
        full_codex = {}
        try:
            from Three_PointO_ArchE.zepto_spr_processor import get_zepto_processor
            processor = get_zepto_processor()
            if processor and hasattr(processor, 'get_codex'):
                full_codex = processor.get_codex()
        except Exception as e:
            print(f"Warning: Could not retrieve full codex: {e}")

        # Prepare response
        response_data = {
            'success': True,
            'zepto_spr': result.zepto_spr,
            'compression_ratio': result.compression_ratio,
            'original_length': result.original_length,
            'zepto_length': result.zepto_length,
            'processing_time_sec': result.processing_time_sec,
            'compression_time_sec': compression_time,
            'target_stage': target_stage,
            'stages_completed': len(result.compression_stages),
            'new_codex_entries_count': len(result.new_codex_entries),
            'filename': filename,
            # Include both new codex entries (for decompression) and full codex (for reference)
            'codex': result.new_codex_entries,  # New entries created during this compression
            'full_codex': full_codex,  # Complete codex with all symbols
            'compression_stages': result.compression_stages
        }

        return jsonify(response_data)

    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large. Maximum size is 50MB.'
        }), 413
    except UnicodeDecodeError:
        return jsonify({
            'success': False,
            'error': 'File encoding error. Please ensure the file is UTF-8 encoded.'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Compression error: {str(e)}'
        }), 500


@app.route('/api/decompress', methods=['POST'])
def api_decompress():
    """API endpoint for decompression."""
    if not ZEPTO_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Zepto decompression module not available'
        }), 500

    try:
        # Get Zepto SPR
        zepto_spr = request.form.get('zepto_spr', '')
        if not zepto_spr:
            return jsonify({
                'success': False,
                'error': 'Zepto SPR text is required'
            }), 400

        # Get codex (optional but recommended)
        codex = None
        if 'codex' in request.form:
            try:
                codex = json.loads(request.form['codex'])
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid codex JSON format'
                }), 400

        # Get compression stages (optional)
        compression_stages = None
        if 'compression_stages' in request.form:
            try:
                compression_stages = json.loads(request.form['compression_stages'])
            except json.JSONDecodeError:
                pass  # Not critical

        # Decompress
        start_time = time.time()
        result = decompress_from_zepto(
            zepto_spr=zepto_spr,
            codex=codex,
            compression_stages=compression_stages
        )
        decompression_time = time.time() - start_time

        if result.error:
            return jsonify({
                'success': False,
                'error': result.error
            }), 500

        # Prepare response
        response_data = {
            'success': True,
            'decompressed_text': result.decompressed_text,
            'decompressed_length': len(result.decompressed_text),
            'zepto_length': len(zepto_spr),
            'decompression_time_sec': decompression_time,
            'symbols_expanded': result.symbols_expanded if hasattr(result, 'symbols_expanded') else {}
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Decompression error: {str(e)}'
        }), 500


@app.route('/api/download', methods=['POST'])
def api_download():
    """Download endpoint for compressed artifacts."""
    try:
        data = request.json
        file_type = data.get('type')  # 'zepto', 'codex', 'stages'
        content = data.get('content', '')
        filename = data.get('filename', 'output')

        if file_type == 'zepto':
            content_type = 'text/plain'
            extension = '.txt'
        elif file_type == 'codex':
            content_type = 'application/json'
            extension = '_codex.json'
            content = json.dumps(content, indent=2, ensure_ascii=False)
        elif file_type == 'stages':
            content_type = 'application/json'
            extension = '_stages.json'
            content = json.dumps(content, indent=2, ensure_ascii=False)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

        # Save to temporary file
        output_path = Path(app.config['OUTPUT_FOLDER']) / f"{filename}{extension}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{filename}{extension}",
            mimetype=content_type
        )

    except Exception as e:
        return jsonify({
            'error': f'Download error: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html', mode='combined', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    print("🚀 Starting Zepto Web Interface...")
    print(f"   Compression module: {'✓ Available' if ZEPTO_AVAILABLE else '✗ Not Available'}")
    print(f"   Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"   Output folder: {app.config['OUTPUT_FOLDER']}")
    print(f"   Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    print("\n📱 Access the interface at: http://localhost:5000")
    print("   - Main: http://localhost:5000")
    print("   - Compress only: http://localhost:5000/compress")
    print("   - Decompress only: http://localhost:5000/decompress\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

