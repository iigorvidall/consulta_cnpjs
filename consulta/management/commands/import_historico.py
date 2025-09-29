from django.core.management.base import BaseCommand, CommandError
from consulta.models import ConsultaHistorico
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import json
import os


class Command(BaseCommand):
    help = (
        "Importa registros de ConsultaHistorico a partir de um arquivo JSON simples.\n"
        "Formato esperado: lista de objetos com campos: data (ISO opcional), tipo, cnpjs, arquivo_nome, resultado."
    )

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Caminho para o arquivo .json com os dados')
        parser.add_argument('--truncate', action='store_true', help='Apaga o histórico antes de importar')

    def handle(self, *args, **options):
        filepath = options['filepath']
        truncate = options['truncate']
        if not os.path.exists(filepath):
            raise CommandError(f"Arquivo não encontrado: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                payload = json.load(f)
            except Exception as e:
                raise CommandError(f"JSON inválido: {e}")

        if not isinstance(payload, list):
            raise CommandError('O JSON deve ser uma lista de objetos.')

        if truncate:
            ConsultaHistorico.objects.all().delete()
            self.stdout.write(self.style.WARNING('Histórico existente apagado.'))

        created = 0
        for item in payload:
            if not isinstance(item, dict):
                continue
            tipo = item.get('tipo') or 'manual'
            cnpjs = item.get('cnpjs')
            arquivo_nome = item.get('arquivo_nome')
            resultado = item.get('resultado') or []
            data_str = item.get('data')

            obj = ConsultaHistorico(
                tipo=tipo,
                cnpjs=cnpjs,
                arquivo_nome=arquivo_nome,
                resultado=resultado,
            )
            if data_str:
                dt = parse_datetime(data_str)
                if dt is not None:
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    obj.data = dt
            obj.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Importação concluída. Registros criados: {created}'))
