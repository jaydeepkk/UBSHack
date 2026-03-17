# PDF Upload + 200-Word Summary (Python PoC)

This PoC is a small Streamlit app that:
1. Uploads a PDF document.
2. Scans/extracts text from the PDF.
3. Creates an approximately **200-word summary**.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser, upload a PDF, and review the generated summary.

## Check in to the branch

If you want to check in your own updates to the current branch, use:

```bash
git branch --show-current
git status
git add .
git commit -m "your message"
git push origin $(git branch --show-current)
```

## Notes

- This version extracts embedded text from PDFs using `pypdf`.
- For scanned image-only PDFs, OCR can be added later (e.g., `pytesseract` + `pdf2image`).
