"""
Streamlit Web Interface - Playwright Web Scraper

Interface visual para configurar e executar scraping.

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

from agent.scraper import WebScraper
from agent.storage import save_data

# Configuração da página
st.set_page_config(
    page_title="Web Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🕷️ Web Scraper</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# URL
url = st.sidebar.text_input(
    "🌐 URL alvo",
    placeholder="https://example.com",
    help="URL da página que deseja fazer scraping"
)

# Opções básicas
col1, col2 = st.sidebar.columns(2)
with col1:
    max_items = st.number_input(
        "📊 Max items",
        min_value=1,
        max_value=100,
        value=10,
        help="Número máximo de itens para coletar"
    )
with col2:
    scroll_pause = st.number_input(
        "⏱️ Scroll pause (s)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        help="Pausa entre scrolls"
    )

# Checkboxes
headless = st.sidebar.checkbox("🔇 Headless mode", value=True, help="Executar sem interface gráfica")
no_scroll = st.sidebar.checkbox("🚫 Não fazer scroll", value=False)
use_storage = st.sidebar.checkbox("🔐 Usar autenticação (storage_state.json)", value=False)

# Output
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Output")

output_format = st.sidebar.selectbox(
    "Formato",
    ["csv", "json"],
    help="Formato do arquivo de saída"
)

output_path = st.sidebar.text_input(
    "Caminho do arquivo",
    value=f"data/scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
)

save_to_db = st.sidebar.checkbox("💿 Salvar em SQLite", value=False)
if save_to_db:
    db_path = st.sidebar.text_input(
        "Caminho do banco",
        value="data/scraping.db"
    )
else:
    db_path = None

# Seletores avançados (expansível)
with st.sidebar.expander("🎯 Seletores CSS (Avançado)"):
    st.markdown("**Deixe vazio para usar padrões**")
    custom_selectors = {}
    
    custom_selectors['container'] = st.text_input(
        "Container",
        placeholder="article, .post, .card",
        help="Seletor para containers principais"
    )
    custom_selectors['title'] = st.text_input(
        "Título",
        placeholder="h1, h2, .title",
        help="Seletor para títulos"
    )
    custom_selectors['author'] = st.text_input(
        "Autor",
        placeholder=".author, .byline",
        help="Seletor para autores"
    )
    custom_selectors['date'] = st.text_input(
        "Data",
        placeholder="time, .date",
        help="Seletor para datas"
    )
    custom_selectors['content'] = st.text_input(
        "Conteúdo",
        placeholder=".content, p",
        help="Seletor para conteúdo"
    )

# Main content
tab1, tab2, tab3 = st.tabs(["🚀 Executar", "📊 Histórico", "ℹ️ Ajuda"])

with tab1:
    st.subheader("Executar Scraping")
    
    # Preview das configurações
    with st.expander("📋 Preview das Configurações", expanded=False):
        config = {
            "URL": url or "Não definida",
            "Max items": max_items,
            "Headless": "Sim" if headless else "Não",
            "Scroll": "Não" if no_scroll else f"Sim (pausa: {scroll_pause}s)",
            "Output": output_path,
            "Formato": output_format.upper(),
            "Banco de dados": db_path if save_to_db else "Não",
            "Autenticação": "Sim" if use_storage else "Não"
        }
        
        for key, value in config.items():
            st.text(f"{key}: {value}")
    
    # Botão de execução
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        execute_button = st.button(
            "▶️ Iniciar Scraping",
            type="primary",
            use_container_width=True,
            disabled=not url
        )
    
    if not url:
        st.warning("⚠️ Por favor, insira uma URL na sidebar.")
    
    # Execução
    if execute_button and url:
        # Validação básica
        if not url.startswith('http'):
            st.error("❌ URL inválida. Deve começar com http:// ou https://")
        else:
            # Container para logs e resultados
            status_container = st.empty()
            progress_bar = st.progress(0)
            log_container = st.expander("📝 Logs", expanded=True)
            
            try:
                with status_container.container():
                    st.info("🚀 Iniciando scraping...")
                
                progress_bar.progress(10)
                
                # Inicializa scraper
                with log_container:
                    st.text("🌐 Iniciando navegador...")
                
                scraper = WebScraper(headless=headless)
                
                # Aplica seletores customizados se fornecidos
                if any(custom_selectors.values()):
                    for key, value in custom_selectors.items():
                        if value:
                            scraper.SELECTORS[key] = value
                    st.text("✅ Seletores customizados aplicados")
                
                storage_state = "storage_state.json" if use_storage and Path("storage_state.json").exists() else None
                scraper.start(storage_state=storage_state)
                
                progress_bar.progress(30)
                
                with log_container:
                    st.text(f"📡 Navegando para: {url}")
                
                # Navega
                if not scraper.navigate(url):
                    st.error("❌ Falha ao carregar página")
                    scraper.close()
                    st.stop()
                
                progress_bar.progress(50)
                
                # Scroll
                if not no_scroll:
                    with log_container:
                        st.text("📜 Fazendo scroll...")
                    scraper.scroll_to_bottom(pause_time=scroll_pause)
                
                progress_bar.progress(70)
                
                # Extrai dados
                with log_container:
                    st.text("🔍 Extraindo dados...")
                
                data = scraper.extract_data(max_items=max_items)
                scraper.close()
                
                progress_bar.progress(90)
                
                if not data:
                    st.warning("⚠️ Nenhum dado coletado. Verifique os seletores CSS.")
                    st.stop()
                
                # Salva dados
                with log_container:
                    st.text("💾 Salvando dados...")
                
                save_data(
                    data=data,
                    output_path=output_path,
                    database_path=db_path,
                    format=output_format
                )
                
                progress_bar.progress(100)
                
                # Sucesso!
                status_container.empty()
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ Scraping concluído com sucesso!</h3>
                    <p><strong>Total de itens:</strong> {len(data)}</p>
                    <p><strong>Arquivo:</strong> {output_path}</p>
                    {f'<p><strong>Banco:</strong> {db_path}</p>' if db_path else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Preview dos dados
                st.subheader("📊 Preview dos Dados")
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Estatísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de itens", len(data))
                with col2:
                    st.metric("Colunas", len(df.columns))
                with col3:
                    st.metric("Tamanho", f"{len(str(data)) / 1024:.1f} KB")
                
                # Download
                st.subheader("📥 Download")
                
                if output_format == "csv":
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        csv_data,
                        file_name=Path(output_path).name,
                        mime="text/csv"
                    )
                else:
                    json_data = json.dumps(data, ensure_ascii=False, indent=2)
                    st.download_button(
                        "⬇️ Download JSON",
                        json_data,
                        file_name=Path(output_path).name,
                        mime="application/json"
                    )
                
            except Exception as e:
                status_container.empty()
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ Erro durante scraping</h3>
                    <p><strong>Erro:</strong> {str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🔍 Detalhes do erro"):
                    st.exception(e)

with tab2:
    st.subheader("📊 Histórico de Scraping")
    
    # Lista arquivos na pasta data
    data_dir = Path("data")
    if data_dir.exists():
        files = sorted(data_dir.glob("scraping_*.csv"), reverse=True)
        
        if files:
            st.write(f"**Total de arquivos:** {len(files)}")
            
            # Tabela de histórico
            history_data = []
            for file in files[:10]:  # Últimos 10
                stat = file.stat()
                history_data.append({
                    "Arquivo": file.name,
                    "Tamanho": f"{stat.st_size / 1024:.1f} KB",
                    "Modificado": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            df_history = pd.DataFrame(history_data)
            st.dataframe(df_history, use_container_width=True)
            
            # Visualizar arquivo específico
            selected_file = st.selectbox("Selecione um arquivo para visualizar:", [f.name for f in files])
            
            if selected_file:
                file_path = data_dir / selected_file
                if file_path.suffix == ".csv":
                    df = pd.read_csv(file_path)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download",
                        csv_data,
                        file_name=selected_file,
                        mime="text/csv"
                    )
        else:
            st.info("📭 Nenhum scraping realizado ainda.")
    else:
        st.info("📁 Pasta 'data' não encontrada.")

with tab3:
    st.subheader("ℹ️ Como Usar")
    
    st.markdown("""
    ### 🚀 Guia Rápido
    
    1. **Configure a URL** na sidebar
    2. **Ajuste as opções** (max items, headless, etc)
    3. **Clique em "Iniciar Scraping"**
    4. **Aguarde** a coleta dos dados
    5. **Visualize e baixe** os resultados
    
    ---
    
    ### 🎯 Seletores CSS
    
    Se o scraper não encontrar dados, você precisa customizar os seletores:
    
    1. Abra o site no navegador
    2. Pressione **F12** (DevTools)
    3. Use o **Inspect** para encontrar as classes CSS
    4. Insira os seletores na seção "Avançado" da sidebar
    
    **Exemplos:**
    - Container: `article`, `.post`, `.card`
    - Título: `h1`, `h2`, `.title`
    - Autor: `.author`, `.byline`
    
    ---
    
    ### 🔐 Autenticação
    
    Para sites que requerem login:
    
    1. Execute no terminal:
       ```bash
       python3 save_storage.py --url "https://site.com/login"
       ```
    2. Faça login manualmente no navegador que abrir
    3. Feche o navegador
    4. Marque a opção "Usar autenticação" na sidebar
    
    ---
    
    ### 💾 Formatos de Saída
    
    - **CSV**: Melhor para Excel, análise de dados
    - **JSON**: Melhor para APIs, programação
    - **SQLite**: Evita duplicatas, consultas SQL
    
    ---
    
    ### 📝 Dicas
    
    - Use **headless mode** para scraping mais rápido
    - Aumente **scroll pause** se o site for lento
    - Salve em **SQLite** para coletar dados diariamente (evita duplicatas)
    - Use **seletores específicos** para melhor precisão
    
    ---
    
    ### 🐛 Problemas Comuns
    
    **"Nenhum dado coletado"**
    - Os seletores CSS estão incorretos
    - Ajuste os seletores na seção Avançado
    
    **"Site bloqueou"**
    - Aumente o scroll pause
    - Use modo não-headless primeiro
    
    **"Erro ao carregar página"**
    - Verifique se a URL está correta
    - Verifique sua conexão
    """)
    
    st.markdown("---")
    st.info("💡 **Automação via CLI:** Para scripts e cron jobs, use `python3 main.py --help`")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🕷️ **Playwright Web Scraper**")
with col2:
    st.markdown("📦 v1.0.0")
with col3:
    st.markdown("⭐ [GitHub](https://github.com/felipemacedo1/playwright-web-scraper)")
