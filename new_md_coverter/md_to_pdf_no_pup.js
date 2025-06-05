#!/usr/bin/env node

/**
 * md-to-pdf-html-pdf.js
 *
 * Convert a Markdown file to a styled PDF, using html-pdf instead of Puppeteer.
 *
 * Usage:
 *   node md-to-pdf-html-pdf.js <markdown-file>
 * Example:
 *   node md-to-pdf-html-pdf.js resume.md
 */

// -------- CONFIGURATION --------
const UNIFIED_MARGIN    = '0.2cm';    // PDF margin on all sides
const MARKDOWN_SCALE    = 0.5;        // same scale you used before
const MAX_CONTENT_WIDTH = 800;        // px, same “800px” container
// --------------------------------

const fs       = require('fs');
const path     = require('path');
const markdown = require('markdown-it')({ html: true, breaks: true });
const htmlpdf  = require('html-pdf');

// 1) Parse command-line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node md-to-pdf-html-pdf.js <markdown-file>');
  console.error('Example: node md-to-pdf-html-pdf.js resume.md');
  process.exit(1);
}

const INPUT_FILE = args[0];
const inputPath  = path.resolve(INPUT_FILE);

if (!fs.existsSync(inputPath)) {
  console.error(`Error: File '${INPUT_FILE}' not found.`);
  process.exit(1);
}

const OUTPUT_FILE = INPUT_FILE.replace(/\.md$/i, '.pdf');
const outputPath  = path.resolve(OUTPUT_FILE);

console.log(`Converting ${INPUT_FILE} → ${OUTPUT_FILE} (using html-pdf)…`);

// 2) Read the Markdown file and render to raw HTML
const mdSource   = fs.readFileSync(inputPath, 'utf8');
const rawHtml    = markdown.render(mdSource);

// 3) Build a complete HTML document that matches your Puppeteer‐CSS
const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    /* exactly the same CSS you had before, minus any body‐margin */
    body {
      margin: 0;                     /* Puppeteer margins are replaced by html-pdf’s border setting */
      padding: 5px;                 /* inner whitespace around content */
      font-family: 'Arial', 'Helvetica', sans-serif;
      line-height: 1.3;
      color: #333;
      max-width: ${MAX_CONTENT_WIDTH}px;
      margin-left: auto;
      margin-right: auto;
      font-size: 10px;       

    }

    h1, h2, h3, h4, h5, h6 {
      color: #2c3e50;
      margin-top: 5px;
      margin-bottom: 5px;
    }

    h1 {
      font-size: 1.5em;
      border-bottom: 1px solid #3498db;
      padding-bottom: 2px;
    }

    h2 {
      font-size: 1.3em;
      border-bottom: 2px solid #ecf0f1;
      padding-bottom: 2px;
    }

    h3 {
      font-size: 1em;
      color: #34495e;
    }

    p {
      margin-bottom: 5px;
      text-align: justify;
    }

    ul, ol {
      margin-bottom: 10px;
      padding-left: 30px;
    }

    li {
      margin-bottom: 3px;
    }

    blockquote {
      border-left: 4px solid #3498db;
      margin: 20px 0;
      padding: 10px 20px;
      background-color: #f8f9fa;
      font-style: italic;
    }

    code {
      background-color: #f1f2f6;
      padding: 2px 4px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
    }

    pre {
      background-color: #f1f2f6;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
      margin: 15px 0;
    }

    pre code {
      background-color: transparent;
      padding: 0;
    }

    table {
      border-collapse: collapse;
      width: 100%;
      margin: 20px 0;
    }

    th, td {
      border: 1px solid #ddd;
      padding: 12px;
      text-align: left;
    }

    th {
      background-color: #f2f2f2;
      font-weight: bold;
    }

    a {
      color: #3498db;
      text-decoration: none;
    }

    hr {
      border: none;
      border-top: 2px solid #ecf0f1;
      margin: 30px 0;
    }
  </style>
</head>
<body>
  ${rawHtml}
</body>
</html>
`;

// 4) Convert that HTML into a PDF
//    html-pdf’s `border` option maps to the PDF‐margin on all sides.
const pdfOptions = {
  format: 'A4',
  border: {
    top:    UNIFIED_MARGIN,
    right:  UNIFIED_MARGIN,
    bottom: UNIFIED_MARGIN,
    left:   UNIFIED_MARGIN
  },
  // html-pdf uses “zoom” to shrink or enlarge content. 1.0 is 100%.
  // If you want exactly the same 0.7 scale, use zoom: 0.7
  zoom: MARKDOWN_SCALE,
  // renderDelay: 0   // you can add a small delay if your CSS is slow to load, but usually 0ms is fine
};

htmlpdf.create(fullHtml, pdfOptions).toFile(outputPath, (err, res) => {
  if (err) {
    console.error('❌ Error during PDF conversion:', err);
    process.exit(1);
  }

  console.log(`✅ Successfully created ${OUTPUT_FILE}`);

  // 5) Report resulting file size
  try {
    const stats   = fs.statSync(outputPath);
    const sizeKB  = (stats.size / 1024).toFixed(2);
    console.log(`📄 Output file size: ${sizeKB} KB`);
  } catch (_) { /* ignore */ }
});
