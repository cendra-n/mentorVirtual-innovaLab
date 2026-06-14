"""
Motor de embeddings con sentence-transformers.
Detecta automáticamente CUDA o cae a CPU.
Modelo: paraphrase-multilingual-MiniLM-L12-v2
  - 384 dimensiones
  - Soporta español perfecto
  - Pesa ~120MB
  - Funciona bien en CPU y vuela en GPU
"""
import logging
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Detectar dispositivo
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"🖥️  Tutor RAG — dispositivo: {DEVICE.upper()}")

# Cargar modelo una sola vez al arrancar Django
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("📦 Cargando modelo de embeddings...")
        _model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2',
            device=DEVICE
        )
        logger.info("✅ Modelo cargado correctamente.")
    return _model


def embed_text(text: str) -> list[float]:
    """Genera el embedding de un texto. Devuelve lista de 384 floats."""
    model = get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Genera embeddings para una lista de textos (más eficiente que uno por uno)."""
    model = get_model()
    vectors = model.encode(texts, convert_to_numpy=True, batch_size=32, show_progress_bar=False)
    return vectors.tolist()
