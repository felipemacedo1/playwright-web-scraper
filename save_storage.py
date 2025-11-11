"""
Save Storage State Script

Script para gerar arquivo storage_state.json através de login manual.
Útil para sites que requerem autenticação.

Uso:
    python save_storage.py --url "https://example.com/login"
    
O navegador abrirá. Faça login manualmente e feche o navegador.
O estado de autenticação será salvo em storage_state.json
"""

import argparse
import logging
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_storage_state(url: str, output_path: str = "storage_state.json"):
    """
    Abre navegador para login manual e salva estado de autenticação.
    
    Args:
        url: URL da página de login
        output_path: Caminho para salvar o storage_state.json
    """
    logger.info(f"Abrindo navegador para login em: {url}")
    logger.info("⚠️  Faça login manualmente e depois FECHE o navegador")
    
    with sync_playwright() as p:
        # Inicia navegador em modo visível
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        try:
            # Navega para página de login
            page.goto(url)
            
            # Aguarda usuário fechar o navegador
            logger.info("✋ Aguardando você fazer login e fechar o navegador...")
            page.wait_for_event("close", timeout=0)  # Sem timeout
            
        except Exception as e:
            logger.info("Navegador fechado pelo usuário")
        
        finally:
            # Salva estado de autenticação
            try:
                context.storage_state(path=output_path)
                logger.info(f"✅ Estado de autenticação salvo em: {output_path}")
                logger.info(f"📝 Tamanho: {Path(output_path).stat().st_size} bytes")
                
                # Dica de uso
                logger.info("\n💡 Para usar este storage_state, execute:")
                logger.info(f"   python main.py --url <URL> --use-storage")
                
            except Exception as e:
                logger.error(f"❌ Erro ao salvar storage_state: {str(e)}")
                sys.exit(1)
            
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Salva estado de autenticação após login manual"
    )
    
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL da página de login'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='storage_state.json',
        help='Caminho do arquivo de saída (padrão: storage_state.json)'
    )
    
    args = parser.parse_args()
    
    # Validação
    if not args.url.startswith('http'):
        logger.error("❌ URL inválida. Deve começar com http:// ou https://")
        sys.exit(1)
    
    # Executa
    try:
        save_storage_state(args.url, args.output)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
