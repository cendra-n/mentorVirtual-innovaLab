"""
Capa de datos para el tutor RAG.
Sin ORM — solo stored procedures y queries directas con pgvector.
"""
import json
from django.db import connection


def sp_create_book(user_id: int, title: str, subject: str, filename: str) -> int:
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO tutor_books (user_id, title, subject, filename) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            [user_id, title, subject, filename]
        )
        return cur.fetchone()[0]


def sp_save_chunk(book_id: int, content: str, page_num: int, embedding: list) -> int:
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO tutor_chunks (book_id, content, page_num, embedding) "
            "VALUES (%s, %s, %s, %s::vector) RETURNING id",
            [book_id, content, page_num, str(embedding)]
        )
        return cur.fetchone()[0]


def sp_get_books(user_id: int) -> list[dict]:
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id, title, subject, filename, created_at, "
            "(SELECT COUNT(*) FROM tutor_chunks WHERE book_id = tutor_books.id) as chunks "
            "FROM tutor_books WHERE user_id = %s ORDER BY created_at DESC",
            [user_id]
        )
        rows = cur.fetchall()
    cols = ['id', 'title', 'subject', 'filename', 'created_at', 'chunks']
    return [dict(zip(cols, r)) for r in rows]


def sp_delete_book(book_id: int, user_id: int) -> bool:
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM tutor_books WHERE id = %s AND user_id = %s",
            [book_id, user_id]
        )
        return cur.rowcount > 0


def sp_search_chunks(book_id: int, query_embedding: list, limit: int = 2) -> list[dict]:
    """
    Busca los chunks más similares usando cosine similarity con pgvector.
    Devuelve los `limit` chunks más relevantes.
    """
    with connection.cursor() as cur:
        cur.execute(
            "SELECT content, page_num, "
            "1 - (embedding <=> %s::vector) AS similarity "
            "FROM tutor_chunks "
            "WHERE book_id = %s "
            "ORDER BY embedding <=> %s::vector "
            "LIMIT %s",
            [str(query_embedding), book_id, str(query_embedding), limit]
        )
        rows = cur.fetchall()
    cols = ['content', 'page_num', 'similarity']
    return [dict(zip(cols, r)) for r in rows]
