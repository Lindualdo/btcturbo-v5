# app/services/utils/helpers/postgres/tecnico_helper.py - ATUALIZADO

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from ..base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_tecnico_completo(dados: Dict) -> bool:
    """
    Insere dados técnicos completos com EMAs, BBW e scores calculados
    """
    try:
        logger.info("💾 Inserindo dados técnico completos com BBW...")
        
        # Converter distancias_json para string JSON
        distancias_json_str = json.dumps(dados.get("distancias_json", {}))
        
        query = """
            INSERT INTO indicadores_tecnico (
                -- EMAs Semanal (1W)
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                -- EMAs Diário (1D)
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                -- Preço atual
                btc_price_current,
                -- Scores individuais EMAs
                score_1w_ema, score_1w_price, score_1d_ema, score_1d_price,
                -- Scores consolidados EMAs
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
                -- BBW (NOVO)
                bbw_percentage, score_bbw,
                -- Score final do bloco (NOVO)
                score_bloco_final,
                -- Compatibilidade (usar score final como sistema_emas)
                sistema_emas, padroes_graficos,
                -- Metadados
                distancias_json, fonte, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s,  -- EMAs 1W
                %s, %s, %s, %s, %s,  -- EMAs 1D
                %s,                  -- BTC price
                %s, %s, %s, %s,      -- Scores individuais
                %s, %s, %s,          -- Scores consolidados EMAs
                %s, %s,              -- BBW (NOVO)
                %s,                  -- Score bloco final (NOVO)
                %s, %s,              -- Compatibilidade
                %s, %s, %s           -- Metadados
            )
        """
        
        params = (
            # EMAs Semanal
            dados.get("ema_17_1w"),
            dados.get("ema_34_1w"), 
            dados.get("ema_144_1w"),
            dados.get("ema_305_1w"),
            dados.get("ema_610_1w"),
            
            # EMAs Diário
            dados.get("ema_17_1d"),
            dados.get("ema_34_1d"),
            dados.get("ema_144_1d"), 
            dados.get("ema_305_1d"),
            dados.get("ema_610_1d"),
            
            # Preço atual
            dados.get("btc_price_current"),
            
            # Scores individuais
            dados.get("score_1w_ema"),
            dados.get("score_1w_price"),
            dados.get("score_1d_ema"),
            dados.get("score_1d_price"),
            
            # Scores consolidados EMAs
            dados.get("score_consolidado_1w"),
            dados.get("score_consolidado_1d"),
            dados.get("score_final_ponderado"),
            
            # BBW (NOVO)
            dados.get("bbw_percentage"),
            dados.get("score_bbw"),
            
            # Score final do bloco (NOVO)
            dados.get("score_bloco_final"),
            
            # Compatibilidade (campos legados)
            dados.get("score_bloco_final"),  # sistema_emas = score final do bloco
            0.0,                             # padroes_graficos = 0 (descontinuado)
            
            # Metadados
            distancias_json_str,
            dados.get("fonte", "tvdatafeed_emas_bbw"),
            dados.get("timestamp", datetime.utcnow())
        )
        
        execute_query(query, params)
        logger.info("✅ Dados técnico completos com BBW inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico: {str(e)}")
        return False

