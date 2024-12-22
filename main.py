import asyncio
import http.server
import socketserver
import threading
from pathlib import Path
from playwright.async_api import async_playwright
from playwright_utils.playwright_utils import wait_for_element

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve files from the example_site directory
        root = Path(__file__).parent / "example_site"
        return str(root / path.lstrip("/"))

def start_server():
    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

async def run(playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    # Replace with the URL you want to test
    await page.goto(f"http://localhost:{PORT}/index.html")

    # Use the utility function to wait for an element
    selector = "#delayedElement"
    element = await wait_for_element(page, selector)
    print(f"Element text: {await element.inner_text()}")

    # Close the browser
    await browser.close()

async def main():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())