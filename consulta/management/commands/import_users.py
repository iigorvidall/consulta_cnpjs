from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
import json
import os

class Command(BaseCommand):
    help = "Importa usuários normais de um arquivo JSON (username, email, password hash, ativo)."

    def add_arguments(self, parser):
        parser.add_argument('filepath', help='Caminho do arquivo .json com os dados')
        parser.add_argument('--truncate', action='store_true', help='Apaga todos os usuários antes de importar')

    def handle(self, *args, **options):
        filepath = options['filepath']
        truncate = options['truncate']
        User = get_user_model()
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
            User.objects.all().delete()
            self.stdout.write(self.style.WARNING('Todos os usuários apagados.'))
        created = 0
        for item in payload:
            if not isinstance(item, dict):
                continue
            username = item.get('username')
            email = item.get('email')
            password = item.get('password')  # hash
            is_active = item.get('is_active', True)
            if not username or not password:
                continue
            user, created_flag = User.objects.get_or_create(username=username, defaults={'email': email or ''})
            user.email = email or ''
            user.is_active = is_active
            user.password = password  # hash direto
            user.save()
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Importação concluída. Usuários criados/atualizados: {created}'))