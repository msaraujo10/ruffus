# 🧠 Ruffus V2

Ruffus V2 é um framework de trading algorítmico com consciência operacional.

Ele não é apenas um “bot”. É um sistema vivo de mercado, capaz de:

- Manter estado real
- Observar a si mesmo
- Decidir com contexto
- Operar em múltiplos modos
- Persistir memória
- Expor seu estado em tempo real

Ruffus foi projetado para ser seguro, observável e evolutivo.

---

## Modos de Operação

| Modo        | Descrição |
|-------------|-----------|
| `VIRTUAL`   | Simulação e replay. Nenhuma ordem real. |
| `OBSERVADOR`| Conecta ao mercado sem executar ordens. |
| `ASSISTED`  | Propõe ações e aguarda confirmação humana. |
| `REAL`      | Opera autonomamente. |

A progressão natural é: `VIRTUAL → ASSISTED → REAL`.

---

## Arquitetura

```
Engine
 ├─ StateMachine
 ├─ World        (mercado)
 ├─ Strategy     (decisão)
 ├─ RiskManager  (blindagem)
 ├─ Broker       (execução)
 ├─ Store        (persistência)
 ├─ Feedback     (diagnóstico)
 └─ Panel / API  (observabilidade)
```

O `Engine` orquestra o ciclo:

> Mercado → Consciência → Decisão → Risco → Execução → Memória

---

## Observabilidade

Ruffus nunca é uma caixa-preta.

Ele oferece:

- Painel no terminal
- API viva (`/snapshot`)
- Dashboard no navegador

Exemplo de estado vivo:

```json
{
  "mode": "ASSISTED",
  "state": "IN_POSITION",
  "health": "OK",
  "intent": null
}
```

---

## Segurança

- Máquina de estados explícita
- Modo observador
- Modo assistido
- Gerenciamento de risco
- Estado `ERROR` isolado

Ruffus foi feito para falhar com dignidade.

---

## Execução

```bash
pip install fastapi uvicorn
python main.py
```

Abra:

```
http://127.0.0.1:8000/snapshot
```

---

Ruffus é um organismo algorítmico.

Ele não apenas executa ordens.

Ele observa, decide e evolui.

