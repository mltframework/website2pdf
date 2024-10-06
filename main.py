import hashlib
import os
import re
import asyncio
import argparse
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    NameObject,
    ArrayObject,
    RectangleObject,
)
from reportlab.pdfgen import canvas

OUTPUT_DIR = "website_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Argument Parser to add options
parser = argparse.ArgumentParser(description="Crawl a website and save as PDFs.")
parser.add_argument(
    "root_url", type=str, help="The root URL of the website to start crawling from."
)
parser.add_argument(
    "-e",
    "--exclude",
    nargs="*",
    help="Link texts to exclude from crawling.",
    default=[],
)
parser.add_argument(
    "-L",
    "--level",
    type=int,
    help="Max depth of the crawl (0 = root page only)",
    default=0,
)
args = parser.parse_args()


async def crawl_and_save_pdf(
    url,
    visited,
    visited_hashes,
    browser,
    base_url,
    depth,
    max_depth,
    exclude_texts,
    pdf_info,
):
    normalized_url = normalize_url(url)
    if normalized_url in visited or depth > max_depth:
        return
    visited.add(normalized_url)

    # Create browser context and page
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Navigate to the page
        await page.goto(url, wait_until="load")

        # Get the page content
        content = await page.content()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        if content_hash in visited_hashes:
            print(f"Duplicate content found at {url}, skipping.")
            return
        visited_hashes.add(content_hash)

        # Save the page as a PDF
        sanitized_url = re.sub(r"[^a-zA-Z0-9]", "_", normalized_url)
        page_path = os.path.join(OUTPUT_DIR, f"{sanitized_url}.pdf")
        await page.pdf(path=page_path)
        print(f"Saved: {url} to {page_path}")

        soup = BeautifulSoup(content, "html.parser")

        # Try to get the first <h1> tag text for a better title
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text(strip=True):
            title = h1_tag.get_text(strip=True)
        else:
            # Fallback to page title
            title = await page.title()

        # Collect information for TOC
        pdf_info.append(
            {
                "title": title,
                "url": normalized_url,
                "file_path": page_path,
                "num_pages": None,  # Will fill later
                "start_page": None,  # Will fill later
            }
        )

        # Extract links for further traversal
        for link_tag in soup.find_all("a", href=True):
            link_text = link_tag.get_text(strip=True)
            href = link_tag["href"]
            next_url = urljoin(
                base_url, href
            )  # Ensure correct handling of relative URLs

            # Normalize the next URL
            normalized_next_url = normalize_url(next_url)

            # Skip links with text matching any of the excluded texts
            if any(
                exclude_text.lower() in link_text.lower()
                for exclude_text in exclude_texts
            ):
                print(f"Skipping link: {link_text} ({next_url})")
                continue

            # Check if the next URL is valid and belongs to the base domain
            parsed_next_url = urlparse(normalized_next_url)
            parsed_base_url = urlparse(base_url)
            if (
                parsed_next_url.netloc == parsed_base_url.netloc
                and normalized_next_url not in visited
            ):
                await crawl_and_save_pdf(
                    next_url,
                    visited,
                    visited_hashes,
                    browser,
                    base_url,
                    depth + 1,
                    max_depth,
                    exclude_texts,
                    pdf_info,
                )

    except Exception as e:
        print(f"Error visiting {url}: {e}")

    finally:
        await page.close()
        await context.close()


def create_table_of_contents(toc_filename, pdf_info):
    c = canvas.Canvas(toc_filename)
    c.setTitle("Table of Contents")

    c.setFont("Helvetica", 16)
    c.drawString(200, 800, "Table of Contents")
    c.setFont("Helvetica", 12)

    y_position = 750
    link_rects = []  # To store link positions for annotations

    for i, entry in enumerate(pdf_info):
        # Shorten title if it's too long
        title = (
            entry["title"] if len(entry["title"]) <= 60 else entry["title"][:57] + "..."
        )
        link_text = f"{i + 1}. {title}"

        # Add entry to TOC
        c.drawString(50, y_position, link_text)

        # Record the position for the link annotation
        text_width = c.stringWidth(link_text, "Helvetica", 12)
        x1 = 50
        y1 = y_position - 2
        x2 = x1 + text_width
        y2 = y_position + 10
        link_rect = (x1, y1, x2, y2)
        link_rects.append(link_rect)

        y_position -= 20
        # Move to next page if space runs out
        if y_position < 50:
            c.showPage()
            y_position = 750

    c.save()
    print(f"Table of Contents saved as {toc_filename}")

    return link_rects  # Return the positions for later use


