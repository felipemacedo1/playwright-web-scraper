"""
Auto-Detect Module

Detecta automaticamente seletores CSS para diferentes sites.
Combina templates conhecidos + heurística inteligente.
"""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# Templates para sites populares
SITE_TEMPLATES = {
    # News & Blogs
    'wikipedia.org': {
        'container': '.mw-parser-output > p, .mw-parser-output > h2, .mw-parser-output > h3',
        'title': '#firstHeading, h1',
        'content': 'p',
        'link': 'a[href]'
    },
    'medium.com': {
        'container': 'article',
        'title': 'h1',
        'author': '[rel="author"], [data-testid="authorName"]',
        'date': 'time',
        'content': 'article p',
        'link': 'a[href]'
    },
    'dev.to': {
        'container': '.crayons-story',
        'title': 'h2, h3',
        'author': '.crayons-story__secondary .crayons-link',
        'date': 'time',
        'content': '.crayons-story__body',
        'link': 'a[href]'
    },
    'reddit.com': {
        'container': '[data-testid="post-container"], .Post',
        'title': 'h3, [data-click-id="text"]',
        'author': '[data-testid="post_author_link"]',
        'date': 'time',
        'content': '[data-test-id="post-content"]',
        'link': 'a[href]'
    },
    'stackoverflow.com': {
        'container': '.question-summary, .answer',
        'title': '.question-hyperlink, h1',
        'author': '.user-details a',
        'date': '.relativetime',
        'content': '.s-prose p',
        'link': 'a.question-hyperlink'
    },
    'github.com': {
        'container': 'article.Box-row, .repo-list li',
        'title': 'h3, h1',
        'author': '[itemprop="author"]',
        'date': 'relative-time',
        'content': 'p.col-9',
        'link': 'a[href]'
    },
    
    # Hacker News (já configurado)
    'news.ycombinator.com': {
        'container': '.athing, tr.athing',
        'title': '.titleline > a',
        'author': '.hnuser',
        'date': '.age',
        'content': '.comment',
        'link': '.titleline > a'
    },
    
    # E-commerce
    'amazon.com': {
        'container': '[data-component-type="s-search-result"], .s-result-item',
        'title': 'h2 a, .s-title-instructions-style',
        'author': '.a-size-base-plus',
        'date': '',
        'content': '.a-size-base-plus',
        'link': 'h2 a'
    },
    'mercadolivre.com.br': {
        'container': '.ui-search-result',
        'title': '.ui-search-item__title',
        'author': '.ui-search-official-store-label',
        'date': '',
        'content': '.ui-search-item__group__element',
        'link': '.ui-search-link'
    },
    
    # News BR
    'g1.globo.com': {
        'container': '.feed-post-body, .widget--info',
        'title': '.feed-post-link, h1',
        'author': '.feed-post-metadata-section',
        'date': '.feed-post-datetime',
        'content': '.feed-post-body-resumo, p',
        'link': '.feed-post-link'
    },
    'uol.com.br': {
        'container': '.thumbnails-item, article',
        'title': '.thumb-title, h1',
        'author': '.author',
        'date': '.time',
        'content': 'p',
        'link': 'a[href]'
    },
    'folha.uol.com.br': {
        'container': '.c-headline, article',
        'title': '.c-headline__title, h1',
        'author': '.c-headline__byline',
        'date': 'time',
        'content': '.c-news__body p',
        'link': '.c-headline__url'
    },
    
    # Tech
    'techcrunch.com': {
        'container': '.post-block, article',
        'title': '.post-block__title, h1',
        'author': '.river-byline__authors',
        'date': 'time',
        'content': '.article-content p',
        'link': '.post-block__title__link'
    },
    'theverge.com': {
        'container': '.duet--content-cards--content-card, article',
        'title': 'h2, h1',
        'author': '.duet--authors--name',
        'date': 'time',
        'content': '.duet--article--article-body-component p',
        'link': 'a[href]'
    }
}


