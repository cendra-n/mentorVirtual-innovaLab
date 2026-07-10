"""
migrate_quiz_files_to_db.py

Migración one-shot: si ya hay cursos generados con la versión vieja
(archivos media/courses/quiz_modulo_<id>.json en disco), este script
los vuelca a la tabla module_quiz y opcionalmente borra los archivos.

Uso (dentro del contenedor backend, con Django ya configurado):

    docker compose exec backend python manage.py shell < migrate_quiz_files_to_db.py

O como management command si preferís (copiarlo a
courses/management/commands/migrate_quiz_files.py y ajustar el shebang
de Django).

Por seguridad, NO borra los archivos automáticamente — solo lo hace si
corrés con DELETE_AFTER_MIGRATE=1 en el entorno, para poder verificar
antes de eliminar el rastro en disco.
"""
import glob
import json
import os
import re

from django.conf import settings

from courses import db

DELETE_AFTER_MIGRATE = os.environ.get("DELETE_AFTER_MIGRATE") == "1"

media_root = getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR, "media"))
quiz_dir = os.path.join(media_root, "courses")
pattern = os.path.join(quiz_dir, "quiz_modulo_*.json")

migrated = 0
skipped = 0
errors = []

for filepath in glob.glob(pattern):
    filename = os.path.basename(filepath)
    match = re.match(r"quiz_modulo_(\d+)\.json$", filename)
    if not match:
        skipped += 1
        continue

    module_id = int(match.group(1))

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        if not isinstance(quiz_data, list) or not quiz_data:
            print(f"[SKIP] {filename}: formato inesperado o vacío")
            skipped += 1
            continue

        db.save_module_quiz(module_id, quiz_data)
        migrated += 1
        print(f"[OK] módulo {module_id} <- {filename}")

        if DELETE_AFTER_MIGRATE:
            os.remove(filepath)
            print(f"      archivo borrado: {filepath}")

    except Exception as e:
        errors.append((filename, str(e)))
        print(f"[ERROR] {filename}: {e}")

print("\n── Resumen ──────────────────────────────────────────────")
print(f"Migrados: {migrated}")
print(f"Omitidos: {skipped}")
print(f"Errores:  {len(errors)}")
if errors:
    for fn, err in errors:
        print(f"  - {fn}: {err}")
if not DELETE_AFTER_MIGRATE and migrated > 0:
    print(
        "\nLos archivos originales NO se borraron. Verificá los datos "
        "en la tabla module_quiz y corré de nuevo con "
        "DELETE_AFTER_MIGRATE=1 para limpiar el disco."
    )
