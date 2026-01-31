# 🧠 RUFFUS V2 - Guia de Setup

Ruffus é dividido em **dois ambientes isolados**:

1. **RUFFUS (Cripto/Bybit)** - Python Global
2. **RUFFUS-BINARY (Bullex)** - Virtual Environment

---

## 🚀 Setup Rápido

### **1. Ruffus (Global - Cripto/Bybit)**

```powershell
# Opção A: Usar script automático
.\setup_ruffus.ps1

# Opção B: Manual
pip install -r requirements.txt
python main.py
```

**Requisitos:**
- Python 3.10+ instalado e no PATH
- Acesso à internet para pip install

**Portas:**
- Web API: `http://127.0.0.1:8000`

---

### **2. Ruffus Binary (VirtualEnv - Bullex)**

```powershell
# Opção A: Usar script automático
.\setup_binary.ps1

# Opção B: Manual
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m apps.ruffus_binary
```

**Requisitos:**
- Python 3.10+ com módulo `venv`

**Portas:**
- Web API: `http://127.0.0.1:8001`

---

## 📦 Dependências

### Ruffus (Global)
```
pybit==5.13.0          # Bybit API
fastapi==0.109.0       # Web Framework
uvicorn==0.27.0        # ASGI Server
python-multipart==0.0.6
```

### Ruffus Binary (VirtualEnv)
Mesmo `requirements.txt` (compartilhado)

---

## 🔧 Troubleshooting

### **"ModuleNotFoundError: No module named 'pybit'"**
```powershell
# Ruffus Global
pip install -r requirements.txt

# Ruffus Binary
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### **"Permission denied: 'setup_ruffus.ps1'"**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_ruffus.ps1
```

### **Porta já em uso (8000 ou 8001)**
Modifique em:
- Ruffus: `main.py` linha ~93 (porta 8000)
- Ruffus Binary: `apps/ruffus_binary.py` linha ~18 (porta 8001)

---

## 📁 Estrutura

```
RUFFUS_V2/
├── .venv/              # Virtual env (apenas Ruffus Binary)
├── adapters/           # Brokers (bybit.py, virtual.py)
├── apps/               # Entry points (ruffus_binary.py)
├── brokers/            # Integrações (bullex.py, bullex_api.py)
├── core/               # Motor principal (engine.py, risk.py)
├── strategies/         # Lógica de decisão
│   ├── canonical/      # Estratégias cripto (Bybit)
│   └── binary/         # Estratégias binárias (Bullex)
├── storage/            # Persistência de dados
├── tools/              # Utilitários (feedback, memory, web)
├── main.py             # Entry point Ruffus (Global)
├── requirements.txt    # Dependências (compartilhadas)
├── setup_ruffus.ps1    # Setup script Ruffus
└── setup_binary.ps1    # Setup script Ruffus Binary
```

---

## 🎯 Próximos Passos

- [ ] Validar Ruffus em modo `VIRTUAL` (sem execução real)
- [ ] Configurar credenciais Bybit em variáveis de ambiente
- [ ] Testar Ruffus Binary em modo `ASSISTED`
- [ ] Implementar `buy()` e `sell()` reais em `adapters/bybit.py`

---

**Versão:** 2.0 Estável | **Data:** 31 de janeiro de 2026
