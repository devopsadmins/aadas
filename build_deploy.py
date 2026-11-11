"""Monta a pasta aadas-site/ para publicação de teste.

- landing/index.html vira a raiz do site; a seção Transparência dela só chama o portal;
- a página /transparencia é gerada a partir da landing (mesmo topo, menu e rodapé) com as pastas
  de DOCUMENTOS (transparencia/index.html fica como versão interna de revisão e não vai para o site);
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


# Única fonte da lista publicada: (id da pasta, pasta, [(subtítulo ou None, [(título, arquivo em transparencia/documentos)])])
# Na página cada pasta aparece fechada, só com o título; o clique abre os documentos.
# O id abre a pasta direto pelo link (/transparencia#contabeis), usado pelos atalhos da landing.
DOCUMENTOS = [
    ("institucionais", "Documentos institucionais", [(None, [
        ("Estatuto Social", "estatuto-social.pdf"),
        ("Regulamento Interno", "regulamento-interno.pdf"),
        ("Certidão de Dirigentes e Conselheiros, gestão 2026 a 2030", "certidao-dirigentes-2026-2030.pdf"),
    ])]),
    ("parcerias", "Convênios e parcerias", [
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
    ("contabeis", "Documentos contábeis", [(None, [
        ("Demonstrações contábeis 2025", "demonstracoes-contabeis-2025.pdf"),
        ("Demonstrações contábeis 2024", "demonstracoes-contabeis-2024.pdf"),
        ("Demonstrações contábeis 2023", "demonstracoes-contabeis-2023.pdf"),
    ])]),
    ("relatorios", "Relatórios de atividades", [(None, [
        (f"Relatório de atividades {ano}", f"relatorio-atividades-{ano}.pdf") for ano in range(2025, 2017, -1)
    ])]),
]

# CSS das pastas recolhíveis, igual na landing e na /transparencia
CSS_PASTAS = """
  .grupo-docs { margin: 0 0 10px; border: 1px solid var(--borda-pasta); border-radius: 12px; background: var(--fundo-pasta); }
  .grupo-docs { scroll-margin-top: 84px; }
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
    for _, _, subgrupos in DOCUMENTOS:
        for _, docs in subgrupos:
            yield from docs


def lista_documentos(nivel):
    blocos = []
    for ident, pasta, subgrupos in DOCUMENTOS:
        partes = []
        for sub, docs in subgrupos:
            itens = "\n".join(
                f'        <li><a href="/transparencia/documentos/{arq}" download>{titulo}</a></li>' for titulo, arq in docs)
            cab = f'      <h{nivel + 1} class="subtitulo">{sub}</h{nivel + 1}>\n' if sub else ""
            partes.append(f'{cab}      <ul class="lista-docs">\n{itens}\n      </ul>')
        blocos.append(f'  <details class="grupo-docs" id="{ident}">\n    <summary>{pasta}</summary>\n'
                      f'    <div class="conteudo">\n' + "\n".join(partes) + '\n    </div>\n  </details>')
    return "\n".join(blocos)


PORTAL = "/transparencia"


def landing():
    t = (RAIZ / "landing/index.html").read_text(encoding="utf-8")
    t = troca(t, '<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + NOINDEX)
    return troca(t, "../transparencia/index.html", PORTAL)


# CSS só do portal: cabeçalho da página, grade das pastas e lista de documentos
CSS_PORTAL = """
  /* Portal da Transparência */
  .portal { padding: 56px 0 88px; }
  .portal h1 { font-size: clamp(2.1rem, 4vw, 3rem); font-weight: 700; margin-top: 10px; }
  .portal .lead { font-size: 1.1rem; }
  .pastas { display: grid; gap: 0 24px; margin-top: 36px; grid-template-columns: 1fr; align-items: start; }
  @media (min-width: 900px) { .pastas { grid-template-columns: repeat(2, 1fr); } }
  .lista-docs { list-style: none; margin: 0; padding: 0; background: var(--fundo); border: 1px solid var(--linha); border-radius: 12px; }
  .lista-docs li { border-top: 1px solid var(--linha); }
  .lista-docs li:first-child { border-top: 0; }
  .lista-docs a { display: block; padding: 10px 16px; font-weight: 600; text-decoration: none; }
  .lista-docs a:hover { text-decoration: underline; }
  .portal .nota { color: var(--texto-2); margin-top: 28px; }
  :root { --borda-pasta: var(--linha); --fundo-pasta: var(--superficie); --foco: var(--amarelo); }
""" + CSS_PASTAS


def transparencia():
    """Página própria do portal, com o mesmo topo, menu, rodapé e VLibras da landing."""
    t = (RAIZ / "landing/index.html").read_text(encoding="utf-8")
    topo, resto = t.split('<main id="conteudo">', 1)
    rodape = resto.split("</main>", 1)[1]
    desc = ("Portal da Transparência da AADAS: documentos institucionais, convênios e parcerias com o poder público, "
            "demonstrações contábeis e relatórios de atividades.")
    topo = troca(topo, '<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + NOINDEX)
    topo = re.sub(r"<title>.*?</title>", "<title>Portal da Transparência | AADAS</title>", topo, count=1)
    topo = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"',
                  lambda m: m.group(1) + desc + '"', topo)
    topo = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*"',
                  lambda m: m.group(1) + 'Portal da Transparência | AADAS"', topo)
    topo = troca(topo, '<meta property="og:url" content="https://www.aadas.org/">',
                 '<meta property="og:url" content="https://www.aadas.org/transparencia">')
    topo = troca(topo, '<link rel="canonical" href="https://www.aadas.org/">',
                 '<link rel="canonical" href="https://www.aadas.org/transparencia">')
    topo = remove(topo, r'<link rel="preload" as="image"[^>]*>\n')
    topo = troca(topo, "</style>", CSS_PORTAL + "</style>")
    topo = troca(topo, '<a href="../transparencia/index.html">Transparência</a>',
                 '<a href="../transparencia/index.html" aria-current="page">Transparência</a>')
    corpo = f"""<main id="conteudo">
  <section class="portal">
    <div class="wrap">
      <p class="sobretitulo">Transparência</p>
      <h1>Portal da Transparência</h1>
      <p class="lead">Documentos da AADAS para associados, parceiros, doadores e poder público. Clique numa pasta para ver os arquivos.</p>
      <div class="pastas">
{lista_documentos(2)}
      </div>
      <p class="nota">Não encontrou o que procurava? Escreva para <a href="mailto:contato@aadasjc.org">contato@aadasjc.org</a>.</p>
    </div>
  </section>
</main>"""
    abre = """<script>
  // /transparencia#contabeis chega com a pasta aberta
  (function () {
    function abrir() { var d = location.hash && document.getElementById(location.hash.slice(1));
      if (d && d.tagName === 'DETAILS') { d.open = true; d.scrollIntoView(); } }
    abrir(); window.addEventListener('hashchange', abrir);
  })();
</script>
"""
    rodape = troca(rodape, "</body>", abre + "</body>")
    pagina = topo + corpo + rodape
    # página fica em /transparencia: caminhos relativos e âncoras passam a apontar para a raiz
    pagina = re.sub(r'(src|href)="assets/', r'\1="/assets/', pagina)
    pagina = troca(pagina, 'href="#topo"', 'href="/"')
    pagina = re.sub(r'href="#(quem-somos|redes|apoie|visite)"', r'href="/#\1"', pagina)
    return troca(pagina, "../transparencia/index.html", PORTAL)


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
