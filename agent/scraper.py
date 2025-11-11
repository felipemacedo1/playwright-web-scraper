"""
Web Scraper Module

Módulo principal de scraping usando Playwright.
Coleta dados de páginas web de forma automatizada e robusta.
"""

import logging
import time
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Scraper web usando Playwright (modo síncrono).
    
    Recursos:
    - Suporte a login com storage_state
    - Scroll automático até o fim da página
    - Extração genérica de dados
    - Tratamento de erros robusto
    """
    
    # Seletores genéricos (ajuste para cada site específico)
    SELECTORS = {
        'container': 'article, .post, .card, .item, .news-item',
        'title': 'h1, h2, h3, .title, .headline',
        'author': '.author, .byline, [rel="author"]',
        'date': 'time, .date, .published',
        'content': '.content, .description, .summary, p',
        'link': 'a[href]',
    }
    
    def __init__(
        self,
        headless: bool = False,
        browser_type: str = "chromium",
        viewport: Dict[str, int] = None,
        user_agent: str = None,
        timeout: int = 30000
    ):
        """
        Inicializa o scraper.
        
        Args:
            headless: Se True, executa sem interface gráfica
            browser_type: Tipo do navegador (chromium, firefox, webkit)
            viewport: Dimensões da janela {'width': 1920, 'height': 1080}
            user_agent: User-Agent customizado
            timeout: Timeout padrão em milissegundos
        """
        self.headless = headless
        self.browser_type = browser_type
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.user_agent = user_agent
        self.timeout = timeout
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def start(self, storage_state: Optional[str] = None):
        """
        Inicia o navegador e cria uma nova página.
        
        Args:
            storage_state: Caminho para arquivo JSON com cookies/auth
        """
        logger.info(f"Iniciando navegador {self.browser_type} (headless={self.headless})")
        
        self.playwright = sync_playwright().start()
        
        # Seleciona o tipo de navegador
        if self.browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"Tipo de navegador inválido: {self.browser_type}")
        
        # Cria contexto do navegador (com ou sem storage_state)
        context_options = {
            "viewport": self.viewport,
        }
        
        if self.user_agent:
            context_options["user_agent"] = self.user_agent
            
        if storage_state:
            logger.info(f"Carregando storage_state de: {storage_state}")
            context_options["storage_state"] = storage_state
        
        self.context = self.browser.new_context(**context_options)
        self.context.set_default_timeout(self.timeout)
        
        # Cria nova página
        self.page = self.context.new_page()
        logger.info("Navegador iniciado com sucesso")
        
    def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navega para uma URL.
        
        Args:
            url: URL de destino
            wait_until: Condição de espera (load, domcontentloaded, networkidle)
            
        Returns:
            True se navegação bem-sucedida, False caso contrário
        """
        logger.info(f"Navegando para: {url}")
        
        try:
            response = self.page.goto(url, wait_until=wait_until)
            
            if response and response.ok:
                logger.info(f"Página carregada: {self.page.title()} (status {response.status})")
                return True
            else:
                status = response.status if response else "N/A"
                logger.error(f"Falha ao carregar página (status {status})")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao navegar: {str(e)}")
            return False
    
    def scroll_to_bottom(self, pause_time: float = 1.0, max_scrolls: int = 50):
        """
        Scrolla até o final da página para carregar conteúdo dinâmico.
        
        Args:
            pause_time: Pausa entre scrolls (segundos)
            max_scrolls: Número máximo de tentativas de scroll
        """
        logger.info("Iniciando scroll até o fim da página...")
        
        last_height = self.page.evaluate("document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scrolla até o fim
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Aguarda carregamento
            time.sleep(pause_time)
            
            # Calcula nova altura
            new_height = self.page.evaluate("document.body.scrollHeight")
            
            # Se não mudou, chegamos ao fim
            if new_height == last_height:
                logger.info(f"Fim da página alcançado após {scrolls} scrolls")
                break
                
            last_height = new_height
            scrolls += 1
            
            logger.debug(f"Scroll {scrolls}/{max_scrolls} - Altura: {new_height}px")
        
        if scrolls >= max_scrolls:
            logger.warning(f"Limite de scrolls atingido ({max_scrolls})")
    
    def extract_data(self, max_items: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Extrai dados da página usando seletores genéricos.
        
        Args:
            max_items: Número máximo de itens para extrair
            
        Returns:
            Lista de dicionários com os dados coletados
        """
        logger.info("Iniciando extração de dados...")
        
        data = []
        
        try:
            # Busca todos os containers de conteúdo
            containers = self.page.query_selector_all(self.SELECTORS['container'])
            logger.info(f"Encontrados {len(containers)} containers na página")
            
            # Limita quantidade se especificado
            if max_items:
                containers = containers[:max_items]
            
            for idx, container in enumerate(containers, 1):
                try:
                    item = self._extract_item_data(container)
                    
                    # Só adiciona se tiver pelo menos título ou link
                    if item.get('title') or item.get('link'):
                        data.append(item)
                        logger.debug(f"Item {idx} extraído: {item.get('title', 'Sem título')[:50]}")
                    
                except Exception as e:
                    logger.warning(f"Erro ao extrair item {idx}: {str(e)}")
                    continue
            
            logger.info(f"Extração concluída: {len(data)} itens coletados")
            
        except Exception as e:
            logger.error(f"Erro durante extração de dados: {str(e)}")
        
        return data
    
    def _extract_item_data(self, container) -> Dict[str, str]:
        """
        Extrai dados de um container específico.
        
        Args:
            container: ElementHandle do container
            
        Returns:
            Dicionário com os dados extraídos
        """
        item = {}
        
        # Extrai título
        title_el = container.query_selector(self.SELECTORS['title'])
        if title_el:
            item['title'] = title_el.inner_text().strip()
        
        # Extrai autor
        author_el = container.query_selector(self.SELECTORS['author'])
        if author_el:
            item['author'] = author_el.inner_text().strip()
        
        # Extrai data
        date_el = container.query_selector(self.SELECTORS['date'])
        if date_el:
            # Tenta pegar atributo datetime primeiro
            date_value = date_el.get_attribute('datetime')
            if not date_value:
                date_value = date_el.inner_text().strip()
            item['date'] = date_value
        
        # Extrai conteúdo/descrição
        content_el = container.query_selector(self.SELECTORS['content'])
        if content_el:
            item['content'] = content_el.inner_text().strip()
        
        # Extrai link
        link_el = container.query_selector(self.SELECTORS['link'])
        if link_el:
            href = link_el.get_attribute('href')
            if href:
                # Converte link relativo em absoluto
                item['link'] = self.page.evaluate(
                    f"new URL('{href}', window.location.href).href"
                )
        
        return item
    
    def screenshot(self, path: str = "screenshot.png"):
        """
        Captura screenshot da página atual.
        
        Args:
            path: Caminho para salvar a imagem
        """
        try:
            self.page.screenshot(path=path, full_page=True)
            logger.info(f"Screenshot salvo em: {path}")
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {str(e)}")
    
    def close(self):
        """Fecha o navegador e libera recursos"""
        logger.info("Fechando navegador...")
        
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
        logger.info("Navegador fechado")


def scrape(
    url: str,
    headless: bool = False,
    storage_state: Optional[str] = None,
    scroll: bool = True,
    max_items: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Função helper para scraping simples.
    
    Args:
        url: URL alvo
        headless: Se True, executa sem interface
        storage_state: Caminho para arquivo de autenticação
        scroll: Se True, scrolla até o fim da página
        max_items: Número máximo de itens
        
    Returns:
        Lista de dicionários com dados coletados
    """
    with WebScraper(headless=headless) as scraper:
        scraper.start(storage_state=storage_state)
        
        if not scraper.navigate(url):
            return []
        
        if scroll:
            scraper.scroll_to_bottom()
        
        return scraper.extract_data(max_items=max_items)
