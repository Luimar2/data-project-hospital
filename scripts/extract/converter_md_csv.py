import csv
import re
import sys
from pathlib import Path


MONEY_RE = re.compile(r"^\d{1,3}(?:\.\d{3})*,\d{2}\s*$|^\d+,\d{2}\s*$")
INT_RE = re.compile(r"^\d+$")
QTY_RE = re.compile(r"^\d+(?:\.\d{3})*$")
UNIT_RE = re.compile(r"^[A-ZÁÉÍÓÚÃÕÇ]{1,5}$")

HEADER_WORDS = {
    "consumo",
    "qtde",
    "código",
    "codigo",
    "nome",
    "unidade",
    "valor",
    "mensal",
    "médio",
    "medio",
    "estoque",
}

POST_NAME_RE = re.compile(
    r"^(?:\(|REF\b|MM X\b|\d+(?:[,.]\d+)?\s*(?:CM|MM|FR|G)?\s*X|[A-Z0-9 /.,+\-ÁÉÍÓÚÂÊÔÃÕÇ]+\))",
    re.IGNORECASE,
)


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def is_int(text: str) -> bool:
    return bool(INT_RE.fullmatch(text.strip()))


def is_qty(text: str) -> bool:
    return bool(QTY_RE.fullmatch(text.strip()))


def is_money(text: str) -> bool:
    return bool(MONEY_RE.fullmatch(text.strip()))


def is_unit(text: str) -> bool:
    return bool(UNIT_RE.fullmatch(text.strip())) and not is_int(text)


def looks_like_header(line: str) -> bool:
    return clean_line(line).casefold() in HEADER_WORDS


def looks_like_product_line(line: str) -> bool:
    letters = [ch for ch in line if ch.isalpha()]
    if not letters:
        return False
    uppercase = sum(1 for ch in letters if ch.upper() == ch)
    return uppercase / len(letters) >= 0.72


def looks_like_category(line: str) -> bool:
    return any(ch.islower() for ch in line if ch.isalpha())


def split_category_and_name(lines):
    if not lines:
        return [], []

    first_product = 0
    for idx, line in enumerate(lines):
        if looks_like_product_line(line):
            first_product = idx
            break
    else:
        first_product = max(0, len(lines) - 1)

    return lines[:first_product], lines[first_product:]


def parse_prefix(prefix):
    """Split lines before the 3 quantities into category/name/code."""
    prefix = [line for line in prefix if line and not looks_like_header(line)]
    expanded = []
    for line in prefix:
        glued = re.match(r"^(\d{2,})\s+(.+)$", line)
        if glued:
            expanded.extend([glued.group(1), glued.group(2)])
        else:
            expanded.append(line)
    prefix = expanded

    if not prefix:
        return "", "", "", []

    int_positions = [idx for idx, line in enumerate(prefix) if is_int(line)]
    if not int_positions:
        category_lines, name_lines = split_category_and_name(prefix)
        return " ".join(category_lines), "", " ".join(name_lines), []

    first = int_positions[0]
    last = int_positions[-1]

    if first == 0 and len(prefix) > 1:
        code = prefix[first]
        category_lines = []
        name_lines = prefix[first + 1 :]
    elif last == len(prefix) - 1 and len(prefix) > 1:
        code = prefix[last]
        category_lines, name_lines = split_category_and_name(prefix[:last])
    else:
        code = prefix[first]
        category_lines = prefix[:first]
        name_lines = prefix[first + 1 :]

    return " ".join(category_lines), code, " ".join(name_lines), []


def convert(input_path: Path, output_path: Path):
    lines = [clean_line(line) for line in input_path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line]

    rows = []
    pending = []
    current_category = ""
    warnings = []
    i = 0

    while i < len(lines):
        if (
            i + 4 < len(lines)
            and is_qty(lines[i])
            and is_qty(lines[i + 1])
            and is_qty(lines[i + 2])
            and is_unit(lines[i + 3])
            and is_money(lines[i + 4])
        ):
            while rows and pending and POST_NAME_RE.match(pending[0]):
                rows[-1]["nome"] = f"{rows[-1]['nome']} {pending.pop(0)}".strip()
            while (
                rows
                and len(pending) > 1
                and looks_like_product_line(pending[0])
                and looks_like_category(pending[1])
            ):
                rows[-1]["nome"] = f"{rows[-1]['nome']} {pending.pop(0)}".strip()

            category, code, name, extra_warnings = parse_prefix(pending)
            warnings.extend(extra_warnings)
            if category:
                if looks_like_category(category):
                    current_category = category
                elif rows:
                    rows[-1]["nome"] = f"{rows[-1]['nome']} {category}".strip()

            if not name:
                warnings.append(f"Registro perto da linha processada {i}: codigo/nome incompleto: {pending!r}")

            rows.append(
                {
                    "categoria": current_category,
                    "codigo": code,
                    "nome": name,
                    "consumo_mensal": lines[i],
                    "consumo_medio": lines[i + 1],
                    "qtde_estoque": lines[i + 2],
                    "unidade": lines[i + 3],
                    "valor": lines[i + 4],
                }
            )
            pending = []
            i += 5
            continue

        line = lines[i]
        if rows and not rows[-1]["codigo"] and not pending and is_int(line):
            rows[-1]["codigo"] = line
            i += 1
            continue

        pending.append(line)
        i += 1

    if pending:
        warnings.append(f"Linhas finais nao convertidas: {pending!r}")

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "categoria",
                "codigo",
                "nome",
                "consumo_mensal",
                "consumo_medio",
                "qtde_estoque",
                "unidade",
                "valor",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows, warnings


def main(argv):
    if len(argv) not in (2, 3):
        print("Uso: converter_estoque_md_csv.py entrada.md [saida.csv]", file=sys.stderr)
        return 2

    input_path = Path(argv[1])
    output_path = Path(argv[2]) if len(argv) == 3 else input_path.with_suffix(".csv")
    rows, warnings = convert(input_path, output_path)

    print(f"CSV gerado: {output_path}")
    print(f"Registros: {len(rows)}")
    print(f"Avisos: {len(warnings)}")
    for warning in warnings[:20]:
        print(f"- {warning}")
    if len(warnings) > 20:
        print(f"- ... mais {len(warnings) - 20} avisos")
    return 0 if not warnings else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
