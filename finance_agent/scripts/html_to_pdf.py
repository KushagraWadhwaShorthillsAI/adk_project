import asyncio
import sys
import os
from playwright.async_api import async_playwright

async def convert_html_to_pdf(source, output_path):
    """
    Converts a URL or a local HTML file to a PDF using Playwright.
    
    Args:
        source: URL (starts with http) or local file path.
        output_path: Path to save the resulting PDF.
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        print(f"Loading {source}...")
        
        if source.startswith("http"):
            # It's a URL
            await page.goto(source, wait_until="networkidle")
        else:
            # It's a local file
            abs_path = os.path.abspath(source)
            if not os.path.exists(abs_path):
                print(f"Error: File {abs_path} not found.")
                return
            await page.goto(f"file://{abs_path}", wait_until="networkidle")

        print(f"Converting to PDF: {output_path}...")
        
        # We use a standard A4 format or Letter
        await page.pdf(
            path=output_path, 
            format="Letter",
            margin={"top": "50px", "bottom": "50px", "left": "50px", "right": "50px"},
            print_background=True
        )
        
        await browser.close()
        print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python html_to_pdf.py <URL or local_html_file> <output_pdf_file>")
        print("Example: python3 html_to_pdf.py https://www.sec.gov/Archives/edgar/data/2035832/000119312525326780/d875386ds1.htm AKTS.pdf")
        sys.exit(1)

    source = sys.argv[1]
    output = sys.argv[2]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    
    asyncio.run(convert_html_to_pdf(source, output))
