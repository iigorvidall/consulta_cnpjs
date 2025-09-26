"""Modelos de persistência da app 'consulta'.

- ConsultaHistorico: snapshot dos resultados e metadados de cada execução.
- ProcessEntry/ProcessResult: modelos auxiliares (não usados diretamente na UI principal).
"""

from django.db import models

class ConsultaHistorico(models.Model):
    """Registro de uma execução (manual/upload) com resultados serializados."""
    TIPO_CHOICES = (
        ('manual', 'Manual'),
        ('upload', 'Upload'),
    )
    data = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cnpjs = models.TextField(blank=True, null=True, help_text="CNPJs consultados (manual ou lista do arquivo)")
    arquivo_nome = models.CharField(max_length=255, blank=True, null=True)
    resultado = models.JSONField()

    def __str__(self):
        return f"{self.data:%d/%m/%Y %H:%M} - {self.tipo}"

class ProcessEntry(models.Model):
    """Linha de entrada de processamento (ex.: processo associado a um CNPJ)."""
    processo = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=20)
    nome = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.processo} - {self.cnpj}"

class ProcessResult(models.Model):
    """Linha de resultado de processamento com contato extraído."""
    processo = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=20)
    nome = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f"{self.processo} - {self.cnpj} - {self.email}"


