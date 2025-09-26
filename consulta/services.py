"""Camada de serviços da app 'consulta'.

Responsabilidades principais:
- Sanitização e formatação de CNPJ.
- Integração com CNPJÁ PRO via `clients.cnpja.CNPJAClient` (com retry/backoff).
- Processamento de entradas CSV/XLSX e agregação dos resultados.
- Exportação em formatos CSV/XLSX.
"""

import re
import csv
import io
import time
import requests
import openpyxl
import xlsxwriter
from django.conf import settings
from clients.cnpja import CNPJAClient, CNPJAClientError

DELAY_SECONDS = 1  # Delay fixo entre consultas para respeitar limites de API e UX

def processar_cnpjs_manualmente(cnpjs: str, on_retry=None):
    """Processa uma string de CNPJs separados por vírgula sequencialmente.

    Retorna (lista_cnpjs_limpos, lista_resultados). Aplica DELAY_SECONDS entre chamadas.
    """
    cnpj_list = [clean_cnpj(c) for c in cnpjs.split(',') if clean_cnpj(c)]
    resultados = []
    for cnpj in cnpj_list:
        resultado = consultar_cnpj_api(cnpj, on_retry=on_retry)
        resultados.append(resultado)
        time.sleep(DELAY_SECONDS)
    return cnpj_list, resultados

def clean_cnpj(cnpj):
    """Remove todos os caracteres não numéricos do CNPJ."""
    return re.sub(r'\D', '', cnpj)

def format_cnpj(cnpj):
    """Formata um CNPJ 14 dígitos para 00.000.000/0000-00."""
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def consultar_cnpj_api(cnpj, retry_count=3, retry_wait=20, on_retry=None):
    """Consulta a API PRO do CNPJÁ com retry/backoff e extração resiliente de campos.

    - retry_count: tentativas para erros transitórios (429/timeout/connerror).
    - retry_wait: segundos de espera entre tentativas (backoff constante).
    - on_retry: callback opcional (attempt:int, wait:int) para feedback de UI.
    """
    client = CNPJAClient()
    clean = clean_cnpj(cnpj)
    for attempt in range(retry_count):
        try:
            data = client.get_office(
                clean,
                timeout=30,
                strategy=getattr(settings, 'CNPJA_STRATEGY', 'CACHE_IF_FRESH'),
                max_age_days=getattr(settings, 'CNPJA_MAX_AGE_DAYS', 14),
                max_stale_days=getattr(settings, 'CNPJA_MAX_STALE_DAYS', 30),
            )
            # Extração resiliente de nome e email a partir do payload da API PRO
            nome = (
                (data.get('company') or {}).get('name')
                or data.get('name')
                or '-'
            )
            email = 'Sem e-mail'
            emails = data.get('emails')
            if isinstance(emails, list) and emails:
                first = emails[0]
                if isinstance(first, dict):
                    email = first.get('address') or first.get('email') or 'Sem e-mail'
                elif isinstance(first, str):
                    email = first
            return {
                'cnpj': format_cnpj(clean),
                'nome': nome,
                'email': email,
                'detalhes': data
            }
        except CNPJAClientError as e:
            msg = str(e)
            # Se for rate limit, aguarda e tenta novamente
            if '429' in msg:
                if on_retry:
                    on_retry(attempt+1, retry_wait)
                time.sleep(retry_wait)
                continue
            return {
                'cnpj': format_cnpj(clean),
                'nome': '-',
                'email': f'Erro API PRO: {msg[:200]}',
                'detalhes': None
            }
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if on_retry:
                on_retry(attempt+1, retry_wait)
            time.sleep(retry_wait)
            continue
        except Exception as e:
            return {
                'cnpj': format_cnpj(clean),
                'nome': '-',
                'email': f'Erro inesperado: {str(e)[:200]}',
                'detalhes': None
            }
    return {
        'cnpj': format_cnpj(clean),
        'nome': '-',
        'email': 'Limite de tentativas excedido devido a rate limit (429).',
        'detalhes': None
    }

