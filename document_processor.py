from pathlib import Path
from pypdf import PdfReader
from docx import Document
from pdf2image import convert_from_path
import pytesseract


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\Sahana\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)


def extract_text_from_file(file_path):

    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    # PDF
    if extension == ".pdf":

        reader = PdfReader(str(file_path))

        pages = []

        # Try normal PDF extraction
        for page_number, page in enumerate(reader.pages, start=1):

            page_text = page.extract_text()

            pages.append({
                "text": page_text.strip() if page_text else "",
                "source": file_path.name,
                "page": page_number
            })

        # If PDF is scanned, use OCR
        if not any(page["text"] for page in pages):

            print("No text found in PDF.")
            print("Using OCR...")

            images = convert_from_path(
                str(file_path),
                poppler_path=POPPLER_PATH
            )

            pages = []

            for page_number, image in enumerate(images, start=1):

                print(f"OCR page {page_number}...")

                page_text = pytesseract.image_to_string(image)

                pages.append({
                    "text": page_text.strip(),
                    "source": file_path.name,
                    "page": page_number
                })

            print("OCR completed!")

        return pages

    # DOCX
    elif extension == ".docx":

        document = Document(str(file_path))

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        return [{
            "text": text,
            "source": file_path.name,
            "page": None
        }]

    # TXT
    elif extension == ".txt":

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        return [{
            "text": text,
            "source": file_path.name,
            "page": None
        }]

    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload PDF, DOCX, or TXT."
        )


# Test
if __name__ == "__main__":

    file_path = "documents/sample.pdf"

    pages = extract_text_from_file(file_path)

    print("\nExtracted pages:")
    print("--------------------------------")

    for page in pages:

        print("Source:", page["source"])
        print("Page:", page["page"])
        print("Text:")
        print(page["text"])
        print("--------------------------------")