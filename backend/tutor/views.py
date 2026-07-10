"""
tutor/views.py

Endpoints:
  POST /api/tutor/books/           → subir PDF y procesarlo
  GET  /api/tutor/books/           → listar libros del usuario
  DELETE /api/tutor/books/<id>/    → eliminar libro
  POST /api/tutor/books/<id>/ask/  → hacer una pregunta al libro
"""
import os
import logging
import tempfile
import urllib.request
import json

from django.conf import settings
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from .pdf_processor import extract_chunks
from .embeddings import embed_text, embed_batch
from .db import (
    sp_create_book, sp_save_chunk, sp_get_books,
    sp_delete_book, sp_search_chunks
)

logger = logging.getLogger(__name__)

# Prompt del profesor — empático, paciente, en español rioplatense
TUTOR_SYSTEM = """Sos un tutor educativo empático y paciente, especializado en ayudar a personas adultas que retoman sus estudios.
Tu estilo es cálido, motivador y usás ejemplos de la vida cotidiana (cocina, trabajo, hogar) para explicar conceptos.
Respondés ÚNICAMENTE basándote en el contenido del libro proporcionado.
Si la respuesta no está en el libro, decís amablemente que ese tema no está cubierto en este material.
Máximo 3 párrafos. Usás lenguaje simple y accesible."""

TUTOR_PROMPT = """El alumno pregunta: "{question}"

Fragmentos relevantes del libro (páginas {pages}):
{context}

Respondé la pregunta basándote únicamente en estos fragmentos. Sé claro, empático y motivador."""


