# webscrapping_twitter

Coletor de tweets do X (antigo Twitter) a partir de termos de busca. O script controla uma janela do Google Chrome já aberta e logada, abre uma aba de busca "Mais recentes" para cada termo, rola as páginas e salva o texto dos tweets encontrados em JSON.

Não usa a API do X: lê o que aparece na tela, como um usuário navegando.

## Como funciona

1. O `run.sh` abre o Chrome com depuração remota na porta `9222`, usando um perfil separado em `~/.x-scraper-profile`.
2. O `main.py` se conecta a esse Chrome via Selenium e lê os termos de busca da entrada padrão.
3. Para cada termo, abre uma aba em `https://x.com/search?q=<termo>&f=live`.
4. Em rodízio entre as abas, coleta os elementos `[data-testid="tweetText"]` visíveis e rola a página.
5. Uma aba é encerrada depois de `MAX_EMPTY_SCROLLS` rolagens seguidas sem tweets novos, ou ao atingir `MAX_SCROLLS`.
6. Ao fim de cada rodada o arquivo de saída é regravado, então uma interrupção no meio não perde o que já foi coletado.

## Requisitos

- Linux (o `run.sh` chama o executável `google-chrome`)
- Google Chrome
- Python 3
- Selenium 4 (o Selenium Manager baixa o ChromeDriver compatível automaticamente)
- Uma conta no X (a busca só funciona logado)

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install selenium
```

## Primeiro uso: login no X

O Chrome é aberto com um perfil próprio (`~/.x-scraper-profile`), sem as sessões do seu navegador normal. Antes da primeira coleta, abra esse perfil e faça login no X:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.x-scraper-profile"
```

Entre em https://x.com, faça login e feche o Chrome. A sessão fica salva no perfil e vale para as próximas execuções.

## Uso

Edite o `input.txt`. A primeira linha é a quantidade de buscas e as seguintes são os termos, um por linha:

```text
3
Lula
Romeu Zema
Luciana Genro
```

Depois, com o ambiente virtual ativado:

```bash
./run.sh
```

Durante a coleta o terminal mostra o progresso de cada termo:

```text
[Lula] scroll 4/15 | novos: 12 | total: 87
```

Também dá para rodar o `main.py` direto, com um Chrome já aberto na porta 9222, e digitar os termos no terminal:

```bash
python3 main.py
```

> **Atenção:** cada execução começa com a lista vazia e **sobrescreve** o `tweets.json`. Renomeie ou copie o arquivo antes de rodar de novo se quiser manter a coleta anterior.

## Configuração

Os parâmetros ficam em `config.py`:

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `MAX_SCROLLS` | `15` | Número máximo de rolagens por aba |
| `SCROLL_DELAY` | `2.5` | Espera (s) após cada rolagem, para o X carregar mais tweets |
| `MAX_EMPTY_SCROLLS` | `3` | Rolagens seguidas sem tweets novos antes de encerrar a aba |
| `OPEN_TAB_DELAY` | `3` | Espera (s) após abrir cada aba de busca |
| `OUTPUT_JSON` | `"tweets.json"` | Arquivo de saída |
| `OUTPUT_JSONL` | `"tweets.jsonl"` | Não é usado pelo código atual |

## Formato da saída

O `tweets.json` é uma lista de objetos:

```json
[
  {
    "id": 1,
    "source": "x",
    "query": "Lula",
    "text": "texto do tweet..."
  }
]
```

| Campo | Descrição |
| --- | --- |
| `id` | Número sequencial na coleta (não é o ID do tweet no X) |
| `source` | Sempre `"x"` |
| `query` | Termo de busca em que o tweet foi encontrado |
| `text` | Texto do tweet |

O `tweets.json` que está no repositório veio de uma versão anterior do script e tem campos a mais (`url`, `created_at`, `images`, `image_captions`) que o `main.py` atual não gera.

## Estrutura

```text
.
├── main.py       # coletor (Selenium)
├── config.py     # parâmetros de coleta
├── run.sh        # abre o Chrome e roda o coletor com input.txt
├── input.txt     # termos de busca
└── tweets.json   # resultado da coleta
```

## Limitações

- **Deduplicação por texto:** tweets com texto idêntico são guardados uma vez só, mesmo que sejam de autores diferentes. Um tweet que aparece em mais de uma busca fica registrado apenas com o primeiro `query` em que foi encontrado.
- **Só o texto:** autor, data, link, métricas e mídia não são coletados.
- **Texto truncado:** tweets longos podem vir cortados, como aparecem na listagem de busca.
- **Dependência do layout:** a coleta depende do seletor `data-testid="tweetText"`. Se o X mudar o HTML, o script para de encontrar tweets.
- **Limites do X:** muitas rolagens em pouco tempo podem fazer o X parar de carregar resultados ou bloquear temporariamente a conta. Se isso acontecer, aumente `SCROLL_DELAY`.
- O `run.sh` espera só 2 segundos pelo Chrome. Em máquinas mais lentas o Selenium pode não conseguir se conectar; nesse caso, aumente o `sleep` no script.
