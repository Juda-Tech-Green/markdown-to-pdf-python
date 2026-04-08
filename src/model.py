import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from playwright.async_api import async_playwright
import pypandoc

class ConversionService:
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.md = (
            MarkdownIt('commonmark', {'breaks': True, 'html': True})
            .enable(['table', 'strikethrough'])
            .use(tasklists_plugin)
            .use(front_matter_plugin)
        )
        self._setup_playwright_env()
        
    def _setup_playwright_env(self):
        """Configure Playwright browser path for bundled executable."""
        if getattr(sys, 'frozen', False):
            # If running as a bundled executable
            bundle_dir = Path(sys._MEIPASS)
            # Standard location we'll use in the .spec file
            browsers_path = bundle_dir / "playwright" / "driver" / "package" / ".local-browsers"
            if browsers_path.exists():
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path)
                print(f"Bundled environment: Setting PLAYWRIGHT_BROWSERS_PATH to {browsers_path}")
        
    def render_markdown_to_html(self, md_content: str) -> str:
        html_content = self.md.render(md_content)
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        return template.replace('<!-- CONTENT_PLACEHOLDER -->', html_content)

    async def _convert_to_pdf_async(self, html_content: str, output_path: str):
        async with async_playwright() as p:
            # Browser path is handled by PLAYWRIGHT_BROWSERS_PATH env var if set
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_content(html_content, wait_until='networkidle')
            
            # Wait for MathJax and Mermaid hooks
            try:
                await page.wait_for_function('() => window.mathjaxReady === true', timeout=15000)
            except Exception:
                print("Warning: MathJax ready signal timeout")
                
            try:
                await page.wait_for_function('() => window.mermaidReady === true', timeout=15000)
            except Exception:
                print("Warning: Mermaid ready signal timeout")
            
            # Additional small delay for final paint stabilization
            await page.wait_for_timeout(500)
            
            await page.pdf(
                path=output_path, 
                format="A4", 
                print_background=True,
                margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}
            )
            await browser.close()

    def convert_to_pdf(self, input_path: str, output_path: Optional[str] = None) -> str:
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
            
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        html_content = self.render_markdown_to_html(md_content)
        
        if not output_path:
            output_path = str(input_file.with_suffix('.pdf'))
            
        asyncio.run(self._convert_to_pdf_async(html_content, output_path))
        return output_path

    def convert_to_docx(self, input_path: str, output_path: Optional[str] = None) -> str:
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
            
        if not output_path:
            output_path = str(input_file.with_suffix('.docx'))
            
        # pypandoc handles the conversion
        pypandoc.convert_file(input_path, 'docx', outputfile=output_path)
        return output_path
