from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import json
import os

class Command(BaseCommand):
    help = "Exporta usuários normais (não superusers) para um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Caminho do arquivo de saída (.json)')
        parser.add_argument('--all', action='store_true', help='Exporta todos os usuários, incluindo superusers')
        parser.add_argument('--username', help='Exporta apenas o usuário especificado')

    def handle(self, *args, **options):
        filepath = options['filepath']
        User = get_user_model()
        if options.get('username'):
            qs = User.objects.filter(username=options['username'])
        elif options['all']:
            qs = User.objects.all()
        else:
            qs = User.objects.filter(is_superuser=False)
        payload = []
        for u in qs:
            payload.append({
                'username': u.username,
                'email': u.email,
                'is_active': u.is_active,
                'password': u.password,  # hash
            })
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f'Exportados {len(payload)} usuários para {filepath}'))