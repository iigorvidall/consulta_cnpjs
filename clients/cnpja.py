import os
from typing import Any, Dict, Optional
import requests

class CNPJAClientError(Exception):
    """Erro ao consultar a API PRO do CNPJÁ."""

class CNPJAClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("CNPJA_API_KEY")
        if not self.api_key:
            raise CNPJAClientError("CNPJA_API_KEY não configurada no ambiente.")
        self.base_url = (base_url or os.getenv("CNPJA_BASE_URL") or "https://api.cnpja.com").rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Consulta-CNPJ/1.0",
        }

    def get_office(
        self,
        cnpj: str,
        timeout: int = 15,
        strategy: Optional[str] = None,
        max_age_days: Optional[int] = None,
        max_stale_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        cnpj = "".join(filter(str.isdigit, cnpj))  # limpa CNPJ
        if len(cnpj) != 14:
            raise CNPJAClientError("CNPJ inválido. Deve conter 14 dígitos.")
        url = f"{self.base_url}/office/{cnpj}"
        params = {}
        if strategy:
            params["strategy"] = strategy
        if max_age_days is not None:
            params["maxAge"] = max_age_days
        if max_stale_days is not None:
            params["maxStale"] = max_stale_days
        resp = requests.get(url, headers=self._headers(), params=params, timeout=timeout)
        if resp.status_code != 200:
            detail = resp.text[:500]
            raise CNPJAClientError(f"Erro {resp.status_code} ao consultar CNPJ {cnpj}: {detail}")
        return resp.json()
