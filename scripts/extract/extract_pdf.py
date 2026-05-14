import fitz  # PyMuPDF
import pandas as pd
import re

pdf_path = "../../data/raw/estoque.pdf"

texto = ""

# 📥 extração mais confiável
doc = fitz.open(pdf_path)

for page in doc:
    texto += page.get_text("text") + "\n"

# 🧪 DEBUG (IMPORTANTE)
print("Primeiros 1000 caracteres:\n")
print(texto[:1000])

# 🔥 agora vamos trabalhar no texto
linhas = texto.split("\n")
linhas = [l.strip() for l in linhas if l.strip()]

print(f"\nTotal de linhas extraídas: {len(linhas)}")

# padrão de item
padrao_inicio = re.compile(r"^\d+\s+\d+,\d+")

itens = []
buffer = []

for linha in linhas:

    if padrao_inicio.match(linha):
        if buffer:
            itens.append(" ".join(buffer))
            buffer = []
        buffer.append(linha)
    else:
        buffer.append(linha)

if buffer:
    itens.append(" ".join(buffer))

print(f"Itens detectados: {len(itens)}")

dados = []

for item in itens:
    match = re.match(r"(\d+)\s+(\d+,\d+)", item)
    if not match:
        continue

    codigo = match.group(1)
    valor = match.group(2)

    descricao = item[len(match.group(0)):].strip()

    dados.append({
        "codigo": codigo,
        "valor": valor,
        "descricao": descricao
    })

df = pd.DataFrame(dados)

df.to_csv("../../data/processed/estoque_tratado.csv", index=False)

print(f"\nRegistros finais: {len(df)}")