def get_dados_tecnico() -> Optional[Dict]:
    """
    Busca dados mais recentes do bloco técnico (ATUALIZADO para BBW)
    """
    try:
        logger.info("🔍 Buscando dados do bloco TÉCNICO...")
        
        query = """
            SELECT 
                -- EMAs Semanal
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                -- EMAs Diário  
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                -- Preço e scores EMAs
                btc_price_current,
                score_1w_ema, score_1w_price, score_1d_ema, score_1d_price,
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
                -- BBW (NOVO)
                bbw_percentage, score_bbw,
                -- Score final do bloco (NOVO)
                score_bloco_final,
                -- Campos legados (compatibilidade)
                sistema_emas, padroes_graficos,
                -- Metadados
                distancias_json, timestamp, fonte, metadados
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados técnico encontrados: score_bloco={result.get('score_bloco_final')}, bbw={result.get('bbw_percentage')}%, timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_tecnico")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco técnico: {str(e)}")
        return None

def get_emas_detalhadas() -> Optional[Dict]:
    """
    Busca EMAs detalhadas por timeframe (ATUALIZADO para incluir BBW)
    """
    try:
        logger.info("🔍 Buscando EMAs detalhadas com BBW...")
        
        query = """
            SELECT 
                -- EMAs Semanal
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                score_1w_ema, score_1w_price, score_consolidado_1w,
                -- EMAs Diário
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                score_1d_ema, score_1d_price, score_consolidado_1d,
                -- Geral
                btc_price_current, score_final_ponderado,
                -- BBW (NOVO)
                bbw_percentage, score_bbw,
                -- Score final do bloco (NOVO)
                score_bloco_final,
                -- Metadados
                distancias_json, timestamp, fonte
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            # Estruturar dados por timeframe + BBW
            dados_estruturados = {
                "semanal": {
                    "emas": {
                        "17": float(result["ema_17_1w"]) if result["ema_17_1w"] else None,
                        "34": float(result["ema_34_1w"]) if result["ema_34_1w"] else None,
                        "144": float(result["ema_144_1w"]) if result["ema_144_1w"] else None,
                        "305": float(result["ema_305_1w"]) if result["ema_305_1w"] else None,
                        "610": float(result["ema_610_1w"]) if result["ema_610_1w"] else None
                    },
                    "scores": {
                        "alinhamento": float(result["score_1w_ema"]) if result["score_1w_ema"] else 0,
                        "posicao": float(result["score_1w_price"]) if result["score_1w_price"] else 0,
                        "consolidado": float(result["score_consolidado_1w"]) if result["score_consolidado_1w"] else 0
                    },
                    "peso": 0.7
                },
                "diario": {
                    "emas": {
                        "17": float(result["ema_17_1d"]) if result["ema_17_1d"] else None,
                        "34": float(result["ema_34_1d"]) if result["ema_34_1d"] else None,
                        "144": float(result["ema_144_1d"]) if result["ema_144_1d"] else None,
                        "305": float(result["ema_305_1d"]) if result["ema_305_1d"] else None,
                        "610": float(result["ema_610_1d"]) if result["ema_610_1d"] else None
                    },
                    "scores": {
                        "alinhamento": float(result["score_1d_ema"]) if result["score_1d_ema"] else 0,
                        "posicao": float(result["score_1d_price"]) if result["score_1d_price"] else 0,
                        "consolidado": float(result["score_consolidado_1d"]) if result["score_consolidado_1d"] else 0
                    },
                    "peso": 0.3
                },
                "geral": {
                    "btc_price": float(result["btc_price_current"]) if result["btc_price_current"] else 0,
                    "score_emas": float(result["score_final_ponderado"]) if result["score_final_ponderado"] else 0,
                    "score_bloco_final": float(result["score_bloco_final"]) if result["score_bloco_final"] else 0,
                    "timestamp": result["timestamp"],
                    "fonte": result["fonte"]
                },
                # BBW (NOVO)
                "bbw": {
                    "percentage": float(result["bbw_percentage"]) if result["bbw_percentage"] else 0,
                    "score": float(result["score_bbw"]) if result["score_bbw"] else 0,
                    "peso": 0.3
                },
                "distancias": result["distancias_json"] if result["distancias_json"] else {}
            }
            
            logger.info(f"✅ EMAs detalhadas com BBW encontradas: score_bloco={dados_estruturados['geral']['score_bloco_final']}")
            return dados_estruturados
        else:
            logger.warning("⚠️ Nenhuma EMA detalhada encontrada")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar EMAs detalhadas: {str(e)}")
        return None

def get_historico_tecnico(limit: int = 10) -> list:
    """Busca histórico de dados do bloco técnico (ATUALIZADO)"""
    try:
        logger.info(f"📊 Buscando histórico do bloco TÉCNICO (últimos {limit} registros)")
        
        query = """
            SELECT 
                score_bloco_final, score_final_ponderado, score_bbw, bbw_percentage,
                score_consolidado_1w, score_consolidado_1d,
                btc_price_current, sistema_emas, padroes_graficos,
                timestamp, fonte
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        result = execute_query(query, params=(limit,), fetch_all=True)
        
        if result:
            logger.info(f"✅ {len(result)} registros históricos encontrados")
            return result
        else:
            logger.warning("⚠️ Nenhum histórico encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico técnico: {str(e)}")
        return []

# Função legada mantida para compatibilidade
def insert_dados_tecnico(sistema_emas: float, padroes: float, fonte: str = "Sistema") -> bool:
    """
    Função legada mantida para compatibilidade
    """
    try:
        logger.info(f"💾 Inserindo dados técnico legados: EMAs={sistema_emas}, Padrões={padroes}")
        
        query = """
            INSERT INTO indicadores_tecnico (sistema_emas, padroes_graficos, fonte, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        params = (sistema_emas, padroes, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados técnico legados inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico legados: {str(e)}")
        return False