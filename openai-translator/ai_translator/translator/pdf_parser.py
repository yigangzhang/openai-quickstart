import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, start_page: Optional[int] = None, end_page: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)

        with pdfplumber.open(pdf_file_path) as pdf:
            # Validate and adjust page range
            total_pages = len(pdf.pages)
            start_page = 1 if start_page is None else max(1, min(start_page, total_pages))
            end_page = total_pages if end_page is None else min(end_page, total_pages)
            
            # Convert to 0-based index for pdfplumber
            pages_to_process = pdf.pages[start_page-1:end_page]

            for pdf_page in pages_to_process:
                page = Page()

                # Store the original text content
                raw_text = pdf_page.extract_text()
                tables = pdf_page.extract_tables()

                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            raw_text = raw_text.replace(cell, "", 1)

                # Handling text
                if raw_text:
                    # Remove empty lines and leading/trailing whitespaces
                    raw_text_lines = raw_text.splitlines()
                    cleaned_raw_text_lines = [line.strip() for line in raw_text_lines if line.strip()]
                    cleaned_raw_text = "\n".join(cleaned_raw_text_lines)

                    text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
                    page.add_content(text_content)
                    LOG.debug(f"[raw_text]\n {cleaned_raw_text}")



                # Handling tables
                if tables:
                    table = TableContent(tables)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                book.add_page(page)

        return book
