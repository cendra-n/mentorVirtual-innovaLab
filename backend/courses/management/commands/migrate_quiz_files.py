import glob
import json
import os
import re
from django.conf import settings
from django.utils.text import slugify
from courses.models import Module
from courses import db

DELETE_AFTER_MIGRATE = os.environ.get("DELETE_AFTER_MIGRATE") == "1"

media_root = getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR, "media"))
quiz_dir = os.path.join(media_root, "courses")
pattern = os.path.join(quiz_dir, "quiz_*.json")

# Mapeo de IDs locales conocidos (de la base de datos de desarrollo de Gerardo)
# a títulos reales/estables de módulos.
OLD_ID_TO_TITLE = {
    2: "Módulo 1: Primeros Pasos en Ciberseguridad — ¿Qué es y por qué me importa?",
    3: "Módulo 2: Engaños Frecuentes en Internet y Cómo Proteger sus Datos",
    5: "Módulo 1: WhatsApp básico",
    7: "Módulo 1: Primeros Pasos en Ciberseguridad — ¿Qué es y por qué me importa?",
    8: "Módulo 2: Engaños Frecuentes en Internet y Cómo Proteger sus Datos",
}

def find_target_module(filename):
    """
    Intenta buscar el módulo correspondiente en la base de datos por:
    1. Mapeo de ID antiguo (si el archivo es quiz_modulo_<id>.json)
    2. Slug del nombre del archivo (si es quiz_<slug>.json)
    3. Fallback directo por ID si existe en la base de datos actual.
    """
    # 1. Caso de archivos con IDs numéricos locales
    match_id = re.match(r"quiz_modulo_(\d+)\.json$", filename)
    if match_id:
        old_id = int(match_id.group(1))
        # Buscar en el mapeo estable
        if old_id in OLD_ID_TO_TITLE:
            title = OLD_ID_TO_TITLE[old_id]
            # Buscar por título en la base de datos
            for m in Module.objects.all():
                if slugify(m.title) == slugify(title):
                    return m
        
        # Fallback 2: Buscar si el ID existe directamente en esta DB
        m = Module.objects.filter(id=old_id).first()
        if m:
            return m

    # 2. Caso de archivos con slug directo en el nombre, ej: quiz_<slug>.json
    match_slug = re.match(r"quiz_(.+)\.json$", filename)
    if match_slug:
        file_slug = slugify(match_slug.group(1).replace("modulo_", ""))
        for m in Module.objects.all():
            if slugify(m.title) == file_slug or file_slug in slugify(m.title):
                return m

    return None

migrated = 0
skipped = 0
errors = []

for filepath in glob.glob(pattern):
    filename = os.path.basename(filepath)
    
    # Resolver a qué módulo de la DB actual pertenece el archivo
    module = find_target_module(filename)
    if not module:
        print(f"[SKIP] {filename}: No se pudo asociar a ningún módulo en la base de datos")
        skipped += 1
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        if not isinstance(quiz_data, list) or not quiz_data:
            print(f"[SKIP] {filename}: formato inesperado o vacío")
            skipped += 1
            continue

        # Guardar en la base de datos utilizando la función idempotente
        db.save_module_quiz(module.id, quiz_data)
        migrated += 1
        print(f"[OK] Mapeado exitoso: {filename} -> Módulo '{module.title}' (ID {module.id})")

        if DELETE_AFTER_MIGRATE:
            os.remove(filepath)
            print(f"      archivo borrado: {filepath}")

    except Exception as e:
        errors.append((filename, str(e)))
        print(f"[ERROR] {filename}: {e}")

print("\n── Resumen de Semillado de Quizzes ────────────────────────")
print(f"Migrados exitosamente: {migrated}")
print(f"Omitidos: {skipped}")
print(f"Errores encontrados:  {len(errors)}")
if errors:
    for fn, err in errors:
        print(f"  - {fn}: {err}")
if not DELETE_AFTER_MIGRATE and migrated > 0:
    print(
        "\nLos archivos originales NO se borraron. Verificá los datos "
        "en la tabla module_quiz y corré de nuevo con "
        "DELETE_AFTER_MIGRATE=1 para limpiar el disco si lo deseas."
    )
