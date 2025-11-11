"""
LLM Refiner Module

Módulo opcional para refinar dados coletados usando IA (OpenAI).
Útil para:
- Limpar e formatar texto
- Extrair informações específicas
- Resumir conteúdo
- Classificar ou categorizar dados
"""

import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI não instalado. Execute: pip install openai")


class LLMRefiner:
    """
    Refina dados coletados usando modelos de linguagem (OpenAI).
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3
    ):
        """
        Inicializa o refinador.
        
        Args:
            api_key: Chave da API OpenAI (ou usa OPENAI_API_KEY do .env)
            model: Modelo a usar (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
            temperature: Criatividade (0-1, menor = mais determinístico)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI não instalado. Execute: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key da OpenAI não encontrada. "
                "Configure OPENAI_API_KEY no .env ou passe como parâmetro"
            )
        
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f"LLM Refiner inicializado com modelo: {model}")
    
    def refine_text(self, text: str, instruction: str) -> str:
        """
        Refina um texto usando instrução customizada.
        
        Args:
            text: Texto original
            instruction: Instrução de como refinar
            
        Returns:
            Texto refinado
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente que refina e melhora textos."
                    },
                    {
                        "role": "user",
                        "content": f"{instruction}\n\nTexto:\n{text}"
                    }
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao refinar texto: {str(e)}")
            return text  # Retorna original em caso de erro
    
    def summarize(self, text: str, max_words: int = 100) -> str:
        """
        Resume um texto.
        
        Args:
            text: Texto para resumir
            max_words: Número máximo de palavras
            
        Returns:
            Resumo do texto
        """
        instruction = f"Resuma este texto em no máximo {max_words} palavras:"
        return self.refine_text(text, instruction)
    
    def extract_key_points(self, text: str, num_points: int = 3) -> List[str]:
        """
        Extrai pontos principais de um texto.
        
        Args:
            text: Texto para analisar
            num_points: Número de pontos a extrair
            
        Returns:
            Lista de pontos principais
        """
        instruction = (
            f"Extraia os {num_points} pontos principais deste texto. "
            "Retorne apenas uma lista numerada, sem introdução."
        )
        
        result = self.refine_text(text, instruction)
        
        # Parse da resposta em lista
        points = []
        for line in result.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numeração e adiciona
                clean_line = line.lstrip('0123456789.-) ').strip()
                if clean_line:
                    points.append(clean_line)
        
        return points
    
    def clean_content(self, text: str) -> str:
        """
        Limpa e formata um texto (remove ruído, corrige formatação).
        
        Args:
            text: Texto para limpar
            
        Returns:
            Texto limpo
        """
        instruction = (
            "Limpe este texto removendo caracteres especiais desnecessários, "
            "corrigindo formatação e mantendo apenas o conteúdo relevante:"
        )
        return self.refine_text(text, instruction)
    
    def refine_batch(
        self,
        data: List[Dict[str, str]],
        field: str = 'content',
        operation: str = 'summarize'
    ) -> List[Dict[str, str]]:
        """
        Refina múltiplos itens de dados.
        
        Args:
            data: Lista de dicionários com os dados
            field: Campo a ser refinado
            operation: Operação ('summarize', 'clean', 'extract_points')
            
        Returns:
            Lista de dados refinados
        """
        logger.info(f"Refinando {len(data)} itens (operação: {operation})...")
        
        refined_data = []
        
        for idx, item in enumerate(data, 1):
            try:
                text = item.get(field, '')
                
                if not text:
                    logger.warning(f"Item {idx}: campo '{field}' vazio")
                    refined_data.append(item)
                    continue
                
                # Aplica operação
                if operation == 'summarize':
                    refined_text = self.summarize(text)
                    item[f'{field}_summary'] = refined_text
                    
                elif operation == 'clean':
                    refined_text = self.clean_content(text)
                    item[f'{field}_cleaned'] = refined_text
                    
                elif operation == 'extract_points':
                    points = self.extract_key_points(text)
                    item[f'{field}_key_points'] = ' | '.join(points)
                
                refined_data.append(item)
                logger.debug(f"Item {idx}/{len(data)} refinado")
                
            except Exception as e:
                logger.error(f"Erro ao refinar item {idx}: {str(e)}")
                refined_data.append(item)  # Mantém original
        
        logger.info(f"✅ Refinamento concluído: {len(refined_data)} itens processados")
        return refined_data


def refine_data(
    data: List[Dict[str, str]],
    field: str = 'content',
    operation: str = 'summarize'
) -> List[Dict[str, str]]:
    """
    Função helper para refinamento de dados.
    
    Args:
        data: Lista de dicionários com os dados
        field: Campo a ser refinado
        operation: Operação ('summarize', 'clean', 'extract_points')
        
    Returns:
        Lista de dados refinados
    """
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI não disponível. Retornando dados originais.")
        return data
    
    try:
        refiner = LLMRefiner()
        return refiner.refine_batch(data, field=field, operation=operation)
    except Exception as e:
        logger.error(f"Erro no refinamento: {str(e)}")
        return data