class BookListView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = sp_get_books(request.user.id)
        return Response({'books': books})

    def post(self, request):
        """Subir y procesar un PDF."""
        pdf_file = request.FILES.get('pdf')
        title    = request.data.get('title', '').strip()
        subject  = request.data.get('subject', '').strip()

        if not pdf_file:
            return Response({'error': 'Se requiere un archivo PDF.'}, status=400)
        if not title:
            return Response({'error': 'El título es obligatorio.'}, status=400)
        if not pdf_file.name.endswith('.pdf'):
            return Response({'error': 'El archivo debe ser un PDF.'}, status=400)

        # Guardar PDF temporalmente
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            for chunk in pdf_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Crear registro del libro
            book_id = sp_create_book(
                user_id=request.user.id,
                title=title,
                subject=subject or 'General',
                filename=pdf_file.name,
            )

            # Extraer chunks del PDF
            chunks = extract_chunks(tmp_path)
            if not chunks:
                return Response({'error': 'No se pudo extraer texto del PDF.'}, status=400)

            # Generar embeddings en batch (eficiente)
            texts = [c['content'] for c in chunks]
            embeddings = embed_batch(texts)

            # Guardar chunks con embeddings
            for chunk, embedding in zip(chunks, embeddings):
                sp_save_chunk(
                    book_id=book_id,
                    content=chunk['content'],
                    page_num=chunk['page_num'],
                    embedding=embedding,
                )

            logger.info(f"📚 Libro {book_id} procesado: {len(chunks)} chunks guardados.")

            return Response({
                'message': f'¡Libro procesado! {len(chunks)} fragmentos indexados.',
                'book_id': book_id,
                'chunks':  len(chunks),
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error procesando PDF: {e}")
            return Response({'error': 'Error al procesar el PDF.'}, status=500)
        finally:
            os.unlink(tmp_path)


class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, book_id):
        user    = request.user
        role    = getattr(getattr(user, 'profile', None), 'role', 'STUDENT')
        is_prof = role in ['ADMIN', 'PROFESSOR'] or user.is_staff

        with connection.cursor() as cur:
            if is_prof:
                cur.execute("DELETE FROM tutor_books WHERE id = %s", [book_id])
            else:
                cur.execute("DELETE FROM tutor_books WHERE id = %s AND user_id = %s", [book_id, user.id])
            deleted = cur.rowcount

        if not deleted:
            return Response({'error': 'Libro no encontrado o sin permiso.'}, status=404)
        return Response({'message': 'Libro eliminado correctamente.'})


class AskStepView(APIView):
    """
    POST /api/tutor/ask_step/
    El robot del paso — busca en los libros del usuario y responde acotado al tema.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question         = request.data.get('question', '').strip()
        step_title       = request.data.get('step_title', '').strip()
        step_description = request.data.get('step_description', '').strip()
        goal_text        = request.data.get('goal_text', '').strip()

        if not question:
            return Response({'error': 'La pregunta es obligatoria.'}, status=400)

        user_id = request.user.id

        # Contexto del paso para enriquecer la búsqueda
        search_query = f"{step_title} {question}"
        query_embedding = embed_text(search_query)

        # Buscar en TODOS los libros del usuario
        source_label = None
        context      = None

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT tc.content, tc.page_num, tb.title, tb.subject,
                       1 - (tc.embedding <=> %s::vector) AS similarity
                FROM tutor_chunks tc
                JOIN tutor_books tb ON tb.id = tc.book_id
                WHERE tb.user_id = %s
                ORDER BY tc.embedding <=> %s::vector
                LIMIT 2
                """,
                [str(query_embedding), user_id, str(query_embedding)]
            )
            rows = cur.fetchall()

        # Solo usar RAG si la similitud es suficientemente alta
        if rows and float(rows[0][4]) > 0.4:
            context = '\n\n'.join([f"[{r[2]}, Pág. {r[1]}] {r[0]}" for r in rows])
            source_label = f"{rows[0][2]} — Pág. {rows[0][1]}"

            prompt = f"""El alumno está estudiando: "{step_title}"
Descripción del tema: {step_description}

Su pregunta es: "{question}"

Fragmentos relevantes de sus libros:
{context}

Respondé la pregunta basándote en estos fragmentos. Sé claro, empático y usá ejemplos simples."""

        else:
            # Sin libro relevante — respondé acotado al tema del paso
            prompt = f"""El alumno está estudiando: "{step_title}" (parte de: "{goal_text}")
Descripción: {step_description}

Su pregunta es: "{question}"

Respondé SOLO sobre este tema específico. Si no tenés certeza, decí "No tengo suficiente información sobre eso, pero puedo decirte que..." y orientalo. No inventes datos. Sé breve y claro."""

        try:
            payload = json.dumps({
                "model": "claude-fable-5",
                "max_tokens": 400,
                "system": TUTOR_SYSTEM,
                "messages": [{"role": "user", "content": prompt}],
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())

            answer = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    answer = block.get("text", "")
                    break

        except Exception as e:
            logger.error(f"Error Claude API en ask_step: {e}")
            return Response({'error': 'No se pudo generar la respuesta.'}, status=503)

        return Response({
            'answer': answer,
            'source': source_label,
        })
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        question = request.data.get('question', '').strip()
        if not question:
            return Response({'error': 'La pregunta es obligatoria.'}, status=400)

        # Embedding de la pregunta
        query_embedding = embed_text(question)

        # Buscar los 2 chunks más relevantes
        chunks = sp_search_chunks(book_id, query_embedding, limit=2)
        if not chunks:
            return Response({'error': 'No se encontraron fragmentos relevantes.'}, status=404)

        # Armar contexto
        context = '\n\n'.join([f"[Pág. {c['page_num']}] {c['content']}" for c in chunks])
        pages   = ', '.join([str(c['page_num']) for c in chunks])

        prompt = TUTOR_PROMPT.format(
            question=question,
            context=context,
            pages=pages,
        )

        # Llamar a Claude API
        try:
            payload = json.dumps({
                "model": "claude-fable-5",
                "max_tokens": 512,
                "system": TUTOR_SYSTEM,
                "messages": [{"role": "user", "content": prompt}],
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())

            answer = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    answer = block.get("text", "")
                    break

        except Exception as e:
            logger.error(f"Error Claude API en tutor: {e}")
            return Response({'error': 'No se pudo generar la respuesta.'}, status=503)

        return Response({
            'answer':  answer,
            'sources': [{'page': c['page_num'], 'similarity': round(float(c['similarity']), 3)} for c in chunks],
        })
