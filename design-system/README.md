# Design System AADAS

Guia visual completo: abra `index.html` no navegador.

## Fontes usadas para montar

- Logo oficial (`landing/assets/logo.png`, `simbolo.png`): cores medidas no arquivo.
- Drive, pasta "AADAS SITE/Docs": *Conteúdo do site*, *Considerações a serem discutidas para o site*, *Reunião de ajustes e segmentos do site*, *respostas para site*.
- O "manual da marca" citado nesses documentos não está no Drive. Se aparecer, conferir cores e fonte do logo contra ele.

## Arquivos

| Arquivo | Para quê |
|---|---|
| `tokens.css` | Variáveis CSS em 3 camadas: primitivo, semântico, componente |
| `tokens.json` | Os mesmos valores para Figma, Canva, Tailwind |
| `components.css` | Botões, balão, cartões, verbos AADAS, selos, formulário, lista de documentos, topo e rodapé |
| `index.html` | O guia, com exemplos de cada peça |

## Regras que não podem ser quebradas

1. Cores oficiais: azul **#1A184D** e amarelo **#F6C313**. Nada de preto nas barras.
2. Amarelo nunca é cor de texto sobre fundo claro (1,6:1). Texto sobre amarelo é sempre azul.
3. Um botão amarelo (principal) por tela.
4. "LIBRAS" em maiúsculas; nunca "surdo-mudo".
5. Frases afirmativas ("Juntos conseguiremos"), de convite, não de pena.
6. Fotos reais da AADAS; sinal de LIBRAS só se for o sinal certo.
7. Vídeo sempre com legenda e janela de LIBRAS.

## Diferença com a página de Transparência

`transparencia/index.html` usa `#001748` e `#EAC700`, que não batem com o logo. Para alinhar, troque o bloco `:root` dela pelos tokens daqui (`--azul` → `var(--aadas-azul-900)`, `--amarelo` → `var(--aadas-amarelo-500)`).
