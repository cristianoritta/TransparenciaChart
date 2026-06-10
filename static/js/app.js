const SERVICE_COLORS = {
    "pessoa-fisica": "blue",
    "servidores": "indigo",
    "servidores-remuneracao": "indigo",
    "peps": "red",
    "viagens": "teal",
    "contratos": "purple",
    "permissionarios": "orange",
    "cartoes": "orange",
    "recursos-recebidos": "purple",
    "documentos-empenho": "green",
    "documentos-liquidacao": "green",
    "documentos-pagamento": "orange",
    "ceis": "red",
    "cnep": "red",
    "ceaf": "red",
    "bolsa-familia": "green",
    "auxilio-emergencial": "teal",
    "bpc": "purple",
    "seguro-defeso": "teal",
    "garantia-safra": "green",
    "peti": "indigo",
};

const SERVICE_ICONS = {
    default: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>',
    "pessoa-fisica": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    viagens: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>',
    "documentos-liquidacao": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "documentos-pagamento": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>',
    "recursos-recebidos": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>',
};

const form = document.getElementById("search-form");
const cpfInput = document.getElementById("cpf-input");
const cpfClear = document.getElementById("cpf-clear");
const searchBtn = document.getElementById("search-btn");
const alertBox = document.getElementById("alert");
const modalOverlay = document.getElementById("modal-overlay");
const modalClose = document.getElementById("modal-close");
const configForm = document.getElementById("config-form");

function formatCpf(value) {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
    if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
    return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

cpfInput.addEventListener("input", () => {
    cpfInput.value = formatCpf(cpfInput.value);
    cpfClear.classList.toggle("hidden", !cpfInput.value);
});

cpfClear.addEventListener("click", () => {
    cpfInput.value = "";
    cpfClear.classList.add("hidden");
    cpfInput.focus();
});

function showAlert(message) {
    alertBox.textContent = message;
    alertBox.className = "alert error";
    alertBox.classList.remove("hidden");
}

function hideAlert() {
    alertBox.classList.add("hidden");
}

function setBtnLoading(btn, loading) {
    btn.disabled = loading;
    btn.querySelector(".btn-text")?.classList.toggle("hidden", loading);
    btn.querySelector(".btn-loader")?.classList.toggle("hidden", !loading);
}

function formatLabel(key) {
    return key.replace(/([A-Z])/g, " $1").replace(/^./, (s) => s.toUpperCase()).trim();
}

function formatValue(value) {
    if (value === null || value === undefined) return "—";
    if (typeof value === "boolean") return value ? "Sim" : "Não";
    if (typeof value === "object") return JSON.stringify(value, null, 2);
    return String(value);
}

function renderObjectData(data) {
    const grid = document.createElement("div");
    grid.className = "kv-grid";
    Object.entries(data).forEach(([key, value]) => {
        const item = document.createElement("div");
        item.className = "kv-item";
        item.innerHTML = `<div class="kv-key">${formatLabel(key)}</div><div class="kv-value${typeof value === "boolean" ? (value ? " true" : " false") : ""}">${formatValue(value)}</div>`;
        grid.appendChild(item);
    });
    return grid;
}

function renderListData(data) {
    const wrapper = document.createElement("div");
    data.forEach((record, index) => {
        const block = document.createElement("div");
        block.className = "record-block";
        block.innerHTML = `<div class="record-title">Registro ${index + 1}</div>`;
        if (typeof record === "object" && record !== null) {
            block.appendChild(renderObjectData(record));
        } else {
            block.appendChild(document.createTextNode(formatValue(record)));
        }
        wrapper.appendChild(block);
    });
    return wrapper;
}

function openModal(result) {
    document.getElementById("modal-category").textContent = result.categoria;
    document.getElementById("modal-title").textContent = result.nome;
    document.getElementById("modal-desc").textContent = result.descricao;
    const body = document.getElementById("modal-body");
    body.innerHTML = "";
    if (Array.isArray(result.dados)) {
        body.appendChild(renderListData(result.dados));
    } else if (typeof result.dados === "object" && result.dados !== null) {
        body.appendChild(renderObjectData(result.dados));
    }
    modalOverlay.classList.remove("hidden");
}

function closeModal() {
    modalOverlay.classList.add("hidden");
}

modalClose.addEventListener("click", closeModal);
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) closeModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

function renderServiceCard(result) {
    const color = SERVICE_COLORS[result.id] || "blue";
    const icon = SERVICE_ICONS[result.id] || SERVICE_ICONS.default;
    const card = document.createElement("div");
    card.className = "service-card";
    card.innerHTML = `
        <div class="service-icon ${color}">${icon}</div>
        <div class="service-info">
            <strong>${result.nome}</strong>
            <span>${result.descricao}</span>
        </div>
        <span class="service-count ${color}">${result.total} registro${result.total !== 1 ? "s" : ""}</span>
        <span class="service-chevron">›</span>
    `;
    card.addEventListener("click", () => openModal(result));
    return card;
}

