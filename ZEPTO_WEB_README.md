# Zepto Compression Web Interface

A modern, elegant Flask web application for Zepto SPR compression and decompression with a beautiful dark mode interface.

## Features

- **Compression**: Upload files or paste text to compress to Zepto SPR format (100:1 to 1000:1 compression ratios)
- **Decompression**: Decompress Zepto SPR back to original text with optional codex support
- **Combined Interface**: Single-page interface supporting both compression and decompression
- **Modern Dark Mode Design**: Elegant, responsive design with glassmorphism effects
- **Mobile Responsive**: Fully optimized for both desktop and mobile devices
- **Real-time Processing**: Fast compression/decompression with progress indicators
- **Download Support**: Download compressed artifacts (Zepto SPR, codex, stages) and decompressed text

## Installation

1. Install Python dependencies:
```bash
pip install -r zepto_web_requirements.txt
```

**Note**: For document formats (`.doc`, `.docx`, `.rtf`, `.odt`), additional libraries are used:
- `python-docx` for `.docx` files
- `docx2txt` or `textract` for `.doc` files (legacy Word format)
- `striprtf` for `.rtf` files
- `odfpy` for `.odt` files

These are included in `zepto_web_requirements.txt` but may require system dependencies for some formats.

2. Ensure Zepto compression module is available:
```bash
# The app will check for Three_PointO_ArchE.zepto_spr_processor
# Make sure your project structure is set up correctly
```

## Usage

### Starting the Server

```bash
python zepto_web_app.py
```

The server will start on `http://localhost:5000`

### Accessing the Interface

- **Main (Combined)**: http://localhost:5000
- **Compress Only**: http://localhost:5000/compress
- **Decompress Only**: http://localhost:5000/decompress

## Interface Modes

### Compression Mode

1. **Upload a File**: Click "Choose File" or drag and drop a file
   - **Text formats**: `.txt`, `.md`, `.markdown`, `.text`
   - **JSON formats**: `.json`, `.jsonl`
   - **Code formats**: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.java`, `.cpp`, `.c`, `.h`, `.cs`, `.go`, `.rs`, `.rb`, `.php`, `.swift`, `.kt`
   - **Web formats**: `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.xml`, `.xhtml`
   - **Data formats**: `.csv`, `.tsv`, `.log`
   - **Document formats**: `.doc`, `.docx`, `.rtf`, `.odt`
   - **Config formats**: `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.properties`, `.env`
   - **Script formats**: `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`
   - **Other**: `.sql`, `.r`, `.m`, `.pl`, `.pm`, `.lua`, `.vim`, `.tex`, `.latex`, `.rst`, `.bib`, `.org`
   - **Files without extension** are also accepted (treated as text)
   - Maximum file size: 50MB

2. **Or Paste Text**: Enter text directly in the textarea

3. **Select Compression Stage**:
   - **Zepto** (Default): Maximum compression (100:1 to 1000:1)
   - **Atto**: Very high compression (50:1 to 100:1)
   - **Femto**: High compression (20:1 to 50:1)
   - **Pico**: Medium-high compression (10:1 to 20:1)
   - **Micro**: Medium compression (5:1 to 10:1)
   - **Nano**: Low-medium compression (2:1 to 5:1)
   - **Concise**: Low compression (1.5:1 to 2:1)

4. **Click "Compress"**: Process the input and view results

5. **Download Results**:
   - Zepto SPR text file
   - Codex JSON (required for decompression)
   - Compression stages JSON

### Decompression Mode

1. **Paste Zepto SPR**: Enter the compressed Zepto SPR text

2. **Provide Codex** (Optional but Recommended):
   - Paste the codex JSON for accurate decompression
   - Usually provided with the Zepto SPR output

3. **Provide Compression Stages** (Optional):
   - Paste compression stages JSON for enhanced decompression

4. **Click "Decompress"**: Process and view decompressed text

5. **Download**: Download the decompressed text file

## API Endpoints

### POST `/api/compress`

Compress text or file to Zepto SPR.

**Form Data**:
- `file` (optional): File to compress
- `text` (optional): Text to compress
- `target_stage` (optional): Compression stage (default: "Zepto")

**Response**:
```json
{
  "success": true,
  "zepto_spr": "...",
  "compression_ratio": 150.5,
  "original_length": 15000,
  "zepto_length": 100,
  "processing_time_sec": 0.123,
  "codex": {...},
  "compression_stages": [...]
}
```

### POST `/api/decompress`

Decompress Zepto SPR to original text.

**Form Data**:
- `zepto_spr` (required): Zepto SPR text
- `codex` (optional): Codex JSON
- `compression_stages` (optional): Compression stages JSON

**Response**:
```json
{
  "success": true,
  "decompressed_text": "...",
  "decompressed_length": 15000,
  "zepto_length": 100,
  "decompression_time_sec": 0.045
}
```

### POST `/api/download`

Download compressed artifacts.

**JSON Body**:
```json
{
  "type": "zepto|codex|stages",
  "content": "...",
  "filename": "output"
}
```

## Design Features

- **Dark Mode**: Beautiful dark theme with gradient accents
- **Glassmorphism**: Modern frosted glass effects
- **Responsive**: Mobile-first design that works on all devices
- **Smooth Animations**: Elegant transitions and loading states
- **Accessibility**: Keyboard navigation and screen reader support
- **Modern Typography**: Inter font for UI, JetBrains Mono for code

## File Structure

```
zepto_web_app.py          # Flask application
templates/
  index.html              # Main HTML template
static/
  css/
    style.css             # Dark mode styles
  js/
    app.js                # JavaScript functionality
uploads/                  # Temporary upload directory
outputs/                  # Download output directory
```

## Configuration

Edit `zepto_web_app.py` to customize:

- `MAX_CONTENT_LENGTH`: Maximum file size (default: 50MB)
- `UPLOAD_FOLDER`: Upload directory (default: 'uploads')
- `OUTPUT_FOLDER`: Output directory (default: 'outputs')
- `ALLOWED_EXTENSIONS`: Allowed file types

## Troubleshooting

**Module Not Available Error**:
- Ensure `Three_PointO_ArchE.zepto_spr_processor` is in your Python path
- Check that the Zepto compression module is properly installed

**File Upload Issues**:
- Check file size (max 50MB)
- For text files: UTF-8 encoding is preferred, but other encodings (latin-1, cp1252, iso-8859-1) are attempted automatically
- For document formats (`.doc`, `.docx`, `.rtf`, `.odt`): Ensure required libraries are installed
- Files without extensions are accepted and treated as text
- If a file type fails, try converting it to `.txt` or `.md` format first

**Decompression Fails**:
- Ensure codex is provided for accurate decompression
- Check that Zepto SPR text is complete and not corrupted

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Part of the ResonantiA Protocol v3.0 project.

