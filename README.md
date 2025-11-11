# 🕷️ Playwright Web Scraper

> Web Scraping profissional com Playwright - Coleta, armazena e refina dados de qualquer site

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Sobre o Projeto

Um web scraper robusto e flexível construído com Playwright que permite:
- 🌐 Coletar dados de qualquer site de forma automatizada
- 💾 Salvar resultados em CSV e SQLite
- 🔐 Suporte a login com autenticação persistente
- 🤖 Refinar dados com IA (OpenAI) - opcional
- 📊 Sistema de logs e tratamento de erros
- 🐳 Containerizado com Docker

## 🎯 Casos de Uso

- Monitorar preços de produtos
- Coletar artigos e notícias
- Extrair dados de vagas de emprego
- Scraping de redes sociais
- Análise de concorrência
- Coleta de dados públicos

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Passo a Passo

```bash
# Clone o repositório
git clone https://github.com/felipemacedo1/playwright-web-scraper.git
cd playwright-web-scraper

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale os navegadores do Playwright
playwright install chromium
```

### Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas configurações
nano .env
```

## 🎮 Como Usar

### 1. Scraping Básico

```bash
python main.py --url "https://example.com" --output data/results.csv
```

### 2. Com Login Manual

Primeiro, salve seu estado de autenticação:

```bash
python save_storage.py --url "https://example.com/login"
```

Isso abrirá o navegador. Faça login manualmente e feche o navegador. O estado será salvo em `storage_state.json`.

Depois execute o scraper com autenticação:

```bash
python main.py --url "https://example.com" --use-storage
```

### 3. Modo Headless

```bash
python main.py --url "https://example.com" --headless
```

### 4. Com Refinamento de IA (OpenAI)

```bash
# Configure sua API key no .env
OPENAI_API_KEY=sk-your-key-here

# Execute com refinamento
python main.py --url "https://example.com" --refine
```

### 5. Salvando em SQLite

```bash
python main.py --url "https://example.com" --database data/scraping.db
```

## 📁 Estrutura do Projeto

```
playwright-web-scraper/
├── agent/
│   ├── __init__.py
│   ├── scraper.py          # Lógica principal de scraping
│   ├── storage.py          # Salvamento em CSV/SQLite
│   └── llm_refiner.py      # Refinamento com IA (opcional)
├── data/                   # Dados coletados
├── logs/                   # Arquivos de log
├── save_storage.py         # Gerador de storage_state.json
├── main.py                 # Script principal
├── requirements.txt        # Dependências Python
├── .env.example            # Exemplo de configuração
├── .gitignore
├── Dockerfile              # Container Docker
└── README.md
```

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente (.env)

```env
# Navegador
BROWSER_TYPE=chromium
HEADLESS=false
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
USER_AGENT=Mozilla/5.0...

# Timeouts (ms)
NAVIGATION_TIMEOUT=30000
DEFAULT_TIMEOUT=10000

# OpenAI (opcional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Logging
LOG_LEVEL=INFO
```

### Personalizar Seletores

Edite `agent/scraper.py` e ajuste os seletores CSS para o site alvo:

```python
# Exemplo para site de notícias
SELECTORS = {
    'container': 'article, .post, .news-item',
    'title': 'h1, h2, .title',
    'author': '.author, .byline',
    'date': 'time, .date',
    'content': '.content, .article-body',
    'link': 'a[href]'
}
```

## 🐳 Docker

### Build

```bash
docker build -t playwright-scraper .
```

### Run

```bash
docker run -v $(pwd)/data:/app/data playwright-scraper \
  --url "https://example.com" --output /app/data/results.csv
```

## 📊 Exemplos de Output

### CSV

```csv
title,author,date,link,content
"Artigo Exemplo","João Silva","2025-01-11","https://...","Conteúdo do artigo..."
```

### SQLite

```sql
CREATE TABLE scraped_data (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    date TEXT,
    link TEXT UNIQUE,
    content TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Argumentos do CLI

```bash
python main.py [opções]

Opções:
  --url URL              URL alvo para scraping (obrigatório)
  --output FILE          Caminho do arquivo CSV de saída
  --database FILE        Caminho do banco SQLite
  --use-storage          Usa storage_state.json para autenticação
  --headless             Executa em modo headless (sem interface)
  --refine               Refina dados coletados com IA
  --max-items N          Número máximo de itens para coletar
  --scroll-pause SEC     Pausa entre scrolls (segundos)
```

## 🛡️ Boas Práticas

### Respeite os Sites
- ✅ Leia e respeite o `robots.txt`
- ✅ Implemente delays entre requisições
- ✅ Não sobrecarregue servidores
- ✅ Respeite termos de uso

### Anti-Detecção
- ✅ Rotate user agents
- ✅ Use proxies quando necessário
- ✅ Simule comportamento humano (scrolls, pauses)
- ✅ Evite padrões óbvios de bot

### Segurança
- ⚠️ Nunca commite `storage_state.json` ou `.env`
- ⚠️ Use variáveis de ambiente para secrets
- ⚠️ Sanitize dados antes de salvar

## 🧪 Testes

```bash
# Execute os testes
pytest tests/

# Com cobertura
pytest --cov=agent tests/
```

## 🐛 Troubleshooting

### Erro: "Browser not found"

```bash
playwright install chromium
```

### Erro: "Navigation timeout"

Aumente o timeout no `.env`:
```env
NAVIGATION_TIMEOUT=60000
```

### Erro: "Element not found"

Verifique os seletores CSS em `agent/scraper.py` e ajuste para o site alvo.

### Site detecta como bot

- Use `--use-storage` para cookies persistentes
- Adicione delays: `--scroll-pause 2`
- Configure user-agent no `.env`

## 📚 Recursos

- [Playwright Documentation](https://playwright.dev/python/)
- [CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona funcionalidade X'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Disclaimer

Este projeto é para fins educacionais. O uso de web scraping deve respeitar os termos de serviço dos sites e as leis aplicáveis (LGPD, GDPR, etc.). O autor não se responsabiliza pelo uso indevido desta ferramenta.

---

**Desenvolvido por Felipe Macedo** | [GitHub](https://github.com/felipemacedo1)

⭐ Se este projeto foi útil, considere dar uma estrela!
