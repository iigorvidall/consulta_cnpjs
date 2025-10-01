// Frontend da página Home: submissão, controle de job (iniciar/pause/resume/cancel),
// alternância de abas, créditos e modal de detalhes. Não depende de frameworks.
// Abas Consulta/Configurações
const btnAbaConsulta = document.getElementById('btn-aba-consulta');
const abaConsulta = document.getElementById('aba-consulta');
// Aba de configurações removida; sempre mostrar aba de consulta
abaConsulta.style.display = '';
btnAbaConsulta.classList.add('active');

// Controles de delay removidos (delay fixo no backend)
const cnpjInput = document.getElementById('cnpjs');
// Ao digitar, remove caracteres não numéricos, exceto vírgula e espaço
cnpjInput.addEventListener('input', function(e) {
    let val = cnpjInput.value;
    // Permite números, vírgula e espaço
    val = val.replace(/[^0-9,\s]/g, '');
    cnpjInput.value = val;
});
// Ao colar, remove caracteres não numéricos, exceto vírgula e espaço
cnpjInput.addEventListener('paste', function(e) {
    e.preventDefault();
    let text = (e.clipboardData || window.clipboardData).getData('text');
    text = text.replace(/[^0-9,\s]/g, '');
    document.execCommand('insertText', false, text);
});
let retryInterval = null;
// CSRF helpers
function getCSRFToken() {
    // Prefer hidden input from Django form
    const inp = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (inp && inp.value) return inp.value;
    // Fallback to cookie (if cookie storage is enabled)
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
}
// Define a animação de entrada uma única vez para evitar reprocessos/reflows múltiplos
function ensureRowAnimStyle() {
    if (document.getElementById('ignea-row-anim-style')) return;
    const style = document.createElement('style');
    style.id = 'ignea-row-anim-style';
    style.textContent = `
.ignea-row-fade-right {
    /* não setamos opacity/transform aqui para evitar flash ao finalizar */
    animation: igneaFadeRightIn 0.7s cubic-bezier(.4,.2,.2,1) forwards;
    will-change: transform, opacity;
}
@keyframes igneaFadeRightIn {
    from { opacity: 0; transform: translateX(60px); }
    to { opacity: 1; transform: none; }
}
`;
    document.head.appendChild(style);
}
const btnBuscar = document.getElementById('btn-buscar');
const btnPausar = document.getElementById('btn-pausar');
const btnRetomar = document.getElementById('btn-retomar');
const btnCancelar = document.getElementById('btn-cancelar');
const formContainer = document.querySelector('.ignea-container');
function collapseFormCard() { if (formContainer) formContainer.classList.add('is-compact'); }
function expandFormCard() { if (formContainer) formContainer.classList.remove('is-compact'); }
// Botão de seta para recolher/expandir manualmente o card
const toggleCardBtn = document.getElementById('btn-toggle-card');
if (toggleCardBtn && formContainer) {
    toggleCardBtn.addEventListener('click', () => {
        formContainer.classList.toggle('is-compact');
    });
}
let loopActive = false, paused = false, cancelled = false;
document.getElementById('consultaForm').addEventListener('submit', async function(e) {
    const cnpjs = cnpjInput.value.trim();
    const csv = document.getElementById('csv_file').files.length;
    const errorMsg = document.getElementById('error-msg');
    errorMsg.style.display = 'none';
    errorMsg.textContent = '';
    if (!cnpjs && !csv) {
        errorMsg.textContent = 'Preencha o campo de CNPJ(s) ou envie um arquivo CSV.';
        errorMsg.style.display = 'block';
        e.preventDefault();
        return;
    }
    // Validação extra: se CNPJ preenchido, só aceita números, vírgulas e espaços
    if (cnpjs && !/^[0-9,\s,]+$/.test(cnpjs)) {
        errorMsg.textContent = 'O campo CNPJ(s) só pode conter números, vírgulas e espaços.';
        errorMsg.style.display = 'block';
        e.preventDefault();
        return;
    }
    // A partir deste ponto, o fluxo utiliza chamadas AJAX sequenciais (polling simples)
    e.preventDefault();
    // removido texto de loading; apenas progresso é exibido
    btnBuscar.disabled = true;
    btnPausar.style.display = '';
    btnRetomar.style.display = 'none';
    btnCancelar.style.display = '';
    paused = false; cancelled = false; loopActive = true;
    // colapsa o card para dar mais espaço à tabela
    collapseFormCard();
    const tbody = document.querySelector('#tab-resultado tbody');
    // Limpa tabela para nova execução
    tbody.innerHTML = '';
    // Usa o indicador de progresso dentro da barra de ações (mesma linha dos botões)
    let progressEl = document.getElementById('progress-indicator');
    if (!progressEl) {
        progressEl = document.createElement('div');
        progressEl.id = 'progress-indicator';
        progressEl.style.fontWeight = 'bold';
        document.getElementById('actions-bar').appendChild(progressEl);
    }

    // 1) Start job
    let startResp;
    const csrfToken = getCSRFToken();
    if (csv > 0) {
        const formData = new FormData();
        formData.append('csv_file', document.getElementById('csv_file').files[0]);
        startResp = await fetch('/jobs/start/', { method: 'POST', body: formData, credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
    } else {
        startResp = await fetch('/jobs/start/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify({ cnpjs })
        });
    }
    if (!startResp.ok) {
        const err = await startResp.json().catch(() => ({}));
        errorMsg.textContent = err.detail || 'Falha ao iniciar o processamento.';
    errorMsg.style.display = 'block';
        return;
    }
    const startData = await startResp.json();
    const total = startData.total || 0;
    progressEl.textContent = `Progresso: 0/${total}`;

    // 2) Loop de passos
    let processed = 0;
    while (loopActive && !cancelled && processed < total) {
        if (paused) { await new Promise(r => setTimeout(r, 800)); continue; }
    const stepResp = await fetch('/jobs/step/', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
        if (!stepResp.ok) break;
        const stepData = await stepResp.json();
    if (stepData.status === 'paused') { paused = true; btnPausar.style.display = 'none'; btnRetomar.style.display = ''; expandFormCard(); continue; }
        if (stepData.status === 'cancelled') { cancelled = true; loopActive = false; break; }
        if (stepData.status === 'done') { processed = stepData.processed; progressEl.textContent = `Progresso: ${processed}/${total}`; break; }
        if (stepData.item) {
            processed = stepData.processed;
            const r = stepData.item;
            const tr = document.createElement('tr');
            const email = (!r.email || r.email === '-') ? 'Sem e-mail' : r.email;
            const cnpjVal = r.cnpj || '-';
            tr.innerHTML = `
                <td style="padding:8px;">${r.processo || ''}</td>
                <td style="padding:8px;">${cnpjVal}</td>
                <td style=\"padding:8px;\">${r.dsevento || ''}</td>
                <td style=\"padding:8px;\">${r.oportunidade || ''}</td>
                <td style=\"padding:8px;\">${r.substancias || ''}</td>
                <td style="padding:8px;">${r.nome || '-'}</td>
                <td style="padding:8px;">${email}</td>
                <td style="padding:8px; text-align:center;">
                    <button class=\"btn-icon btn-details\" data-cnpj=\"${cnpjVal}\" title=\"Ver detalhes\" style=\"background:transparent; border:1px solid var(--ignea-brown); border-radius:6px; width:28px; height:28px; display:inline-grid; place-items:center; color:inherit;\"> 
                        <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n                            <rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"3\" ry=\"3\"></rect>\n                            <line x1=\"12\" y1=\"10\" x2=\"12\" y2=\"16\"></line>\n                            <line x1=\"12\" y1=\"7\" x2=\"12.01\" y2=\"7\"></line>\n                        </svg>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
            // Garante CSS da animação (definido uma única vez)
            ensureRowAnimStyle();
            // Dispara animação de entrada
            tr.classList.add('ignea-row-fade-right');
            // Limpa a classe ao término da animação sem "piscadas"
            tr.addEventListener('animationend', () => {
                tr.classList.remove('ignea-row-fade-right');
            }, { once: true });
            progressEl.textContent = `Progresso: ${processed}/${total}`;
// CSS da animação já é injetado por ensureRowAnimStyle()
        }
    }
    // sem indicador de loading textual
    btnBuscar.disabled = false;
    btnPausar.style.display = 'none';
    btnRetomar.style.display = 'none';
    btnCancelar.style.display = 'none';
    // Finaliza job: persiste no histórico (sem recarregar a página)
    try {
        if (!cancelled) {
            const resp = await fetch('/jobs/finalize/', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
            if (resp.ok) {
            // Mostra mensagem sutil de sucesso sem apagar a tabela
            let doneEl = document.getElementById('done-indicator');
            if (!doneEl) {
                doneEl = document.createElement('div');
                doneEl.id = 'done-indicator';
                doneEl.style.marginTop = '8px';
                doneEl.style.color = 'var(--ignea-brown)';
                doneEl.style.fontWeight = 'bold';
                document.getElementById('consultaForm').appendChild(doneEl);
            }
                doneEl.textContent = 'Processamento concluído e salvo no histórico.';
                // Atualiza créditos após finalizar o lote
                try { await loadCredits(true); } catch (e2) {}
                // mantém compacto após finalizar para priorizar resultados
                collapseFormCard();
            }
        }
    } catch (e) {
        console.error('Falha ao salvar histórico:', e);
    }
});
// Controles: Pausar/Retomar/Cancelar
btnPausar.addEventListener('click', async () => {
    const csrfToken = getCSRFToken();
    await fetch('/jobs/pause/', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
    paused = true; btnPausar.style.display = 'none'; btnRetomar.style.display = ''; expandFormCard();
});
btnRetomar.addEventListener('click', async () => {
    const csrfToken = getCSRFToken();
    await fetch('/jobs/resume/', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
    paused = false; btnRetomar.style.display = 'none'; btnPausar.style.display = ''; collapseFormCard();
});
btnCancelar.addEventListener('click', async () => {
    cancelled = true; loopActive = false;
    const csrfToken = getCSRFToken();
    await fetch('/jobs/cancel/', { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': csrfToken } });
    // sem indicador de loading textual
    btnBuscar.disabled = false;
    btnPausar.style.display = 'none'; btnRetomar.style.display = 'none'; btnCancelar.style.display = 'none';
    // ao cancelar, expande para permitir nova entrada
    expandFormCard();
    let doneEl = document.getElementById('done-indicator');
    if (!doneEl) {
        doneEl = document.createElement('div');
        doneEl.id = 'done-indicator';
        doneEl.style.marginTop = '8px';
        doneEl.style.color = '#d32f2f';
        doneEl.style.fontWeight = 'bold';
        document.getElementById('consultaForm').appendChild(doneEl);
    }
    doneEl.textContent = 'Processamento cancelado pelo usuário.';
    doneEl.style.color = 'var(--ignea-brown)';
});
// Limpa polling ao sair da página
window.addEventListener('beforeunload', function() {
    if (retryInterval) clearInterval(retryInterval);
});
// Função para exibir status de retry (será chamada pelo backend via websocket ou polling futuramente)
function showRetryStatus(msg) {
    const statusDiv = document.getElementById('status-indicator');
    statusDiv.textContent = msg;
    statusDiv.style.display = '';
    statusDiv.style.color = 'var(--ignea-brown)';
}

// Créditos CNPJÁ (mostra apenas o total: transient + perpetual). Sem botão, discreto no card.
async function loadCredits(forceRefresh = false) {
    const content = document.getElementById('credits-inline-content');
    if (!content) return;
    try {
        const url = forceRefresh ? '/api/creditos/?refresh=1' : '/api/creditos/';
        const resp = await fetch(url);
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (data && typeof data === 'object') {
            // Preferimos os campos "transient" e "perpetual"; caímos para outros se necessário
            const transientRaw = data.transient ?? data.monthlyCredits ?? data.monthly ?? data.month ?? data.mensal;
            const perpetualRaw = data.perpetual ?? data.permanentCredits ?? data.permanent ?? data.perm ?? data.permanentes;
            const t1 = transientRaw != null ? Number(transientRaw) : null;
            const t2 = perpetualRaw != null ? Number(perpetualRaw) : null;
            if (typeof t1 === 'number' && !Number.isNaN(t1) && typeof t2 === 'number' && !Number.isNaN(t2)) {
                content.textContent = String(t1 + t2);
            } else if (typeof data.total === 'number') {
                content.textContent = String(data.total);
            } else if (typeof data.totalCredits === 'number') {
                content.textContent = String(data.totalCredits);
            } else {
                content.textContent = '—';
            }
        } else {
            content.textContent = '—';
        }
    } catch (e) {
        const content2 = document.getElementById('credits-inline-content');
        if (content2) content2.textContent = '—';
    }
}
// Carrega créditos mesmo se DOM já estiver pronto
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => { loadCredits(false); });
} else {
    try { loadCredits(false); } catch (e) {}
}
// Alternância de abas Resultado/Histórico
const btnResultado = document.getElementById('btn-resultado');
const btnHistorico = document.getElementById('btn-historico');
const formLimpar = document.getElementById('form-limpar-historico');
btnResultado.onclick = function() {
    document.getElementById('tab-resultado').style.display = '';
    document.getElementById('tab-historico').style.display = 'none';
    this.classList.add('active');
    btnHistorico.classList.remove('active');
    if (formLimpar) formLimpar.style.display = 'none';
};
btnHistorico.onclick = function() {
    document.getElementById('tab-resultado').style.display = 'none';
    document.getElementById('tab-historico').style.display = '';
    this.classList.add('active');
    btnResultado.classList.remove('active');
    if (formLimpar) formLimpar.style.display = '';
};
// Exibe botão se já estiver na aba histórico ao carregar
window.addEventListener('DOMContentLoaded', function() {
    if (btnHistorico.classList.contains('active') && formLimpar) {
        formLimpar.style.display = '';
    }
});

// Helpers
function formatCNPJ(cnpj) {
    const d = (cnpj || '').replace(/\D/g, '').padStart(14, '0');
    return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}
function formatCurrencyBRL(n) {
    if (n == null || n === '' || isNaN(Number(n))) return '—';
    try { return Number(n).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }); } catch { return String(n); }
}
function esc(str){ return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])); }

async function openDetailsModalForCNPJ(cnpj) {
    const modal = document.getElementById('details-modal');
    const body = document.getElementById('details-body');
    const title = document.getElementById('details-title');
    title.textContent = `Detalhes: ${formatCNPJ(cnpj)}`;
    body.innerHTML = `<div class="muted">Carregando...</div>`;
    modal.style.display = 'flex';
    try {
        // Tenta obter dados já salvos na página (resultados/histórico)
        let data = null;
        // Busca na tabela de resultados
        const resRows = document.querySelectorAll('#tab-resultado tbody tr');
        for (const tr of resRows) {
            const cnpjCell = tr.children && tr.children[1] ? (tr.children[1].textContent || '').replace(/\D/g, '') : '';
            if (cnpjCell === cnpj) {
                break;
            }
        }
  
        let resp = await fetch(`/api/detalhes/${cnpj}/`);
        if (!resp.ok) {
            // Fallback: consulta direta (mantido como rede de segurança)
            resp = await fetch(`/cnpj/${cnpj}/`);
        }
        if (!resp.ok) throw new Error('HTTP '+resp.status);
        data = await resp.json();
        // Extract highlights
        const updated = data.updated ? new Date(data.updated).toLocaleString('pt-BR') : '—';
        const taxId = data.taxId || cnpj;
        const company = data.company || {}; 
        const name = company.name || '—';
        const equity = formatCurrencyBRL(company.equity);
        const nature = (company.nature && company.nature.text) ? company.nature.text : '—';
        const size = (company.size && (company.size.acronym || company.size.text)) ? `${company.size.acronym||''} ${company.size.text||''}`.trim() : '—';
        const alias = data.alias || '—';
        const founded = data.founded || '—';
        const status = (data.status && data.status.text) ? data.status.text : '—';
        const head = (data.head === true) ? 'Matriz' : (data.head === false ? 'Filial' : '—');
    const mainActText = (data.mainActivity && data.mainActivity.text) ? data.mainActivity.text : null;
    const mainActId = (data.mainActivity && data.mainActivity.id != null) ? String(data.mainActivity.id) : null;
    const mainAct = (mainActId || mainActText) ? `${esc(mainActId||'')} ${mainActText ? (mainActId?'- ':'')+esc(mainActText): ''}`.trim() : '—';
        const addr = data.address || {};
        const addressLine = [addr.street, addr.number, addr.district].filter(Boolean).join(', ');
    const cityLine = [addr.city, addr.state, addr.zip].filter(Boolean).join(' - ');
    const countryName = (addr.country && addr.country.name) ? addr.country.name : null;
    // Prefer the city name for municipality display; fall back to numeric IBGE code only if city is unavailable
    const municipalityName = addr.city ? String(addr.city) : null;
    const municipalityCode = (addr.municipality != null) ? String(addr.municipality) : null;
    const details = addr.details ? String(addr.details) : null;
    const emails = Array.isArray(data.emails) ? data.emails.map(e => e.address).filter(Boolean) : [];
    const phones = Array.isArray(data.phones) ? data.phones.map(p => `${p.type ? p.type+': ' : ''}${p.area||''} ${p.number||''}`.trim()).filter(Boolean) : [];
    const side = Array.isArray(data.sideActivities) ? data.sideActivities.map(a => `${a.id!=null? a.id+' - ' : ''}${a.text||''}`.trim()).filter(Boolean) : [];
    const statusDate = data.statusDate || null;
    const members = (company && Array.isArray(company.members)) ? company.members : [];

    let html = '';
    html += `<div class="line"><strong style="font-size:16px;">${esc(name)}</strong></div>`;
    html += `<div class="kv"><strong>CNPJ:</strong> ${esc(formatCNPJ(taxId))}</div>`;
    html += `<div class="kv"><strong>Atualizado:</strong> ${esc(updated)}</div>`;
    html += `<div class="kv"><strong>Capital:</strong> ${esc(equity)}</div>`;
    html += `<div class="kv"><strong>Natureza:</strong> ${esc(nature)}</div>`;
    html += `<div class="kv"><strong>Porte:</strong> ${esc(size)}</div>`;
    html += `<div class="kv"><strong>Apelido:</strong> ${esc(alias)}</div>`;
    html += `<div class="kv"><strong>Fundação:</strong> ${esc(founded)}</div>`;
        html += `<div class=\"kv\"><strong>Situação:</strong> ${esc(status)}</div>`;
        if (statusDate) html += `<div class=\"kv\"><strong>Data da Situação:</strong> ${esc(statusDate)}</div>`;
    html += `<div class="kv"><strong>Tipo:</strong> ${esc(head)}</div>`;
    html += `<div class="kv"><strong>Atividade Principal:</strong> ${esc(mainAct)}</div>`;
        if (addressLine || cityLine) html += `<div class=\"kv\"><strong>Endereço:</strong> ${esc(addressLine)}${addressLine && cityLine ? ' - ' : ''}${esc(cityLine)}</div>`;
        if (details) html += `<div class=\"kv\"><strong>Complemento:</strong> ${esc(details)}</div>`;
        if (municipalityName) {
            html += `<div class=\"kv\"><strong>Município:</strong> ${esc(municipalityName)}</div>`;
        } else if (municipalityCode) {
            html += `<div class=\"kv\"><strong>Município (IBGE):</strong> ${esc(municipalityCode)}</div>`;
        }
        if (countryName) html += `<div class=\"kv\"><strong>País:</strong> ${esc(countryName)}</div>`;
    if (emails.length) html += `<div class="kv"><strong>E-mails:</strong> ${esc(emails.join(' | '))}</div>`;
    if (phones.length) html += `<div class="kv"><strong>Telefones:</strong> ${esc(phones.join(' | '))}</div>`;
    if (side.length) html += `<div class="kv"><strong>Atividades Secundárias:</strong> ${esc(side.join(' | '))}</div>`;
        if (members && members.length) {
            html += `<div class=\"kv\"><strong>Administradores:</strong></div>`;
            html += `<ul class=\"kv-list\">`;
            for (const m of members) {
                const since = m.since || '—';
                const roleText = (m.role && m.role.text) ? m.role.text : '—';
                const personName = (m.person && m.person.name) ? m.person.name : '—';
                const ageBand = (m.person && m.person.age) ? m.person.age : null;
                const type = (m.person && m.person.type) ? m.person.type : null;
                const extra = [type, ageBand].filter(Boolean).join(', ');
                html += `<li>${esc(roleText)} — ${esc(personName)} (desde ${esc(since)}${extra?'; '+esc(extra):''})</li>`;
            }
            html += `</ul>`;
        }
        body.innerHTML = html;
    } catch (err) {
        body.innerHTML = `<div class="muted">Falha ao carregar detalhes (${esc(err.message)})</div>`;
    }
}

// Close modal
document.getElementById('modal-close').addEventListener('click', () => {
    document.getElementById('details-modal').style.display = 'none';
});
document.getElementById('details-modal').addEventListener('click', (e) => {
    if (e.target && e.target.id === 'details-modal') {
        document.getElementById('details-modal').style.display = 'none';
    }
});

// Event delegation for details buttons (results and history)
function setupDelegatesAndFilters(){
    const resultsTbody = document.querySelector('#tab-resultado tbody');
    const histTbody = document.querySelector('#tab-historico tbody');
    function delegateHandler(e) {
        const btn = e.target.closest('.btn-details');
        if (!btn) return;
        const cnpj = (btn.getAttribute('data-cnpj') || '').replace(/\D/g, '');
        if (cnpj.length === 14) openDetailsModalForCNPJ(cnpj);
    }
    if (resultsTbody) resultsTbody.addEventListener('click', delegateHandler);
    if (histTbody) histTbody.addEventListener('click', delegateHandler);

    // ----------------- Filtro dinâmico (Resultados e Histórico) -----------------
    function normalizeDigits(s){ return (s||'').replace(/\D/g,''); }
    function normalizeText(s){ return (s||'').toString().toLowerCase(); }
    function normalizeProcesso(s){
        const d = normalizeDigits(s);
        if (d.length === 10) return `${d.slice(0,3)}.${d.slice(3,6)}/${d.slice(6)}`;
        const m = (s||'').match(/\b\d{3}\.\d{3}\/\d{4}\b/);
        return m ? m[0] : s || '';
    }

    function filterTable(tbody, field, term) {
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const raw = term || '';
        const text = normalizeText(raw);
        const digits = normalizeDigits(raw);
        const procMask = normalizeProcesso(raw);
        // Map col index per table layout
        // Resultado: [Processo(0), CNPJ(1), DSEvento(2), OPORTUNIDADE(3), Substâncias(4), Nome(5), Email(6), Detalhes(7)]
        // Histórico: [Data(0), Processo(1), CNPJ(2), DSEvento(3), OPORTUNIDADE(4), Substâncias(5), Nome(6), Email(7), Detalhes(8)]
        const map = tbody.closest('#tab-resultado')
            ? { processo:0, cnpj:1, dsevento:2, oportunidade:3, substancias:4, nome:5, email:6 }
            : { processo:1, cnpj:2, dsevento:3, oportunidade:4, substancias:5, nome:6, email:7 };
        const idx = map[field] ?? map['cnpj'];
        let visible = 0;
        rows.forEach(tr => {
            const cell = tr.children[idx];
            if (!cell) { tr.style.display = ''; return; }
            const cellText = (cell.textContent || '');
            let ok = true;
            if (text) {
                if (field === 'cnpj') {
                    ok = normalizeDigits(cellText).includes(digits);
                } else if (field === 'processo') {
                    // comparar tanto com máscara quanto só dígitos
                    const cd = normalizeDigits(cellText);
                    ok = cd.includes(digits) || (cellText.includes(procMask));
                } else {
                    ok = normalizeText(cellText).includes(text);
                }
            }
            tr.style.display = ok ? '' : 'none';
            if (ok) visible++;
        });
        // Atualiza contador
        const counterId = tbody.closest('#tab-resultado') ? 'res-count' : 'his-count';
        const el = document.getElementById(counterId);
        if (el) el.textContent = `${visible}/${rows.length}`;
    }

    // Resultados
    const resField = document.getElementById('res-search-field');
    const resInput = document.getElementById('res-search-input');
    if (resField && resInput && resultsTbody) {
        const apply = () => filterTable(resultsTbody, resField.value, resInput.value);
        resInput.addEventListener('input', apply);
        resField.addEventListener('change', apply);
        // inicializa contador
        apply();
    }

    // Histórico
    const hisField = document.getElementById('his-search-field');
    const hisInput = document.getElementById('his-search-input');
    if (hisField && hisInput && histTbody) {
        const applyH = () => filterTable(histTbody, hisField.value, hisInput.value);
        hisInput.addEventListener('input', applyH);
        hisField.addEventListener('change', applyH);
        // inicializa contador
        applyH();
    }
}

// Garante inicialização mesmo se DOMContentLoaded já ocorreu
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupDelegatesAndFilters);
} else {
    setupDelegatesAndFilters();
}