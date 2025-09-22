from django.http import JsonResponse
from django.shortcuts import render
from .models import ConsultaHistorico
import logging
from django.http import HttpResponse
from .services import clean_cnpj, format_cnpj, consultar_cnpj_api, processar_csv, processar_xlsx, exportar_csv, exportar_xlsx, processar_cnpjs_manualmente

def status_retry(request):
	status = request.session.get('status_retry', '')
	return JsonResponse({'status': status})

def home(request):
	error_msg = None
	resultados = []
	historico = ConsultaHistorico.objects.order_by('-data')[:30]
	if request.method == 'POST':
		if request.POST.get('limpar_historico') == '1':
			ConsultaHistorico.objects.all().delete()
			historico = []
			context = {'resultados': [], 'historico': historico, 'msg': 'Histórico apagado com sucesso!'}
			return render(request, 'consulta/home.html', context)
		logger = logging.getLogger('consulta')
		cnpjs = request.POST.get('cnpjs', '').strip()
		csv_file = request.FILES.get('csv_file')
		delay = request.POST.get('delay')
		try:
			delay = float(delay)
			if delay < 0.1:
				delay = 0.1
		except Exception:
			delay = 0.5
		tipo = None
		cnpjs_registro = ''

		def on_retry(attempt, wait):
			pass  # Não altera a mensagem, mantém 'Processando...'

		if cnpjs:
			tipo = 'manual'
			cnpj_list, resultados = processar_cnpjs_manualmente(cnpjs, delay=delay, on_retry=on_retry)
			cnpjs_registro = ','.join(cnpj_list)
		elif csv_file:
			tipo = 'upload'
			if csv_file.name.lower().endswith('.csv'):
				try:
					resultados = processar_csv(csv_file, logger=logger, delay=delay, on_retry=on_retry)
				except Exception as e:
					error_msg = f'Erro ao processar o arquivo: {str(e)}'
			elif csv_file.name.lower().endswith('.xlsx'):
				try:
					resultados = processar_xlsx(csv_file, logger=logger, delay=delay, on_retry=on_retry)
				except Exception as e:
					error_msg = f'Erro ao processar o arquivo: {str(e)}'
			else:
				error_msg = 'O arquivo enviado deve ser um CSV ou XLSX.'
		# Limpa status de retry ao fim do processamento
		request.session['status_retry'] = ''
		# Salvar histórico se houver resultados
		if (tipo and (resultados or error_msg)):
			ConsultaHistorico.objects.create(
				tipo=tipo,
				cnpjs=cnpjs_registro,
				arquivo_nome=csv_file.name if tipo == 'upload' and csv_file else None,
				resultado=resultados if resultados else {'erro': error_msg}
			)
		# Salvar resultados atuais na sessão para exportação
		request.session['ultimos_resultados'] = resultados
	context = {'resultados': resultados, 'historico': historico}
	if error_msg:
		context['error_msg'] = error_msg
	return render(request, 'consulta/home.html', context)


def export_resultado_csv(request):
	resultados = request.session.get('ultimos_resultados', [])
	csv_data = exportar_csv(resultados)
	response = HttpResponse(csv_data, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="resultado.csv"'
	return response


def export_resultado_xlsx(request):
	resultados = request.session.get('ultimos_resultados', [])
	xlsx_data = exportar_xlsx(resultados)
	response = HttpResponse(xlsx_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename="resultado.xlsx"'
	return response


def export_historico_csv(request):
	historico = ConsultaHistorico.objects.order_by('-data')
	resultados = []
	for h in historico:
		for r in h.resultado:
			r_cpy = r.copy()
			r_cpy['data'] = h.data.strftime('%d/%m/%Y %H:%M')
			resultados.append(r_cpy)
	csv_data = exportar_csv(resultados, include_data=True)
	response = HttpResponse(csv_data, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="historico.csv"'
	return response


def export_historico_xlsx(request):
	historico = ConsultaHistorico.objects.order_by('-data')
	resultados = []
	for h in historico:
		for r in h.resultado:
			r_cpy = r.copy()
			r_cpy['data'] = h.data.strftime('%d/%m/%Y %H:%M')
			resultados.append(r_cpy)
	xlsx_data = exportar_xlsx(resultados, include_data=True)
	response = HttpResponse(xlsx_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename="historico.xlsx"'
	return response
