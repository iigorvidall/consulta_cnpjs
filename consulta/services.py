import re
import requests
import csv
import io
import time
import openpyxl
import xlsxwriter
from django.conf import settings

def processar_cnpjs_manualmente(cnpjs: str, delay=0.5, on_retry=None):
    cnpj_list = [clean_cnpj(c) for c in cnpjs.split(',') if clean_cnpj(c)]
    resultados = []
    for cnpj in cnpj_list:
        resultado = consultar_cnpj_api(cnpj, on_retry=on_retry)
        resultados.append(resultado)
        time.sleep(delay)
    return cnpj_list, resultados

def clean_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

def format_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def consultar_cnpj_api(cnpj, retry_count=3, retry_wait=20, on_retry=None):
    for attempt in range(retry_count):
        resp = requests.get(f'https://open.cnpja.com/office/{cnpj}', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            nome = data.get('company', {}).get('name', '-')
            email = '-'
            emails = data.get('emails', [])
            if emails and isinstance(emails, list):
                email = emails[0].get('address', '-')
            return {
                'cnpj': format_cnpj(cnpj),
                'nome': nome,
                'email': email
            }
        elif resp.status_code == 429:
            if on_retry:
                on_retry(attempt+1, retry_wait)
            time.sleep(retry_wait)
        else:
            return {
                'cnpj': format_cnpj(cnpj),
                'nome': '-',
                'email': f'API retornou status {resp.status_code}: {resp.text[:200]}'
            }
    return {
        'cnpj': format_cnpj(cnpj),
        'nome': '-',
        'email': 'API retornou status 429: Limite de requisições excedido após múltiplas tentativas.'
    }

def processar_csv(file, logger=None, delay=0.5, on_retry=None):
    decoded = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    cnpj_keys = ['cnpj', 'CNPJ', 'CNPJ/CPF', 'cnpj_cpf']
    resultados = []
    for row in reader:
        cnpj_val = None
        for key in row:
            if not cnpj_val and any(k.lower() in key.lower() for k in cnpj_keys):
                original = row[key]
                cnpj_val = clean_cnpj(original).strip()
                if logger:
                    logger.info(f"Linha CSV: '{original}' -> CNPJ limpo: '{cnpj_val}'")
        if cnpj_val:
            try:
                if logger:
                    logger.info(f'Consultando CNPJ (CSV): {cnpj_val}')
                resultado = consultar_cnpj_api(cnpj_val, on_retry=on_retry)
                resultados.append(resultado)
            except Exception as e:
                if logger:
                    logger.error(f'Erro ao consultar CNPJ {cnpj_val}: {e}')
                resultados.append({'cnpj': format_cnpj(cnpj_val), 'nome': '-', 'email': f'Erro: {str(e)}'})
            time.sleep(delay)
    return resultados

def processar_xlsx(file, logger=None, delay=0.5, on_retry=None):
    wb = openpyxl.load_workbook(file, read_only=True)
    ws = wb.active
    headers = [str(cell.value).strip() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    cnpj_keys = ['cnpj', 'CNPJ', 'CNPJ/CPF', 'cnpj_cpf']
    cnpj_idx = None
    for idx, h in enumerate(headers):
        if cnpj_idx is None and any(k.lower() in h.lower() for k in cnpj_keys):
            cnpj_idx = idx
    if cnpj_idx is None:
        raise Exception('Coluna de CNPJ não encontrada no arquivo XLSX.')
    resultados = []
    for row in ws.iter_rows(min_row=2):
        cnpj_val = clean_cnpj(str(row[cnpj_idx].value) if row[cnpj_idx].value else '')
        if cnpj_val:
            try:
                resultado = consultar_cnpj_api(cnpj_val, on_retry=on_retry)
                resultados.append(resultado)
            except Exception as e:
                resultados.append({'cnpj': format_cnpj(cnpj_val), 'nome': '-', 'email': f'Erro: {str(e)}'})
            time.sleep(delay)
    return resultados

def exportar_csv(resultados, include_data=False):
    output = io.StringIO()
    writer = csv.writer(output)
    if include_data:
        writer.writerow(['Data', 'CNPJ', 'Nome', 'E-mail'])
        for r in resultados:
            writer.writerow([
                r.get('data', ''),
                r.get('cnpj', ''),
                r.get('nome', ''),
                r.get('email', '')
            ])
    else:
        writer.writerow(['CNPJ', 'Nome', 'E-mail'])
        for r in resultados:
            writer.writerow([r.get('cnpj', ''), r.get('nome', ''), r.get('email', '')])
    return output.getvalue()

def exportar_xlsx(resultados, include_data=False):
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet('Export')
    if include_data:
        ws.write_row(0, 0, ['Data', 'CNPJ', 'Nome', 'E-mail'])
        for idx, r in enumerate(resultados, 1):
            ws.write_row(idx, 0, [r.get('data', ''), r.get('cnpj', ''), r.get('nome', ''), r.get('email', '')])
    else:
        ws.write_row(0, 0, ['CNPJ', 'Nome', 'E-mail'])
        for idx, r in enumerate(resultados, 1):
            ws.write_row(idx, 0, [r.get('cnpj', ''), r.get('nome', ''), r.get('email', '')])
    wb.close()
    output.seek(0)
    return output.read()