def combine_pdfs(output_filename, toc_filename, pdf_info):
    writer = PdfWriter()

    # Read the TOC PDF and add its pages
    toc_reader = PdfReader(toc_filename)
    writer.append_pages_from_reader(toc_reader)
    total_pages = len(toc_reader.pages)

    # Keep track of starting page numbers
    for info in pdf_info:
        pdf_reader = PdfReader(info["file_path"])
        num_pages = len(pdf_reader.pages)
        info["num_pages"] = num_pages
        info["start_page"] = total_pages  # Page numbering starts from 0
        total_pages += num_pages
        writer.append_pages_from_reader(pdf_reader)

    # Write the combined PDF without annotations first
    with open(output_filename, "wb") as f:
        writer.write(f)

    print(f"Combined PDF saved as {output_filename}")


def add_internal_links(output_filename, link_rects, pdf_info):
    reader = PdfReader(output_filename)
    writer = PdfWriter()

    # Copy pages to writer
    for page in reader.pages:
        writer.add_page(page)

    # Iterate over the links and add annotations
    for rect, info in zip(link_rects, pdf_info):
        x1, y1, x2, y2 = rect
        dest_page_number = info["start_page"]

        # Get the indirect reference to the target page
        target_page_ref = writer.pages[dest_page_number].indirect_reference

        # Create the GoTo action
        action = DictionaryObject(
            {
                NameObject("/S"): NameObject("/GoTo"),
                NameObject("/D"): ArrayObject([target_page_ref, NameObject("/Fit")]),
            }
        )

        # Create link annotation
        annotation = DictionaryObject()
        annotation.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/Rect"): RectangleObject([x1, y1, x2, y2]),
                NameObject("/Border"): ArrayObject(
                    [NumberObject(0), NumberObject(0), NumberObject(0)]
                ),
                NameObject("/A"): action,
                NameObject("/H"): NameObject("/I"),
            }
        )

        # Add the annotation to the TOC page (page 0)
        writer.add_annotation(page_number=0, annotation=annotation)

    # Save the updated PDF with annotations
    with open(output_filename, "wb") as f:
        writer.write(f)

    print(f"Internal links added to {output_filename}")


async def main(root_url, exclude_texts, max_depth):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        visited = set()
        visited_hashes = set()
        pdf_info = []  # To store information about each crawled page
        await crawl_and_save_pdf(
            root_url,
            visited,
            visited_hashes,
            browser,
            root_url,
            0,
            max_depth,
            exclude_texts,
            pdf_info,
        )
        await browser.close()

    # Generate TOC and get link positions
    toc_filename = "toc.pdf"
    link_rects = create_table_of_contents(toc_filename, pdf_info)

    # Combine all PDFs
    final_output = "final_combined_output.pdf"
    combine_pdfs(final_output, toc_filename, pdf_info)

    # Add internal links to TOC
    add_internal_links(final_output, link_rects, pdf_info)


from urllib.parse import urljoin, urlparse, urlunparse, urlencode, parse_qsl


def normalize_url(url):
    """
    Normalize the URL to ensure consistent representation.
    """
    parsed = urlparse(url)
    # Remove fragment
    parsed = parsed._replace(fragment="")
    # Remove 'www.' prefix and convert netloc to lowercase
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    # Remove default port numbers
    if netloc.endswith(":80"):
        netloc = netloc[:-3]
    elif netloc.endswith(":443"):
        netloc = netloc[:-4]
    # Remove trailing slash from path
    path = parsed.path.rstrip("/")
    # Sort query parameters (if you want to consider query parameters)
    # If you want to ignore query parameters, comment out the next two lines
    query = urlencode(sorted(parse_qsl(parsed.query)))
    parsed = parsed._replace(netloc=netloc, path=path, query=query)
    # Reconstruct the URL without the fragment
    normalized = urlunparse(parsed)
    return normalized.lower()


if __name__ == "__main__":
    asyncio.run(main(args.root_url, args.exclude, args.level))
