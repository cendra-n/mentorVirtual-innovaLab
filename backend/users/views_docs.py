from django.shortcuts import render

def developer_portal(request):
    """
    Vista del Portal de Desarrolladores.
    Renderiza el portal central con los enlaces a Swagger y ReDoc.
    """
    return render(request, 'users/developer_portal.html')
