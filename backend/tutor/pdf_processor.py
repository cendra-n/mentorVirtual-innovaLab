"""
Procesador de PDFs.
Extrae texto con pdfplumber y lo corta en chunks de ~500 chars
cuidando no cortar en el medio de una oración.
"""
import logging
import pdfplumber

logger = logging.getLogger(__name__)

CHUNK_SIZE    = 500   # caracteres por chunk
CHUNK_OVERLAP = 50    # overlap para no perder contexto entre chunks


def extract_chunks(pdf_path: str) -> list[dict]:
    """
    Lee un PDF y devuelve lista de dicts:
    { page_num: int, content: str }
    """
    chunks = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text or not text.strip():
                continue

            # Limpiar texto
            text = ' '.join(text.split())

            # Cortar en chunks
            page_chunks = _split_text(text, page_num)
            chunks.extend(page_chunks)

    logger.info(f"📄 PDF procesado: {len(chunks)} chunks extraídos.")
    return chunks


def _split_text(text: str, page_num: int) -> list[dict]:
    """Corta el texto en chunks respetando oraciones."""
    chunks = []
    start  = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        if end >= len(text):
            # Último chunk
            chunk = text[start:].strip()
            if chunk:
                chunks.append({'page_num': page_num, 'content': chunk})
            break

        # Buscar el último punto antes del límite para no cortar oraciones
        cut = text.rfind('.', start, end)
        if cut == -1 or cut <= start:
            cut = end  # No hay punto, cortamos igual

        chunk = text[start:cut + 1].strip()
        if chunk:
            chunks.append({'page_num': page_num, 'content': chunk})

        start = cut + 1 - CHUNK_OVERLAP

    return chunks
