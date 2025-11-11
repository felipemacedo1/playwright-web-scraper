"""
Storage Module

Módulo para salvar dados coletados em diferentes formatos:
- CSV
- SQLite
- JSON
"""

import csv
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class CSVStorage:
    """Gerencia salvamento de dados em formato CSV"""
    
    @staticmethod
    def save(data: List[Dict[str, str]], output_path: str, append: bool = False):
        """
        Salva dados em arquivo CSV.
        
        Args:
            data: Lista de dicionários com os dados
            output_path: Caminho do arquivo de saída
            append: Se True, adiciona ao arquivo existente
        """
        if not data:
            logger.warning("Nenhum dado para salvar")
            return
        
        # Cria diretório se não existir
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'a' if append else 'w'
        
        try:
            # Pega todas as chaves únicas dos dados
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)
            
            with open(output_path, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Escreve cabeçalho se for novo arquivo
                if mode == 'w':
                    writer.writeheader()
                
                writer.writerows(data)
            
            logger.info(f"✅ {len(data)} itens salvos em: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar CSV: {str(e)}")
            raise


class SQLiteStorage:
    """Gerencia salvamento de dados em banco SQLite"""
    
    def __init__(self, db_path: str):
        """
        Inicializa conexão com banco de dados.
        
        Args:
            db_path: Caminho do arquivo SQLite
        """
        self.db_path = db_path
        
        # Cria diretório se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self._create_table()
        
    def _create_table(self):
        """Cria tabela se não existir"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                date TEXT,
                link TEXT UNIQUE,
                content TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        logger.info(f"Tabela 'scraped_data' pronta no banco: {self.db_path}")
    
    def save(self, data: List[Dict[str, str]]):
        """
        Salva dados no banco SQLite.
        
        Args:
            data: Lista de dicionários com os dados
        """
        if not data:
            logger.warning("Nenhum dado para salvar")
            return
        
        inserted = 0
        duplicates = 0
        errors = 0
        
        for item in data:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO scraped_data 
                    (title, author, date, link, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item.get('title'),
                    item.get('author'),
                    item.get('date'),
                    item.get('link'),
                    item.get('content')
                ))
                
                if self.cursor.rowcount > 0:
                    inserted += 1
                else:
                    duplicates += 1
                    
            except sqlite3.IntegrityError:
                duplicates += 1
            except Exception as e:
                logger.warning(f"Erro ao inserir item: {str(e)}")
                errors += 1
        
        self.conn.commit()
        
        logger.info(
            f"✅ Banco atualizado: {inserted} novos | "
            f"{duplicates} duplicados | {errors} erros"
        )
    
    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retorna todos os registros do banco.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de dicionários com os dados
        """
        query = "SELECT * FROM scraped_data ORDER BY scraped_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def count(self) -> int:
        """Retorna total de registros"""
        self.cursor.execute("SELECT COUNT(*) FROM scraped_data")
        return self.cursor.fetchone()[0]
    
    def close(self):
        """Fecha conexão com banco"""
        self.conn.close()
        logger.info(f"Conexão com banco fechada: {self.db_path}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class JSONStorage:
    """Gerencia salvamento de dados em formato JSON"""
    
    @staticmethod
    def save(data: List[Dict[str, str]], output_path: str, indent: int = 2):
        """
        Salva dados em arquivo JSON.
        
        Args:
            data: Lista de dicionários com os dados
            output_path: Caminho do arquivo de saída
            indent: Indentação do JSON (None para minificado)
        """
        if not data:
            logger.warning("Nenhum dado para salvar")
            return
        
        # Cria diretório se não existir
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Adiciona metadata
            output = {
                "scraped_at": datetime.now().isoformat(),
                "total_items": len(data),
                "data": data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=indent)
            
            logger.info(f"✅ {len(data)} itens salvos em: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON: {str(e)}")
            raise
    
    @staticmethod
    def load(input_path: str) -> List[Dict[str, str]]:
        """
        Carrega dados de arquivo JSON.
        
        Args:
            input_path: Caminho do arquivo JSON
            
        Returns:
            Lista de dicionários com os dados
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Se tiver estrutura com metadata, retorna só os dados
            if isinstance(content, dict) and 'data' in content:
                return content['data']
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar JSON: {str(e)}")
            return []


def save_data(
    data: List[Dict[str, str]],
    output_path: Optional[str] = None,
    database_path: Optional[str] = None,
    format: str = 'csv'
):
    """
    Função helper para salvar dados em múltiplos formatos.
    
    Args:
        data: Lista de dicionários com os dados
        output_path: Caminho do arquivo CSV/JSON
        database_path: Caminho do banco SQLite
        format: Formato do arquivo ('csv' ou 'json')
    """
    if not data:
        logger.warning("Nenhum dado para salvar")
        return
    
    # Salva em arquivo (CSV ou JSON)
    if output_path:
        if format == 'csv':
            CSVStorage.save(data, output_path)
        elif format == 'json':
            JSONStorage.save(data, output_path)
        else:
            logger.error(f"Formato inválido: {format}")
    
    # Salva em banco SQLite
    if database_path:
        with SQLiteStorage(database_path) as db:
            db.save(data)
