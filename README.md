# PDF2Text Converter

A robust Python application for converting PDF files to text format with multiple extraction methods.

## Features

- **Multiple extraction methods**: Uses both PyPDF2 and pdfplumber for reliable text extraction
- **Auto mode**: Automatically tries different methods to get the best results
- **Batch processing**: Convert multiple PDFs at once
- **Recursive directory processing**: Process all PDFs in subdirectories
- **Progress tracking**: Visual progress bar for batch operations
- **Error handling**: Graceful handling of corrupted or problematic PDFs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Convert a single PDF

```bash
# Display text to console
python pdf2text.py document.pdf

# Save to text file
python pdf2text.py document.pdf -o output.txt
```

### Convert multiple PDFs

```bash
# Convert all PDFs in a directory
python pdf2text.py /path/to/pdfs/ -o /path/to/output/

# Convert recursively (include subdirectories)
python pdf2text.py /path/to/pdfs/ -r -o /path/to/output/
```

### Options

- `-o, --output`: Specify output file or directory
- `-m, --method`: Choose extraction method (auto, pypdf2, pdfplumber)
- `-r, --recursive`: Process directories recursively
- `-v, --verbose`: Show detailed output

### Examples

```bash
# Use specific extraction method
python pdf2text.py document.pdf -m pdfplumber

# Convert all PDFs in current directory with verbose output
python pdf2text.py . -v -o ./converted/

# Recursive conversion with auto method
python pdf2text.py ./documents -r -m auto -o ./text_files/
```

## How it works

The app uses two popular PDF libraries:
1. **pdfplumber**: Better for complex layouts, tables, and formatted text
2. **PyPDF2**: Fallback option for simple text extraction

In auto mode (default), it tries pdfplumber first and falls back to PyPDF2 if needed, ensuring maximum compatibility with different PDF types.