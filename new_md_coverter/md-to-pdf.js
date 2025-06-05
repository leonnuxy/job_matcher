#!/usr/bin/env node

const fs = require('fs');
const markdownIt = require('markdown-it');
const puppeteer = require('puppeteer');
const path = require('path');

// ---- CONFIGURABLE VARIABLES ----
const UNIFIED_MARGIN = '0.2cm';
const MARKDOWN_SCALE = 0.7;
// --------------------------------

// Get command line arguments
const args = process.argv.slice(2);

if (args.length === 0) {
    console.log('Usage: node md-to-pdf.js <markdown-file>');
    console.log('Example: node md-to-pdf.js resume.md');
    process.exit(1);
}

const INPUT_FILE = args[0];
const inputPath = path.resolve(INPUT_FILE);

// Check if input file exists
if (!fs.existsSync(inputPath)) {
    console.error(`Error: File '${INPUT_FILE}' not found.`);
    process.exit(1);
}

// Generate output filename
const OUTPUT_FILE = INPUT_FILE.replace(/\.md$/i, '.pdf');
const outputPath = path.resolve(OUTPUT_FILE);

console.log(`Converting ${INPUT_FILE} to ${OUTPUT_FILE}...`);

// Step 1: Convert Markdown to HTML
const md = markdownIt({ html: true, breaks: true });
const markdown = fs.readFileSync(inputPath, 'utf8');
const html = md.render(markdown);

// Create a complete HTML document with styling
const styledHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    /* Remove body margin, only use padding for inner spacing */
    body {
      margin: 0;
      padding: 20px;
      font-family: 'Arial', 'Helvetica', sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 1000px;
      margin-left: auto;       
      margin-right: auto;
      /* No more margin: ${UNIFIED_MARGIN}; */
    }

    h1, h2, h3, h4, h5, h6 {
      color: #2c3e50;
      margin-top: 15px;
      margin-bottom: 5px;
    }

    h1 {
      font-size: 2em;
      border-bottom: 3px solid #3498db;
      padding-bottom: 5px;
    }

    h2 {
      font-size: 1.5em;
      border-bottom: 2px solid #ecf0f1;
      padding-bottom: 2px;
    }

    h3 {
      font-size: 1.0em;
      color: #34495e;
    }

    p {
      margin-bottom: 10px;
      text-align: justify;
    }

    ul, ol {
      margin-bottom: 15px;
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
  ${html}
</body>
</html>
`;

// Step 2: Convert HTML to PDF
(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setContent(styledHtml, { waitUntil: 'networkidle0' });
        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true,
            scale: MARKDOWN_SCALE,
            margin: {
                top: UNIFIED_MARGIN,
                bottom: UNIFIED_MARGIN,
                left: UNIFIED_MARGIN,
                right: UNIFIED_MARGIN,
            }
        });
        await browser.close();
        
        console.log(`✅ Successfully converted ${INPUT_FILE} to ${OUTPUT_FILE}`);
        
        // Check file size
        const stats = fs.statSync(outputPath);
        const fileSizeInBytes = stats.size;
        const fileSizeInKB = (fileSizeInBytes / 1024).toFixed(2);
        
        console.log(`📄 Output file size: ${fileSizeInKB} KB`);
    } catch (error) {
        console.error('Error converting file:', error.message);
        process.exit(1);
    }
})();
