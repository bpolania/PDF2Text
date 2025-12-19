#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Optional, List
import click
from tqdm import tqdm
import PyPDF2
import pdfplumber


class PDFConverter:
    def __init__(self, method: str = 'auto'):
        self.method = method

    def extract_with_pypdf2(self, pdf_path: Path) -> str:
        text = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())

            return '\n'.join(text)
        except Exception as e:
            raise Exception(f"PyPDF2 extraction failed: {str(e)}")

    def extract_with_pdfplumber(self, pdf_path: Path) -> str:
        text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return '\n'.join(text)
        except Exception as e:
            raise Exception(f"pdfplumber extraction failed: {str(e)}")

    def convert(self, pdf_path: Path) -> str:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")

        if self.method == 'pypdf2':
            return self.extract_with_pypdf2(pdf_path)
        elif self.method == 'pdfplumber':
            return self.extract_with_pdfplumber(pdf_path)
        else:
            try:
                text = self.extract_with_pdfplumber(pdf_path)
                if not text.strip():
                    text = self.extract_with_pypdf2(pdf_path)
                return text
            except:
                return self.extract_with_pypdf2(pdf_path)

    def batch_convert(self, pdf_paths: List[Path], output_dir: Optional[Path] = None) -> dict:
        results = {}

        for pdf_path in tqdm(pdf_paths, desc="Converting PDFs"):
            try:
                text = self.convert(pdf_path)

                if output_dir:
                    output_path = output_dir / f"{pdf_path.stem}.txt"
                    output_path.write_text(text, encoding='utf-8')
                    results[str(pdf_path)] = {'status': 'success', 'output': str(output_path)}
                else:
                    results[str(pdf_path)] = {'status': 'success', 'text': text[:200] + '...' if len(text) > 200 else text}

            except Exception as e:
                results[str(pdf_path)] = {'status': 'error', 'error': str(e)}

        return results


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file or directory for converted text')
@click.option('-m', '--method', type=click.Choice(['auto', 'pypdf2', 'pdfplumber']), default='auto',
              help='Extraction method to use (default: auto)')
@click.option('-r', '--recursive', is_flag=True, help='Process all PDFs in directory recursively')
@click.option('-v', '--verbose', is_flag=True, help='Show detailed output')
def main(input_path: str, output: Optional[str], method: str, recursive: bool, verbose: bool):
    input_path = Path(input_path)
    converter = PDFConverter(method=method)

    if input_path.is_file():
        if verbose:
            click.echo(f"Converting single PDF: {input_path}")

        try:
            text = converter.convert(input_path)

            if output:
                output_path = Path(output)
                output_path.write_text(text, encoding='utf-8')
                click.echo(f"✅ Successfully converted to: {output_path}")
            else:
                click.echo("\n" + "="*50)
                click.echo("EXTRACTED TEXT:")
                click.echo("="*50)
                click.echo(text)

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)

    elif input_path.is_dir():
        pattern = '**/*.pdf' if recursive else '*.pdf'
        pdf_files = list(input_path.glob(pattern))

        if not pdf_files:
            click.echo(f"No PDF files found in {input_path}")
            sys.exit(0)

        click.echo(f"Found {len(pdf_files)} PDF files")

        output_dir = None
        if output:
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)

        results = converter.batch_convert(pdf_files, output_dir)

        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        error_count = sum(1 for r in results.values() if r['status'] == 'error')

        click.echo(f"\n✅ Successfully converted: {success_count}/{len(pdf_files)}")

        if error_count > 0:
            click.echo(f"❌ Failed: {error_count}")
            if verbose:
                click.echo("\nErrors:")
                for path, result in results.items():
                    if result['status'] == 'error':
                        click.echo(f"  - {path}: {result['error']}")

    else:
        click.echo(f"Invalid path: {input_path}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()