"""
Main Script - Playwright Web Scraper

Script principal para executar web scraping com Playwright.

Uso básico:
    python main.py --url "https://example.com"
    
Com opções:
    python main.py --url "https://example.com" --headless --refine --output data/results.csv
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from agent.scraper import WebScraper
from agent.storage import save_data
from agent.llm_refiner import refine_data, OPENAI_AVAILABLE

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Web Scraper profissional com Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Scraping básico
  python main.py --url "https://news.ycombinator.com"

  # Com autenticação
  python main.py --url "https://example.com" --use-storage

  # Salvar em CSV e banco
  python main.py --url "https://example.com" --output data/news.csv --database data/news.db

  # Com refinamento de IA
  python main.py --url "https://example.com" --refine --output data/refined.csv

  # Modo headless
  python main.py --url "https://example.com" --headless
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL alvo para scraping'
    )
    
    # Saída
    parser.add_argument(
        '--output',
        type=str,
        default='data/scraped_data.csv',
        help='Caminho do arquivo CSV de saída (padrão: data/scraped_data.csv)'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        help='Caminho do banco SQLite (opcional)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json'],
        default='csv',
        help='Formato do arquivo de saída (padrão: csv)'
    )
    
    # Navegação
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Executa navegador em modo headless (sem interface)'
    )
    
    parser.add_argument(
        '--use-storage',
        action='store_true',
        help='Usa storage_state.json para autenticação'
    )
    
    parser.add_argument(
        '--no-scroll',
        action='store_true',
        help='Não faz scroll automático até o fim da página'
    )
    
    # Limites
    parser.add_argument(
        '--max-items',
        type=int,
        help='Número máximo de itens para coletar'
    )
    
    parser.add_argument(
        '--scroll-pause',
        type=float,
        default=1.0,
        help='Pausa entre scrolls em segundos (padrão: 1.0)'
    )
    
    # Refinamento com IA
    parser.add_argument(
        '--refine',
        action='store_true',
        help='Refina dados coletados com IA (requer OpenAI API key)'
    )
    
    parser.add_argument(
        '--refine-operation',
        type=str,
        choices=['summarize', 'clean', 'extract_points'],
        default='summarize',
        help='Operação de refinamento (padrão: summarize)'
    )
    
    # Outros
    parser.add_argument(
        '--screenshot',
        type=str,
        help='Captura screenshot e salva no caminho especificado'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso (mais logs)'
    )
    
    return parser.parse_args()


def main():
    """Função principal"""
    args = parse_arguments()
    
    # Ajusta nível de log
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("🕷️  PLAYWRIGHT WEB SCRAPER")
    logger.info("=" * 60)
    logger.info(f"URL alvo: {args.url}")
    logger.info(f"Modo headless: {args.headless}")
    logger.info(f"Output: {args.output}")
    
    # Validação
    if not args.url.startswith('http'):
        logger.error("❌ URL inválida. Deve começar com http:// ou https://")
        sys.exit(1)
    
    # Verifica storage_state
    storage_state = None
    if args.use_storage:
        storage_path = Path("storage_state.json")
        if storage_path.exists():
            storage_state = str(storage_path)
            logger.info(f"✅ Usando storage_state: {storage_state}")
        else:
            logger.error(
                "❌ storage_state.json não encontrado!\n"
                "   Execute: python save_storage.py --url <LOGIN_URL>"
            )
            sys.exit(1)
    
    # Verifica OpenAI se --refine
    if args.refine and not OPENAI_AVAILABLE:
        logger.error(
            "❌ OpenAI não disponível!\n"
            "   Execute: pip install openai"
        )
        sys.exit(1)
    
    try:
        # Inicia scraping
        logger.info("\n🚀 Iniciando scraping...")
        
        with WebScraper(headless=args.headless) as scraper:
            # Inicia navegador
            scraper.start(storage_state=storage_state)
            
            # Navega para URL
            if not scraper.navigate(args.url):
                logger.error("❌ Falha ao carregar página")
                sys.exit(1)
            
            # Scroll até o fim (se não desabilitado)
            if not args.no_scroll:
                scraper.scroll_to_bottom(pause_time=args.scroll_pause)
            
            # Captura screenshot (se solicitado)
            if args.screenshot:
                scraper.screenshot(args.screenshot)
            
            # Extrai dados
            data = scraper.extract_data(max_items=args.max_items)
            
            if not data:
                logger.warning("⚠️  Nenhum dado coletado")
                sys.exit(0)
            
            logger.info(f"✅ {len(data)} itens coletados")
            
            # Mostra preview dos primeiros itens
            logger.info("\n📋 Preview dos dados:")
            for i, item in enumerate(data[:3], 1):
                title = item.get('title', 'Sem título')[:60]
                logger.info(f"  {i}. {title}...")
            
            if len(data) > 3:
                logger.info(f"  ... e mais {len(data) - 3} itens")
        
        # Refinamento com IA (opcional)
        if args.refine:
            logger.info(f"\n🤖 Refinando dados com IA ({args.refine_operation})...")
            data = refine_data(
                data,
                field='content',
                operation=args.refine_operation
            )
        
        # Salva dados
        logger.info("\n💾 Salvando dados...")
        save_data(
            data=data,
            output_path=args.output,
            database_path=args.database,
            format=args.format
        )
        
        # Resumo final
        logger.info("\n" + "=" * 60)
        logger.info("✅ SCRAPING CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(f"Total de itens: {len(data)}")
        logger.info(f"Arquivo salvo: {args.output}")
        if args.database:
            logger.info(f"Banco de dados: {args.database}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operação cancelada pelo usuário")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante scraping: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
