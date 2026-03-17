import re
from collections import Counter
from io import BytesIO

import streamlit as st
from pypdf import PdfReader

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in",
    "is", "it", "its", "of", "on", "that", "the", "to", "was", "were", "will", "with", "this",
    "or", "we", "they", "their", "you", "your", "our", "can", "may", "also", "not", "but", "if",
    "than", "then", "there", "these", "those", "such", "into", "about", "over", "under", "after",
    "before", "between", "during", "using", "used", "use", "each", "other", "more", "most", "many",
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
    return "\n".join(pages)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def summarize_text(text: str, target_words: int = 200) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""

    word_freq = Counter(w for w in tokenize_words(text) if w not in STOPWORDS and len(w) > 2)
    if not word_freq:
        return " ".join(sentences[: min(5, len(sentences))])

    sentence_scores: list[tuple[int, float]] = []
    for idx, sentence in enumerate(sentences):
        words = tokenize_words(sentence)
        if not words:
            continue
        score = sum(word_freq.get(w, 0) for w in words) / max(len(words), 1)
        sentence_scores.append((idx, score))

    ranked = sorted(sentence_scores, key=lambda x: x[1], reverse=True)

    chosen_indices = []
    total_words = 0
    for idx, _score in ranked:
        sent_words = len(tokenize_words(sentences[idx]))
        chosen_indices.append(idx)
        total_words += sent_words
        if total_words >= target_words:
            break

    chosen_indices = sorted(set(chosen_indices))
    summary = " ".join(sentences[i] for i in chosen_indices)

    summary_words = tokenize_words(summary)
    if len(summary_words) > target_words:
        trimmed_words = summary.split()
        summary = " ".join(trimmed_words[:target_words])
        if not summary.endswith((".", "!", "?")):
            summary += "..."

    return summary


def main() -> None:
    st.set_page_config(page_title="PDF Scanner & Summarizer (PoC)", layout="centered")
    st.title("PDF Scanner & 200-Word Summary")
    st.write(
        "Upload a PDF file, extract/scanned text content, and generate an approximate 200-word summary."
    )

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is None:
        return

    file_bytes = uploaded_file.read()

    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(file_bytes)

    if not extracted_text.strip():
        st.error("No extractable text found in the PDF.")
        st.info("If your PDF is image-only, add OCR support (e.g., Tesseract + pdf2image) in a next step.")
        return

    st.subheader("Extracted Text Preview")
    st.text_area("First 2,000 characters", extracted_text[:2000], height=220)

    with st.spinner("Generating summary..."):
        summary = summarize_text(extracted_text, target_words=200)

    word_count = len(tokenize_words(summary))
    st.subheader("Summary")
    st.write(summary)
    st.caption(f"Summary length: ~{word_count} words")


if __name__ == "__main__":
    main()
