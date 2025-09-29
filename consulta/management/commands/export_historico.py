from django.core.management.base import BaseCommand
from consulta.models import ConsultaHistorico
from django.utils.timezone import is_naive, make_naive
from django.utils import timezone
import json
import os


class Command(BaseCommand):
    help = (
        "Exporta todos os registros de ConsultaHistorico para um arquivo JSON simples.\n"
        "Uso: python manage.py export_historico caminho/para/historico.json"
    )

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Caminho do arquivo de saída (.json)')

    def handle(self, *args, **options):
        filepath = options['filepath']
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        payload = []
        for h in ConsultaHistorico.objects.order_by('data'):
            dt = h.data
            if is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            # Serializa como ISO 8601 em UTC para portabilidade
            iso = dt.astimezone(timezone.utc).isoformat()
            payload.append({
                'data': iso,
                'tipo': h.tipo,
                'cnpjs': h.cnpjs,
                'arquivo_nome': h.arquivo_nome,
                'resultado': h.resultado,
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'Exportados {len(payload)} registros para {filepath}'))
