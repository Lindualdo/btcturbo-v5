# source: app/services/dashboards/dash_main/helpers/data_helper.py

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query
import pytz

logger = logging.getLogger(__name__)

def save_dashboard(dashboard_data: Dict) -> bool:
    """
    Salva dashboard  no PostgreSQL
    """
    try:
        logger.info("💾 Salvando Dashboard...")
        
        _create_table_if_not_exists()
        
        campos = dashboard_data["campos"]
        dashboard_json = dashboard_data["json"]
        timestamp_lisboa = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            INSERT INTO dash_main (
                btc_price, score_mercado, score_risco, ciclo_atual, 
                setup, decisao_final, alavancagem_atual, health_factor,
                ema_distance, rsi_diario, dashboard_json, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            campos["btc_price"],
            campos["score_mercado"], 
            campos["score_risco"],
            campos["ciclo_atual"],
            campos["setup"],
            campos["decisao_final"],
            campos["alavancagem_atual"],
            campos["health_factor"],
            campos["ema_distance"],
            campos["rsi_diario"],
            json.dumps(dashboard_json),
            timestamp_lisboa
        )
        
        execute_query(query, valores)
        logger.info("✅ Dashboard salvo com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro salvando Dashboard: {str(e)}")
        return False

def get_latest_dashboard() -> Optional[Dict]:
    """
    Busca último dashboard
    """
    try:
        logger.info("🔍 Buscando último Dashboard...")
        
        query = """
            SELECT * FROM dash_main 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard encontrado: ID {result['id']}")
            return result
        else:
            logger.warning("⚠️ Nenhum Dashboard encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro buscar Dashboard: {str(e)}")
        return None

def _create_table_if_not_exists():
    """
    Cria tabela se não existir (mesma da V2)
    """
    try:
        query = """
            CREATE TABLE IF NOT EXISTS dash_main (
                id SERIAL PRIMARY KEY,
                btc_price DECIMAL(12,2),
                score_mercado DECIMAL(5,2),
                score_risco DECIMAL(5,2),
                ciclo_atual VARCHAR(50),
                setup_ VARCHAR(100),
                decisao_final VARCHAR(100),
                alavancagem_atual DECIMAL(5,2),
                health_factor DECIMAL(8,6),
                ema_distance DECIMAL(5,2),
                rsi_diario DECIMAL(5,2),
                dashboard_json JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        execute_query(query)
        logger.info("✅ Tabela dashboard_decisao_v2 verificada")
        
    except Exception as e:
        logger.error(f"❌ Erro criar tabela: {str(e)}")
        raise