def processar_csv(file, logger=None, on_retry=None):
    """Lê um CSV, detecta colunas relevantes e consulta a API por linha.

    Aceita fallback por varredura dos campos quando o cabeçalho é inconsistente.
    Aplica DELAY_SECONDS entre chamadas.
    """
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    cnpj_keys = ['cnpj', 'CNPJ', 'CNPJ/CPF', 'cnpj_cpf']
    proc_keys = ['processo', 'Processo', 'número do processo', 'numero do processo']
    resultados = []
    for row in reader:
        cnpj_val = None
        proc_val = None
        for key in row:
            if not cnpj_val and any(k.lower() in key.lower() for k in cnpj_keys):
                original = row[key]
                cnpj_val = clean_cnpj(original).strip()
                if logger:
                    logger.info(f"Linha CSV: '{original}' -> CNPJ limpo: '{cnpj_val}'")
            if not proc_val and any(k.lower() in key.lower() for k in proc_keys):
                proc_val = (row[key] or '').strip()
        if cnpj_val:
            try:
                if logger:
                    logger.info(f'Consultando CNPJ (CSV): {cnpj_val}')
                resultado = consultar_cnpj_api(cnpj_val, on_retry=on_retry)
                resultado['processo'] = proc_val
                resultados.append(resultado)
            except Exception as e:
                if logger:
                    logger.error(f'Erro ao consultar CNPJ {cnpj_val}: {e}')
                resultados.append({'processo': proc_val, 'cnpj': format_cnpj(cnpj_val), 'nome': '-', 'email': f'Erro: {str(e)}', 'detalhes': None})
            time.sleep(DELAY_SECONDS)
    return resultados

def processar_xlsx(file, logger=None, on_retry=None):
    """Lê um XLSX (primeira planilha), detecta colunas e consulta API por linha."""
    wb = openpyxl.load_workbook(file, read_only=True)
    ws = wb.active
    headers = [str(cell.value).strip() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    cnpj_keys = ['cnpj', 'CNPJ', 'CNPJ/CPF', 'cnpj_cpf']
    proc_keys = ['processo', 'Processo', 'número do processo', 'numero do processo']
    cnpj_idx = None
    proc_idx = None
    for idx, h in enumerate(headers):
        if cnpj_idx is None and any(k.lower() in h.lower() for k in cnpj_keys):
            cnpj_idx = idx
        if proc_idx is None and any(k.lower() in h.lower() for k in proc_keys):
            proc_idx = idx
    if cnpj_idx is None:
        raise Exception('Coluna de CNPJ não encontrada no arquivo XLSX.')
    resultados = []
    for row in ws.iter_rows(min_row=2):
        cnpj_val = clean_cnpj(str(row[cnpj_idx].value) if row[cnpj_idx].value else '')
        proc_val = (str(row[proc_idx].value).strip() if (proc_idx is not None and row[proc_idx].value) else None)
        if cnpj_val:
            try:
                resultado = consultar_cnpj_api(cnpj_val, on_retry=on_retry)
                resultado['processo'] = proc_val
                resultados.append(resultado)
            except Exception as e:
                resultados.append({'processo': proc_val, 'cnpj': format_cnpj(cnpj_val), 'nome': '-', 'email': f'Erro: {str(e)}', 'detalhes': None})
            time.sleep(DELAY_SECONDS)
    return resultados

def exportar_csv(resultados, include_data=False):
    """Gera CSV em memória a partir da lista de resultados.

    Quando include_data=True, inclui a coluna Data (para histórico).
    """
    output = io.StringIO()
    writer = csv.writer(output)
    if include_data:
        writer.writerow(['Data', 'Processo', 'CNPJ', 'Nome', 'E-mail'])
        for r in resultados:
            writer.writerow([
                r.get('data', ''),
                r.get('processo', ''),
                r.get('cnpj', ''),
                r.get('nome', ''),
                r.get('email', '')
            ])
    else:
        writer.writerow(['Processo', 'CNPJ', 'Nome', 'E-mail'])
        for r in resultados:
            email = r.get('email', '')
            if email in ('', '-', None):
                email = 'Sem e-mail'
            writer.writerow([r.get('processo', ''), r.get('cnpj', ''), r.get('nome', ''), email])
    return output.getvalue()

def exportar_xlsx(resultados, include_data=False):
    """Gera XLSX em memória a partir da lista de resultados.

    Quando include_data=True, inclui a coluna Data (para histórico).
    """
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet('Export')
    if include_data:
        ws.write_row(0, 0, ['Data', 'Processo', 'CNPJ', 'Nome', 'E-mail'])
        for idx, r in enumerate(resultados, 1):
            ws.write_row(idx, 0, [r.get('data', ''), r.get('processo', ''), r.get('cnpj', ''), r.get('nome', ''), r.get('email', '')])
    else:
        ws.write_row(0, 0, ['Processo', 'CNPJ', 'Nome', 'E-mail'])
        for idx, r in enumerate(resultados, 1):
            email = r.get('email', '')
            if email in ('', '-', None):
                email = 'Sem e-mail'
            ws.write_row(idx, 0, [r.get('processo', ''), r.get('cnpj', ''), r.get('nome', ''), email])
    wb.close()
    output.seek(0)
    return output.read()
