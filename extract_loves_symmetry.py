#!/usr/bin/env python3
"""Extract text from Love's Hidden Symmetry PDF"""
import sys

try:
    import PyPDF2
    print("Using PyPDF2")
    with open("Love-s-Hidden-Symmetry-pdf.pdf", "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)
        print(f"Total pages: {total_pages}")
        # Extract first 50 pages for analysis
        text = ""
        for i in range(min(50, total_pages)):
            page = pdf_reader.pages[i]
            text += f"\n\n--- PAGE {i+1} ---\n\n"
            text += page.extract_text()
        
        with open("loves_hidden_symmetry_extract.txt", "w", encoding="utf-8") as out:
            out.write(text)
        print(f"Extracted {min(50, total_pages)} pages ({len(text)} characters)")
        print("Saved to loves_hidden_symmetry_extract.txt")
        
except ImportError:
    try:
        import pdfplumber
        print("Using pdfplumber")
        with pdfplumber.open("Love-s-Hidden-Symmetry-pdf.pdf") as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            text = ""
            for i in range(min(50, total_pages)):
                page = pdf.pages[i]
                text += f"\n\n--- PAGE {i+1} ---\n\n"
                page_text = page.extract_text() or ""
                text += page_text
            
            with open("loves_hidden_symmetry_extract.txt", "w", encoding="utf-8") as out:
                out.write(text)
            print(f"Extracted {min(50, total_pages)} pages ({len(text)} characters)")
            print("Saved to loves_hidden_symmetry_extract.txt")
    except ImportError:
        print("ERROR: Neither PyPDF2 nor pdfplumber available")
        print("Install with: pip install PyPDF2")
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


