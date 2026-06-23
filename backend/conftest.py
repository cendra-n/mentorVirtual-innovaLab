"""
conftest.py — Configuración global de pytest

Links en el reporte HTML:
- Cada test puede tener un link a Jira, GitHub Issues o cualquier gestor de tickets
- Se configura en JIRA_LINKS abajo — key = nombre del test, value = URL del ticket

Para agregar un link nuevo:
  1. Copiás el nombre exacto del test (sin el prefijo de clase)
  2. Agregás una entrada en JIRA_LINKS
  3. La próxima vez que corra el reporte HTML va a aparecer en la columna Links
"""

from pytest_html import extras

# ── Mapa de tests → tickets externos ─────────────────────────────────────────
# Reemplazá las URLs con las de tu Jira / GitHub Issues / Linear / Trello
JIRA_LINKS = {
    'test_api_register_success':                       'https://jira.tuempresa.com/browse/MV-101',
    'test_api_register_password_mismatch':             'https://jira.tuempresa.com/browse/MV-102',
    'test_api_register_weak_password':                 'https://jira.tuempresa.com/browse/MV-103',
    'test_api_register_duplicate_email':               'https://jira.tuempresa.com/browse/MV-104',
    'test_api_register_missing_fields':                'https://jira.tuempresa.com/browse/MV-105',
    'test_api_register_invalid_phone':                 'https://jira.tuempresa.com/browse/MV-106',
    'test_api_register_invalid_font_size':             'https://jira.tuempresa.com/browse/MV-107',
    'test_api_login_success':                          'https://jira.tuempresa.com/browse/MV-108',
    'test_api_login_invalid_credentials':              'https://jira.tuempresa.com/browse/MV-109',
    'test_api_login_missing_fields':                   'https://jira.tuempresa.com/browse/MV-110',
    'test_api_profile_unauthorized':                   'https://jira.tuempresa.com/browse/MV-111',
    'test_api_profile_get_success':                    'https://jira.tuempresa.com/browse/MV-112',
    'test_api_profile_update_put_success':             'https://jira.tuempresa.com/browse/MV-113',
    'test_api_profile_update_patch_success':           'https://jira.tuempresa.com/browse/MV-114',
    'test_api_profile_update_duplicate_email_blocked': 'https://jira.tuempresa.com/browse/MV-115',
    'test_api_users_list_success':                     'https://jira.tuempresa.com/browse/MV-116',
    'test_api_logout_success':                         'https://jira.tuempresa.com/browse/MV-117',
}


def pytest_runtest_makereport(item, call):
    """Hook que agrega el link al reporte HTML después de cada test."""
    pass


def pytest_html_results_table_row(report, cells):
    """Agrega el link en la columna Links del reporte HTML."""
    test_name = report.nodeid.split('::')[-1]
    url = JIRA_LINKS.get(test_name)
    if url:
        # Inserta el link en la celda Links
        cells.insert(-1, (f'<a href="{url}" target="_blank">🎫 Ticket</a>', ''))


def pytest_configure(config):
    """Registra el hook de la columna extra."""
    pass
