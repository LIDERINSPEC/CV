# Líder Inspeções · Gerador de CV · RH

App completo para o RH da Líder gerar CVs no padrão Quality Experts.

## Estrutura do Projeto

```
lider-cv-app/
├── frontend/
│   └── index.html        ← App do RH (sobe no Vercel)
├── backend/
│   ├── main.py           ← API FastAPI
│   ├── pdf_generator.py  ← Geração de PDF com ReportLab
│   ├── lider_logo.png    ← Logo da Líder (já incluído)
│   ├── requirements.txt  ← Dependências Python
│   └── Procfile          ← Configuração Railway
└── README.md
```

---

## Deploy em Produção — Passo a Passo

### Pré-requisitos
- Conta no [GitHub](https://github.com) (gratuita)
- Conta no [Railway](https://railway.app) (gratuita)
- Conta no [Vercel](https://vercel.com) (gratuita)
- Chave da [Anthropic API](https://console.anthropic.com)

---

### PASSO 1 — Subir o projeto no GitHub

1. Acesse [github.com](https://github.com) → New Repository
2. Nome: `lider-cv-app` → Create Repository
3. Faça upload de todos os arquivos desta pasta
   - Ou use Git: `git init && git add . && git commit -m "init" && git push`

---

### PASSO 2 — Backend no Railway

1. Acesse [railway.app](https://railway.app) → New Project
2. Clique em **Deploy from GitHub Repo**
3. Selecione o repositório `lider-cv-app`
4. Em **Root Directory**, coloque: `backend`
5. Em **Variables**, adicione:
   ```
   ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
   ```
6. Clique em **Deploy** — aguarde ~2 minutos
7. Vá em **Settings → Networking → Generate Domain**
8. Copie a URL gerada (ex: `https://lider-cv-app.up.railway.app`)

---

### PASSO 3 — Frontend no Vercel

1. Acesse [vercel.com](https://vercel.com) → New Project
2. Importe o repositório `lider-cv-app`
3. Em **Root Directory**, coloque: `frontend`
4. Clique em **Deploy** — aguarde ~1 minuto
5. Vercel gera uma URL (ex: `https://lider-cv.vercel.app`)

---

### PASSO 4 — Conectar Frontend ao Backend

1. Abra o app no Vercel: `https://lider-cv.vercel.app`
2. Clique em **Configurações** (sidebar)
3. Cole a URL do Railway no campo **URL do Backend**
4. Clique em **Testar conexão** — deve aparecer ✓ Online
5. Clique em **Salvar configurações**

---

### PASSO 5 — Testar

1. Clique em **Novo CV**
2. Cole um currículo bruto na caixa de texto
3. Clique em **Extrair com IA**
4. Aguarde os campos preenchidos automaticamente
5. Clique em **Gerar PDF Líder** — o PDF baixa automaticamente

---

## Como Usar

### Gerar um CV
1. **Novo CV** → Cole o currículo bruto
2. (Opcional) Cole o escopo da vaga para alinhar o perfil
3. **Extrair com IA** → revise os campos
4. **Gerar PDF Líder** → download automático

### Banco de Inspetores
- Todos os CVs gerados ficam salvos automaticamente
- Acesse **Banco de Inspetores** para ver, editar ou regerar
- **Exportar CSV** para relatórios de RH

---

## Custos Estimados

| Serviço | Custo |
|---------|-------|
| Vercel (frontend) | Grátis |
| Railway (backend) | Grátis até 500h/mês |
| Anthropic API | ~$0,01 por CV extraído |
| **Total** | **~R$ 0 a R$ 5/mês** |

---

## Suporte

Desenvolvido pela Líder Inspeções Quality Experts | ValueAddingPartners
