# MD to PDF Converter

A utility with two different approaches to convert Markdown files to PDF with styled output.

## Two Conversion Options

### 1. Puppeteer Version (`md-to-pdf.js`)
- Uses modern Puppeteer + markdown-it
- Higher quality output with better rendering
- Larger file sizes but more precise formatting

### 2. No-Puppeteer Version (`md_to_pdf_no_pup.js`)
- Uses markdown-pdf + markdown-it
- Lighter weight, no browser dependencies
- Smaller file sizes, faster conversion

## Installation

```bash
npm install markdown-it puppeteer highlight.js markdown-pdf
```

## Usage

### Puppeteer Version (High Quality):
```bash
node md-to-pdf.js <filename.md>
npm run convert-resume
```

### No-Puppeteer Version (Lightweight):
```bash
node md_to_pdf_no_pup.js <filename.md>
npm run convert-resume-no-pup
```

### General conversion scripts:
```bash
npm run md-to-pdf
npm run md-to-pdf-no-pup
```

## Features

- ✅ Clean, professional PDF styling
- ✅ Proper heading hierarchy
- ✅ Code syntax highlighting
- ✅ Table formatting
- ✅ Responsive layout for print
- ✅ Custom CSS styling
- ✅ File size reporting

## Examples

```bash
# Puppeteer version (high quality)
node md-to-pdf.js resume.md
npm run convert-resume

# No-Puppeteer version (lightweight)
node md_to_pdf_no_pup.js resume.md
npm run convert-resume-no-pup

# Convert README with either version
node md-to-pdf.js README.md
node md_to_pdf_no_pup.js README.md
```

## Output

The script will create a PDF file with the same name as the input file, replacing the `.md` extension with `.pdf`.

## Styling

The PDF output uses custom CSS styling defined in `pdf-styles.css`. You can modify this file to customize the appearance of your PDFs.

## Dependencies

### Puppeteer Version:
- `markdown-it`: Modern markdown parser with extensible syntax
- `puppeteer`: Headless Chrome for high-quality PDF generation
- `highlight.js`: Syntax highlighting for code blocks

### No-Puppeteer Version:
- `markdown-it`: Modern markdown parser with extensible syntax
- `markdown-pdf`: Lightweight PDF generation without browser dependencies
- Embedded CSS for professional styling
