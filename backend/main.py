from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import anthropic
import json
import io
import os

from pdf_generator import gerar_pdf_lider

app = FastAPI(title="Líder CV API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Você é o formatador oficial de CVs da Líder Inspeções e Qualidade (Quality Experts | ValueAddingPartners).

Sua função é receber o currículo bruto de um profissional e extrair os dados estruturados em JSON.

REGRAS:
1. REMOVER sempre: telefone, e-mail, endereço completo, CPF, RG, data de nascimento, estado civil, foto, idade.
2. MANTER apenas: nome completo e Cidade – Estado.
3. NUNCA copiar e colar o texto original. Reescrever com linguagem técnica profissional elevada.
4. REFORÇAR aspectos de: inspeção de fabricação, diligenciamento de projetos e interface com cliente final.
5. Tom: português técnico formal, verbos ativos, sem adjetivos vazios.
6. Se receber escopo de vaga, alinhar o perfil naturalmente — sem copiar termos da vaga diretamente.

Retorne APENAS um JSON válido, sem markdown, sem texto extra, com esta estrutura exata:
{
  "nome": "Nome Completo",
  "cidade": "Cidade – Estado",
  "titulo": "Cargo Sênior | Especialidades | Segmento",
  "perfil": "Parágrafo único de 5-8 linhas com experiência, especialidades, clientes e certificações.",
  "competencias": ["competencia 1", "competencia 2", ...],
  "clientes": ["Cliente A", "Cliente B", ...],
  "experiencias": [
    {
      "empresa": "EMPRESA | Cliente ou Fornecedor",
      "cargo": "Cargo / Função",
      "periodo": "Mês/Ano – Mês/Ano",
      "bullets": ["atividade 1", "atividade 2", ...]
    }
  ],
  "formacao": [
    {"curso": "Nome do Curso", "instituicao": "Instituição", "ano": "Ano"}
  ],
  "certificacoes": ["certificação 1", "certificação 2", ...],
  "cursos": ["curso 1", "curso 2", ...]
}"""


class ExtractRequest(BaseModel):
    cv_texto: str
    escopo_vaga: Optional[str] = None


class CVData(BaseModel):
    nome: str
    cidade: str
    titulo: str
    perfil: str
    competencias: List[str]
    clientes: List[str]
    experiencias: List[dict]
    formacao: List[dict]
    certificacoes: List[str]
    cursos: List[str]


class SaveRequest(BaseModel):
    cv_data: dict


@app.get("/")
def root():
    return {"status": "Líder CV API online"}


@app.post("/extrair")
async def extrair_cv(req: ExtractRequest):
    if not ANTHROPIC_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada")

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    user_content = f"CV BRUTO:\n{req.cv_texto}"
    if req.escopo_vaga:
        user_content += f"\n\nESCOPO DA VAGA (alinhar perfil naturalmente):\n{req.escopo_vaga}"

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}]
        )

        raw = message.content[0].text.strip()
        # Remove possíveis blocos de código
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        return {"success": True, "data": data}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Erro ao parsear JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gerar-pdf")
async def gerar_pdf(cv: CVData):
    try:
        pdf_bytes = gerar_pdf_lider(cv.dict())
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="CV_{cv.nome.replace(" ", "_")}_Lider.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/inspetores")
async def listar_inspetores():
    # Retorna lista mockada — substitua por Supabase em produção
    return {"inspetores": []}


@app.post("/inspetores")
async def salvar_inspetor(req: SaveRequest):
    # Salva no banco — substitua por Supabase em produção
    return {"success": True, "message": "Inspetor salvo"}
