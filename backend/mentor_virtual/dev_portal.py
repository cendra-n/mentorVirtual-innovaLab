from django.http import HttpResponse


def developer_portal(request):
    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mentor Virtual — Developer Portal</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    :root {
      --azul: #336ACC; --marino: #101E37; --teal: #005E7A;
      --verde: #26874A; --gris: #F3F6F9; --borde: #E6EBF0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; background: var(--gris); color: var(--marino); }
    header { background: var(--marino); padding: 28px 40px; display: flex; align-items: center; gap: 16px; }
    header h1 { color: white; font-size: 22px; font-weight: 800; }
    header p  { color: #8fafd6; font-size: 13px; margin-top: 2px; }
    .badge { background: var(--azul); color: white; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 50px; margin-left: 8px; }
    main { max-width: 860px; margin: 40px auto; padding: 0 24px; }
    h2 { font-size: 18px; font-weight: 800; color: var(--marino); margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 40px; }
    .card { background: white; border: 1px solid var(--borde); border-radius: 12px; padding: 24px; text-decoration: none; color: var(--marino); transition: all .2s; display: block; }
    .card:hover { box-shadow: 0 4px 20px rgba(16,30,55,.12); transform: translateY(-2px); }
    .card-icon { font-size: 32px; margin-bottom: 12px; }
    .card h3 { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
    .card p  { font-size: 12.5px; color: #666; line-height: 1.5; }
    .endpoints { background: white; border: 1px solid var(--borde); border-radius: 12px; overflow: hidden; margin-bottom: 40px; }
    .ep-group { border-bottom: 1px solid var(--borde); }
    .ep-group:last-child { border-bottom: none; }
    .ep-group-title { padding: 14px 20px; background: var(--gris); font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #666; }
    .ep-row { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-top: 1px solid var(--borde); font-size: 13px; }
    .method { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; width: 52px; text-align: center; flex-shrink: 0; }
    .get    { background: #dbeafe; color: #1d4ed8; }
    .post   { background: #dcfce7; color: #15803d; }
    .delete { background: #fee2e2; color: #b91c1c; }
    .patch  { background: #fef9c3; color: #854d0e; }
    .ep-url { font-family: monospace; font-size: 12px; color: var(--marino); flex: 1; }
    .ep-desc { font-size: 12px; color: #666; }
    .auth-badge { font-size: 10px; background: #f3f6f9; border: 1px solid var(--borde); padding: 2px 7px; border-radius: 50px; color: #666; flex-shrink: 0; }
    .auth-badge.staff { background: #fef3c7; border-color: #fcd34d; color: #92400e; }
    footer { text-align: center; padding: 32px; color: #999; font-size: 12px; border-top: 1px solid var(--borde); margin-top: 20px; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Mentor Virtual Adaptativo <span class="badge">v1.0</span></h1>
      <p>Developer Portal — API REST Documentation</p>
    </div>
  </header>

  <main>
    <h2>Documentación interactiva</h2>
    <div class="grid">
      <a href="/api/schema/swagger-ui/" class="card">
        <div class="card-icon">📋</div>
        <h3>Swagger UI</h3>
        <p>Explorá y probá todos los endpoints directamente desde el browser con autenticación JWT.</p>
      </a>
      <a href="/api/schema/redoc/" class="card">
        <div class="card-icon">📖</div>
        <h3>ReDoc</h3>
        <p>Documentación legible y navegable de todos los endpoints, parámetros y respuestas.</p>
      </a>
      <a href="/api/schema/" class="card">
        <div class="card-icon">⚙️</div>
        <h3>OpenAPI Schema</h3>
        <p>Schema en formato JSON/YAML para importar en Postman, Insomnia o cualquier cliente REST.</p>
      </a>
    </div>

    <h2>Referencia rápida de endpoints</h2>
    <div class="endpoints">

      <div class="ep-group">
        <div class="ep-group-title">🔐 Autenticación</div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/auth/register/</span><span class="ep-desc">Crear cuenta nueva</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/auth/login/</span><span class="ep-desc">Login → access + refresh token</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/auth/token/refresh/</span><span class="ep-desc">Renovar access token</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/auth/logout/</span><span class="ep-desc">Cerrar sesión</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/auth/me/</span><span class="ep-desc">Datos del usuario actual</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/auth/change_password/</span><span class="ep-desc">Cambiar contraseña</span><span class="auth-badge">JWT</span></div>
      </div>

      <div class="ep-group">
        <div class="ep-group-title">🎯 Metas y Planes IA</div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/goals/</span><span class="ep-desc">Listar metas del usuario</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/goals/create/</span><span class="ep-desc">Crear meta → genera plan con IA + videos YouTube</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/goals/&lt;id&gt;/</span><span class="ep-desc">Detalle: pasos + videos + logros</span><span class="auth-badge">JWT</span></div>
      </div>

      <div class="ep-group">
        <div class="ep-group-title">📈 Progreso y Gamificación</div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/progress/steps/&lt;id&gt;/complete/</span><span class="ep-desc">Completar un paso</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/progress/videos/&lt;id&gt;/view/</span><span class="ep-desc">Registrar video visto</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/progress/goals/&lt;id&gt;/</span><span class="ep-desc">Progreso de una meta</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/progress/streak/</span><span class="ep-desc">Racha de días activos</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/progress/logros/</span><span class="ep-desc">Logros del usuario</span><span class="auth-badge">JWT</span></div>
      </div>

      <div class="ep-group">
        <div class="ep-group-title">🤖 Tutor RAG (PDF + Embeddings)</div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/tutor/books/</span><span class="ep-desc">Listar libros subidos</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/tutor/books/</span><span class="ep-desc">Subir y procesar PDF (multipart/form-data)</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method delete">DELETE</span><span class="ep-url">/api/tutor/books/&lt;id&gt;/</span><span class="ep-desc">Eliminar libro y sus chunks</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/tutor/books/&lt;id&gt;/ask/</span><span class="ep-desc">Preguntar sobre un libro específico</span><span class="auth-badge">JWT</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/tutor/ask_step/</span><span class="ep-desc">Robot tutor por paso — busca en todos los libros</span><span class="auth-badge">JWT</span></div>
      </div>

      <div class="ep-group">
        <div class="ep-group-title">⚙️ Panel de Administración</div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/admin/users/</span><span class="ep-desc">Listar todos los usuarios</span><span class="auth-badge staff">Staff</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/admin/users/&lt;id&gt;/</span><span class="ep-desc">Detalle de un usuario</span><span class="auth-badge staff">Staff</span></div>
        <div class="ep-row"><span class="method patch">PATCH</span><span class="ep-url">/api/admin/users/&lt;id&gt;/</span><span class="ep-desc">Activar / desactivar usuario</span><span class="auth-badge staff">Staff</span></div>
        <div class="ep-row"><span class="method post">POST</span><span class="ep-url">/api/admin/users/&lt;id&gt;/set_password/</span><span class="ep-desc">Cambiar contraseña de usuario</span><span class="auth-badge staff">Staff</span></div>
        <div class="ep-row"><span class="method get">GET</span><span class="ep-url">/api/admin/stats/</span><span class="ep-desc">Estadísticas generales de la plataforma</span><span class="auth-badge staff">Staff</span></div>
      </div>

    </div>
  </main>

  <footer>
    Mentor Virtual Adaptativo v1.0 &nbsp;·&nbsp; Django REST Framework &nbsp;·&nbsp; drf-spectacular
  </footer>
</body>
</html>"""
    return HttpResponse(html)