function renderResults(data) {
    hideAlert();

    document.getElementById("profile-nome").textContent = data.nome || "Não informado";
    document.getElementById("profile-cpf").textContent = `CPF: ${data.cpf_mascarado || data.cpf}`;
    document.getElementById("profile-date").textContent = `Última consulta: ${data.consultado_em || "—"}`;

    document.getElementById("metric-servicos").textContent = data.total_positivos;
    document.getElementById("metric-registros").textContent = data.total_registros || 0;
    document.getElementById("metric-categorias").textContent = data.categorias || 0;

    document.getElementById("profile-card").classList.remove("hidden");
    document.getElementById("metrics").classList.remove("hidden");

    const grid = document.getElementById("services-grid");
    grid.innerHTML = "";

    if (data.total_positivos === 0) {
        document.getElementById("services-section").classList.add("hidden");
        document.getElementById("empty-section").classList.remove("hidden");
        return;
    }

    document.getElementById("empty-section").classList.add("hidden");
    document.getElementById("services-section").classList.remove("hidden");
    data.resultados.forEach((r) => grid.appendChild(renderServiceCard(r)));
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    const cpf = cpfInput.value.replace(/\D/g, "");
    if (cpf.length !== 11) {
        showAlert("Informe um CPF válido com 11 dígitos.");
        return;
    }

    setBtnLoading(searchBtn, true);
    document.getElementById("profile-card").classList.add("hidden");
    document.getElementById("metrics").classList.add("hidden");
    document.getElementById("services-section").classList.add("hidden");
    document.getElementById("empty-section").classList.add("hidden");

    try {
        const response = await fetch("/api/buscar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cpf }),
        });
        const data = await response.json();
        if (data.erro) {
            showAlert(data.erro);
            if (data.erro.includes("Configurações")) navigateTo("configuracoes");
            return;
        }
        renderResults(data);
    } catch {
        showAlert("Erro ao consultar a API. Verifique sua conexão.");
    } finally {
        setBtnLoading(searchBtn, false);
    }
});

function navigateTo(page) {
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    document.querySelectorAll(".nav-item[data-page]").forEach((n) => n.classList.remove("active"));
    document.getElementById(`page-${page}`)?.classList.add("active");
    document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add("active");
    if (page === "historico") loadHistorico();
    if (page === "configuracoes") loadConfig();
}

document.querySelectorAll(".nav-item[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => navigateTo(btn.dataset.page));
});

async function loadHistorico() {
    const list = document.getElementById("historico-list");
    const empty = document.getElementById("historico-empty");
    list.innerHTML = "";

    try {
        const res = await fetch("/api/historico");
        const data = await res.json();
        if (!data.consultas.length) {
            empty.classList.remove("hidden");
            return;
        }
        empty.classList.add("hidden");
        data.consultas.forEach((c) => {
            const item = document.createElement("div");
            item.className = "historico-item";
            const dataFmt = new Date(c.criado_em).toLocaleString("pt-BR");
            item.innerHTML = `
                <div>
                    <h4>${c.nome || "Sem nome"}</h4>
                    <p>CPF: ${c.cpf_mascarado} · ${dataFmt}</p>
                </div>
                <div class="historico-meta">
                    <span><strong>${c.total_positivos}</strong> serviços</span>
                    <span><strong>${c.total_registros}</strong> registros</span>
                </div>
            `;
            item.addEventListener("click", () => loadHistoricoDetalhe(c.id));
            list.appendChild(item);
        });
    } catch {
        empty.classList.remove("hidden");
    }
}

async function loadHistoricoDetalhe(id) {
    try {
        const res = await fetch(`/api/historico/${id}`);
        const data = await res.json();
        if (data.erro) return;
        navigateTo("consulta");
        renderResults(data.resultado);
        if (data.resultado.cpf) {
            cpfInput.value = formatCpf(data.resultado.cpf);
            cpfClear.classList.remove("hidden");
        }
    } catch { /* silencioso */ }
}

async function loadConfig() {
    try {
        const res = await fetch("/api/configuracoes");
        const data = await res.json();
        document.getElementById("api-header").value = data.api_header || "chave-api-dados";
        const status = document.getElementById("api-key-status");
        if (data.api_key_configurada) {
            status.textContent = `Chave configurada: ${data.api_key_mascarada}`;
            status.className = "ok";
        } else {
            status.textContent = "Nenhuma chave configurada.";
            status.className = "";
        }
    } catch { /* silencioso */ }
}

configForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("config-save-btn");
    const apiKey = document.getElementById("api-key").value.trim();
    const apiHeader = document.getElementById("api-header").value.trim();

    if (!apiKey) {
        showAlert("Informe a chave da API.");
        return;
    }

    setBtnLoading(btn, true);
    try {
        const res = await fetch("/api/configuracoes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_key: apiKey, api_header: apiHeader }),
        });
        const data = await res.json();
        if (data.erro) {
            showAlert(data.erro);
            return;
        }
        document.getElementById("api-key").value = "";
        const status = document.getElementById("api-key-status");
        status.textContent = `Chave salva: ${data.api_key_mascarada}`;
        status.className = "ok";
        hideAlert();
    } catch {
        showAlert("Erro ao salvar configurações.");
    } finally {
        setBtnLoading(btn, false);
    }
});

document.getElementById("theme-toggle").addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.dataset.theme === "dark" ? "light" : "dark";
    html.dataset.theme = next;
    localStorage.setItem("ui-theme", next);
});

const savedTheme = localStorage.getItem("ui-theme") || "light";
document.documentElement.dataset.theme = savedTheme;
loadConfig();
