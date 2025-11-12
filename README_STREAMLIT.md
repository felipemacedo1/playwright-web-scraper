# 🎨 Interface Streamlit

## 🚀 Como Iniciar

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Inicie a interface
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

---

## ✨ Funcionalidades

### ⚙️ Configurações (Sidebar)
- 🌐 **URL alvo** - Site para fazer scraping
- 📊 **Max items** - Limite de itens
- ⏱️ **Scroll pause** - Pausa entre scrolls
- 🔇 **Headless mode** - Executar sem interface gráfica
- 🚫 **Não fazer scroll** - Desabilitar scroll automático
- 🔐 **Autenticação** - Usar storage_state.json
- 💾 **Formato de saída** - CSV ou JSON
- 💿 **SQLite** - Salvar em banco de dados

### 🎯 Seletores CSS Avançados
- Container
- Título  
- Autor
- Data
- Conteúdo

### 📋 Abas

**🚀 Executar**
- Configurar e iniciar scraping
- Ver progress em tempo real
- Preview dos dados coletados
- Download dos resultados

**📊 Histórico**
- Ver scraping anteriores
- Visualizar arquivos salvos
- Download de resultados antigos

**ℹ️ Ajuda**
- Guia de uso
- Dicas e troubleshooting
- Exemplos práticos

---

## 📸 Screenshots

### Tela Principal
- Interface limpa e intuitiva
- Configurações na sidebar
- Execução com feedback visual

### Resultados
- Tabela interativa com dados
- Estatísticas (total, colunas, tamanho)
- Botão de download

### Histórico
- Lista de scraping anteriores
- Preview de arquivos
- Gerenciamento de dados

---

## 💡 Dicas

### Para Desenvolvedores
- Use CLI para automação
- Use Streamlit para configurar/testar

### Para Não-Técnicos
- Interface auto-explicativa
- Não precisa terminal
- Visual e interativo

---

## 🔧 Customização

Edite `app.py` para:
- Mudar cores/tema
- Adicionar mais opções
- Criar novos gráficos
- Integrar com outros serviços

---

## 🐛 Troubleshooting

**Streamlit não abre**
```bash
streamlit run app.py --server.headless true
```

**Porta em uso**
```bash
streamlit run app.py --server.port 8502
```

**Erro de importação**
```bash
pip install streamlit pandas
```

---

**Criado com ❤️ usando Streamlit**
