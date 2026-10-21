"""Monta a pasta aadas-site/ para publicação de teste.

- landing/index.html vira a raiz do site, com a seção Transparência trocada pela lista de DOCUMENTOS;
- a página /transparencia é gerada só com a lista de DOCUMENTOS (transparencia/index.html fica
  como versão interna de revisão e não vai para o site);
- as duas páginas recebem noindex (o vercel.json repete isso no cabeçalho HTTP).
"""
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "aadas-site"
NOINDEX = '<meta name="robots" content="noindex, nofollow">\n'


def troca(texto, antigo, novo):
    if antigo not in texto:
        raise SystemExit(f"trecho não encontrado: {antigo[:70]!r}")
    return texto.replace(antigo, novo)


def remove(texto, padrao, minimo=1):
    novo, n = re.subn(padrao, "", texto, flags=re.S)
    if n < minimo:
        raise SystemExit(f"padrão não encontrado: {padrao[:70]!r}")
    return novo


# Única fonte da lista publicada: (pasta, [(subtítulo ou None, [(título, arquivo em transparencia/documentos)])])
# Na página cada pasta aparece fechada, só com o título; o clique abre os documentos.
DOCUMENTOS = [
    ("Documentos institucionais", [(None, [
        ("Estatuto Social", "estatuto-social.pdf"),
        ("Regulamento Interno", "regulamento-interno.pdf"),
        ("Certidão de Dirigentes e Conselheiros, gestão 2026 a 2030", "certidao-dirigentes-2026-2030.pdf"),
    ])]),
    ("Convênios e parcerias", [
        ("Termo de Colaboração nº 32/2018, Prefeitura de São José dos Campos", [
            ("Termo de Colaboração nº 32/2018", "tc-32-2018-termo.pdf"),
            ("Plano de Trabalho 2026", "plano-de-trabalho-2026.pdf"),
            *[(f"{n}º Termo Aditivo", f"tc-32-2018-aditivo-{n:02d}.pdf") for n in range(1, 9)],
            *[(f"{n}º Apostilamento", f"tc-32-2018-apostilamento-{n:02d}.pdf") for n in range(1, 4)],
        ]),
        ("Equipe da parceria", [
            ("Relação de cargos e salários 2025", "cargos-e-salarios-2025.pdf"),
        ]),
    ]),
    ("Documentos contábeis", [(None, [
        ("Demonstrações contábeis 2025", "demonstracoes-contabeis-2025.pdf"),
        ("Demonstrações contábeis 2024", "demonstracoes-contabeis-2024.pdf"),
    ])]),
    ("Relatórios de Atividades", [(None, [
        (f"Relatório de atividades {ano}", f"relatorio-atividades-{ano}.pdf") for ano in range(2025, 2017, -1)
    ])]),
]

# CSS das pastas recolhíveis, igual na landing e na /transparencia
CSS_PASTAS = """
  .grupo-docs { margin: 0 0 10px; border: 1px solid var(--borda-pasta); border-radius: 12px; background: var(--fundo-pasta); }
  .grupo-docs > summary { cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center;
                          gap: 12px; padding: 14px 16px; font-weight: 700; font-size: 1.05rem; }
  .grupo-docs > summary::-webkit-details-marker { display: none; }
  .grupo-docs > summary::after { content: "+"; font-size: 1.4rem; line-height: 1; }
  .grupo-docs[open] > summary::after { content: "\\2212"; }
  .grupo-docs > summary:focus-visible { outline: 3px solid var(--foco, currentColor); outline-offset: 2px; }
  .grupo-docs .conteudo { padding: 0 16px 16px; }
  .grupo-docs .subtitulo { font-size: .95rem; margin: 8px 0 6px; }
"""


def documentos():
    for _, subgrupos in DOCUMENTOS:
        for _, docs in subgrupos:
            yield from docs


def lista_documentos(nivel):
    blocos = []
    for pasta, subgrupos in DOCUMENTOS:
        partes = []
        for sub, docs in subgrupos:
            itens = "\n".join(
                f'        <li><a href="/transparencia/documentos/{arq}" download>{titulo}</a></li>' for titulo, arq in docs)
            cab = f'      <h{nivel + 1} class="subtitulo">{sub}</h{nivel + 1}>\n' if sub else ""
            partes.append(f'{cab}      <ul class="lista-docs">\n{itens}\n      </ul>')
        blocos.append(f'  <details class="grupo-docs">\n    <summary>{pasta}</summary>\n'
                      f'    <div class="conteudo">\n' + "\n".join(partes) + '\n    </div>\n  </details>')
    return "\n".join(blocos)


VLIBRAS = ('<div vw class="enabled"><div vw-access-button class="active"></div>'
           '<div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div></div>\n'
           '<script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>\n'
           "<script>if (window.VLibras) new window.VLibras.Widget('https://vlibras.gov.br/app');</script>\n")