class AutoDetector:
    """Detecta automaticamente seletores CSS para um site"""
    
    def __init__(self, page):
        """
        Args:
            page: Página do Playwright
        """
        self.page = page
        self.url = page.url
        self.domain = self._extract_domain(self.url)
        
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio da URL"""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    
    def detect(self) -> Dict[str, str]:
        """
        Detecta seletores automaticamente.
        
        Returns:
            Dicionário com seletores detectados
        """
        logger.info(f"🔍 Auto-detectando seletores para: {self.domain}")
        
        # 1. Tenta template de site conhecido
        template = self._try_template()
        if template:
            logger.info(f"✅ Template encontrado para {self.domain}")
            return template
        
        # 2. Tenta heurística inteligente
        logger.info("🧠 Usando detecção heurística...")
        heuristic = self._heuristic_detection()
        
        return heuristic
    
    def _try_template(self) -> Optional[Dict[str, str]]:
        """
        Tenta encontrar template para o domínio.
        
        Returns:
            Template se encontrado, None caso contrário
        """
        # Busca exata
        if self.domain in SITE_TEMPLATES:
            return SITE_TEMPLATES[self.domain].copy()
        
        # Busca parcial (ex: en.wikipedia.org -> wikipedia.org)
        for template_domain in SITE_TEMPLATES:
            if template_domain in self.domain:
                logger.info(f"📌 Match parcial: {template_domain}")
                return SITE_TEMPLATES[template_domain].copy()
        
        return None
    
    def _heuristic_detection(self) -> Dict[str, str]:
        """
        Detecta seletores usando heurística.
        
        Estratégia:
        1. Tenta tags semânticas (article, section)
        2. Tenta classes comuns (post, card, item)
        3. Analisa estrutura do DOM
        4. Fallback para padrões genéricos
        """
        selectors = {
            'container': '',
            'title': '',
            'author': '',
            'date': '',
            'content': '',
            'link': 'a[href]'
        }
        
        # 1. Detecta container
        selectors['container'] = self._detect_container()
        
        # 2. Detecta título (relativo ao container)
        selectors['title'] = self._detect_title()
        
        # 3. Detecta autor
        selectors['author'] = self._detect_author()
        
        # 4. Detecta data
        selectors['date'] = self._detect_date()
        
        # 5. Detecta conteúdo
        selectors['content'] = self._detect_content()
        
        return selectors
    
    def _detect_container(self) -> str:
        """Detecta seletor de container principal"""
        
        # Prioridade: tags semânticas
        semantic_tags = ['article', 'section[class*="post"]', 'section[class*="item"]']
        
        for tag in semantic_tags:
            count = len(self.page.query_selector_all(tag))
            if 3 <= count <= 100:  # Range razoável de items
                logger.info(f"📦 Container detectado: {tag} ({count} elementos)")
                return tag
        
        # Classes comuns
        common_classes = [
            '.post', '.card', '.item', '.entry', '.article-item',
            '[class*="post"]', '[class*="card"]', '[class*="item"]',
            '[class*="story"]', '[class*="content-item"]'
        ]
        
        for selector in common_classes:
            try:
                count = len(self.page.query_selector_all(selector))
                if 3 <= count <= 100:
                    logger.info(f"📦 Container detectado: {selector} ({count} elementos)")
                    return selector
            except:
                continue
        
        # Fallback: div com múltiplos filhos
        logger.warning("⚠️ Container não detectado, usando fallback")
        return 'article, .post, .card, .item, .entry, section[class*="post"]'
    
    def _detect_title(self) -> str:
        """Detecta seletor de título"""
        
        # Headings são o mais comum
        headings = ['h1', 'h2', 'h3']
        
        for heading in headings:
            count = len(self.page.query_selector_all(heading))
            if count > 0:
                logger.info(f"📝 Título detectado: {heading}")
                return heading
        
        # Classes comuns
        title_classes = ['.title', '.headline', '[class*="title"]', '[class*="heading"]']
        
        for selector in title_classes:
            try:
                count = len(self.page.query_selector_all(selector))
                if count > 0:
                    logger.info(f"📝 Título detectado: {selector}")
                    return selector
            except:
                continue
        
        # Fallback
        return 'h1, h2, h3, .title, .headline'
    
    def _detect_author(self) -> str:
        """Detecta seletor de autor"""
        
        author_selectors = [
            '.author', '.byline', '[class*="author"]',
            '[rel="author"]', '[itemprop="author"]',
            '.meta-author', '.writer'
        ]
        
        for selector in author_selectors:
            try:
                count = len(self.page.query_selector_all(selector))
                if count > 0:
                    logger.info(f"👤 Autor detectado: {selector}")
                    return selector
            except:
                continue
        
        return '.author, .byline, [rel="author"]'
    
    def _detect_date(self) -> str:
        """Detecta seletor de data"""
        
        date_selectors = [
            'time', '[datetime]', '.date', '.published',
            '[class*="date"]', '[class*="time"]',
            '.meta-date', '.timestamp'
        ]
        
        for selector in date_selectors:
            try:
                count = len(self.page.query_selector_all(selector))
                if count > 0:
                    logger.info(f"📅 Data detectada: {selector}")
                    return selector
            except:
                continue
        
        return 'time, .date, .published'
    
    def _detect_content(self) -> str:
        """Detecta seletor de conteúdo"""
        
        content_selectors = [
            '.content', '.description', '.summary', '.excerpt',
            '[class*="content"]', '[class*="description"]',
            'p', '.text'
        ]
        
        for selector in content_selectors:
            try:
                count = len(self.page.query_selector_all(selector))
                if count > 0:
                    logger.info(f"📄 Conteúdo detectado: {selector}")
                    return selector
            except:
                continue
        
        return '.content, .description, .summary, p'


def auto_detect_selectors(page) -> Dict[str, str]:
    """
    Função helper para auto-detecção.
    
    Args:
        page: Página do Playwright
        
    Returns:
        Dicionário com seletores detectados
    """
    detector = AutoDetector(page)
    return detector.detect()
