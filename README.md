# Web-to-PDF Crawler

This Python script automates the process of crawling websites, saving individual pages as PDFs, and combining them into a single document with a clickable table of contents. It's ideal for creating offline archives, comprehensive documentation, or e-books from web content.

## Features

- Crawls websites starting from a given URL
- Converts each page to a PDF
- Combines all PDFs into a single document
- Generates a clickable table of contents
- Allows setting crawl depth and excluding specific links
- Handles relative and absolute URLs
- Avoids duplicate content

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/web-to-pdf-crawler.git
   cd web-to-pdf-crawler
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line with the following syntax:

```
python web_to_pdf_crawler.py <root_url> [options]
```

### Arguments

- `root_url`: The starting URL for the crawler (required)

### Options

- `-e` or `--exclude`: Specify link texts to exclude from crawling (can be used multiple times)
- `-L` or `--level`: Set the maximum depth of the crawl (default is 0, which crawls only the root page)

### Examples

1. Basic usage (crawl only the root page):
   ```
   python web_to_pdf_crawler.py https://example.com
   ```

2. Crawl to a depth of 2, excluding certain pages:
   ```
   python web_to_pdf_crawler.py https://example.com -L 2 -e "Privacy Policy" "Terms of Service"
   ```

## Output

- Individual PDFs are saved in the `website_pdfs` directory
- The final combined PDF is saved as `final_combined_output.pdf` in the script's directory

## How It Works

1. The script uses Playwright to render web pages and convert them to PDFs
2. BeautifulSoup is used to parse HTML and extract links
3. PyPDF2 is used to combine PDFs and add internal links
4. A table of contents is generated using ReportLab

## Limitations

- JavaScript-heavy websites may not render correctly
- The script respects `robots.txt` by default (controlled by Playwright)
- Very large websites may take a long time to crawl completely

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