def landing():
    t = (RAIZ / "landing/index.html").read_text(encoding="utf-8")
    t = troca(t, '<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + NOINDEX)
    t = t.replace("../transparencia/index.html", "transparencia/index.html")
    t = re.sub(r"(<!-- documentos:inicio -->\n).*?(\s*<!-- documentos:fim -->)",
               lambda m: m.group(1) + lista_documentos(3) + m.group(2), t, count=1, flags=re.S)
    t = troca(t, "  .grupo-docs h3 { font-size: 1.05rem; margin: 0 0 8px; }\n",
              "  :root { --borda-pasta: var(--linha); --fundo-pasta: var(--superficie); }" + CSS_PASTAS)
    if "documentos:inicio" not in t:
        raise SystemExit("marcador da lista de documentos não encontrado na landing")
    return t


def transparencia():
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
{NOINDEX}<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Transparência | AADAS</title>
<meta name="description" content="Portal da Transparência da AADAS: documentos institucionais, parcerias com o poder público, equipe, contas e relatórios de atividades.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AADAS">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="Transparência | AADAS">
<meta property="og:description" content="Estatuto, termos de colaboração, contas e relatórios de atividades da AADAS.">
<meta property="og:url" content="https://www.aadas.org/transparencia">
<meta property="og:image" content="https://www.aadas.org/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.aadas.org/assets/og-image.jpg">
<meta name="theme-color" content="#1a184d">
<link rel="icon" href="/assets/simbolo.png">
<link rel="canonical" href="https://www.aadas.org/transparencia">
<link rel="stylesheet" href="/design-system/tokens.css">
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: var(--fonte-texto); font-size: var(--fs-corpo); line-height: var(--lh-corpo);
         color: var(--texto); background: var(--fundo-pagina); }}
  h1, h2, .marca {{ font-family: var(--fonte-titulo); }}
  a:focus-visible {{ outline: 3px solid var(--foco); outline-offset: 2px; box-shadow: 0 0 0 6px var(--cor-marca); }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 0 16px; }}
  header {{ background: var(--fundo-inverso); color: var(--texto-inverso); border-bottom: 6px solid var(--cor-destaque); }}
  header .wrap {{ padding-top: 32px; padding-bottom: 28px; }}
  .marca {{ font-weight: 800; letter-spacing: .04em; color: var(--texto-inverso); text-decoration: none; }}
  .marca span {{ color: var(--cor-destaque); }}
  h1 {{ font-size: clamp(1.8rem, 4vw, 2.6rem); margin: 14px 0 0; line-height: 1.15; }}
  main {{ padding-bottom: 56px; }}
  h2 {{ color: var(--cor-marca); font-size: 1.25rem; margin: 40px 0 8px; }}
  .lista-docs {{ list-style: none; margin: 0; padding: 0; background: var(--fundo-superficie);
                border: 1px solid var(--borda); border-radius: 10px; }}
  .lista-docs li {{ border-top: 1px solid var(--borda); }}
  .lista-docs li:first-child {{ border-top: 0; }}
  .lista-docs a {{ display: block; padding: 12px 16px; font-weight: 600; color: var(--texto-link); text-decoration: none; }}
  .lista-docs a:hover {{ text-decoration: underline; }}
  :root {{ --borda-pasta: var(--borda); --fundo-pasta: var(--fundo-superficie); }}
  main.wrap {{ padding-top: 32px; }}
{CSS_PASTAS}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <a class="marca" href="/">AADAS <span>●</span></a>
    <h1>Transparência</h1>
  </div>
</header>
<main class="wrap">
{lista_documentos(2)}
</main>
{VLIBRAS}</body>
</html>
"""


# Arquivos locais da Vercel CLI: ficam entre um build e outro e não são publicados
PRESERVAR = {".vercel", ".env.local", ".gitignore"}


def main():
    if SAIDA.exists():
        for item in SAIDA.iterdir():
            if item.name in PRESERVAR:
                continue
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    (SAIDA / "transparencia").mkdir(parents=True)
    shutil.copytree(RAIZ / "landing/assets", SAIDA / "assets")
    (SAIDA / "design-system").mkdir()
    shutil.copy2(RAIZ / "design-system/tokens.css", SAIDA / "design-system/tokens.css")
    # PDFs já tarjados (LGPD); a página só aponta para arquivos que estão aqui
    shutil.copytree(RAIZ / "transparencia/documentos", SAIDA / "transparencia/documentos")
    (SAIDA / "index.html").write_text(landing(), encoding="utf-8")
    (SAIDA / "transparencia/index.html").write_text(transparencia(), encoding="utf-8")
    for _, arq in documentos():
        if not (SAIDA / "transparencia/documentos" / arq).is_file():
            raise SystemExit(f"documento listado e ausente: {arq}")
    (SAIDA / "vercel.json").write_text(
        '{\n  "cleanUrls": true,\n  "headers": [\n    {"source": "/(.*)", "headers": [\n'
        '      {"key": "X-Robots-Tag", "value": "noindex, nofollow"}\n    ]}\n  ]\n}\n',
        encoding="utf-8",
    )
    publicados = [p for p in SAIDA.rglob("*") if p.is_file() and p.relative_to(SAIDA).parts[0] not in PRESERVAR]
    print("aadas-site/ pronto:", sorted(str(p.relative_to(SAIDA)) for p in publicados))


if __name__ == "__main__":
    main()
