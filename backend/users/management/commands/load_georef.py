import json
import urllib.request
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Country, Nationality, Province, Locality

class Command(BaseCommand):
    help = 'Precarga países, nacionalidades, provincias y localidades de Argentina usando la API oficial de GeoRef.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando la carga de datos geográficos desde GeoRef...'))
        base_url = settings.GEOREF_API_BASE_URL

        with transaction.atomic():
            country_arg, _ = Country.objects.get_or_create(
                country_name__iexact="Argentina",
                defaults={'country_name': "Argentina"}
            )
            self.stdout.write(self.style.SUCCESS(f' País verificado: {country_arg.country_name}'))

            nat_arg, _ = Nationality.objects.get_or_create(
                nationality_name__iexact="Argentina",
                defaults={'nationality_name': "Argentina"}
            )
            self.stdout.write(self.style.SUCCESS(f' Nacionalidad verificada: {nat_arg.nationality_name}'))

        provincias_url = f"{base_url}/provincias?campos=id,nombre&max=50"
        try:
            req = urllib.request.Request(provincias_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data_provincias = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' Error al conectar con GeoRef (Provincias): {str(e)}'))
            return

        provincias_list = data_provincias.get('provincias', [])
        self.stdout.write(f' Se encontraron {len(provincias_list)} provincias. Procesando localidades...')

        for prov_data in provincias_list:
            prov_nombre = prov_data['nombre']
            prov_georef_id = prov_data['id']  # ID interno de GeoRef para filtrar localidades

            # Guardamos la provincia en nuestra base de datos
            with transaction.atomic():
                prov_obj, created = Province.objects.get_or_create(
                    province_name__iexact=prov_nombre,
                    country=country_arg,
                    defaults={'province_name': prov_nombre}
                )
            
            status_prov = "Creada" if created else "Existente"
            self.stdout.write(f'   [Provincia] {prov_nombre} ({status_prov}) - Consultando localidades...')

            # Consultamos las localidades específicas de esta provincia (máximo 1000 por provincia)
            localidades_url = f"{base_url}/localidades?provincia={prov_georef_id}&campos=id,nombre&max=1000"
            try:
                req_loc = urllib.request.Request(localidades_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_loc) as response:
                    data_localidades = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'     Error al obtener localidades de {prov_nombre}: {str(e)}'))
                continue

            localidades_list = data_localidades.get('localidades', [])
            
            # Inserción segura dentro de un bloque transaccional para optimizar rendimiento
            with transaction.atomic():
                loc_count_nuevas = 0
                for loc_data in localidades_list:
                    loc_nombre = loc_data['nombre']
                    _, loc_created = Locality.objects.get_or_create(
                        locality_name__iexact=loc_nombre,
                        province=prov_obj,
                        defaults={'locality_name': loc_nombre}
                    )
                    if loc_created:
                        loc_count_nuevas += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'     {len(localidades_list)} localidades procesadas ({loc_count_nuevas} nuevas en BD).'
            ))

        self.stdout.write(self.style.SUCCESS('¡Carga de datos geográficos finalizada con éxito!'))