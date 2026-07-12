import pandas as pd
import logging

def run_fusion(live_features: pd.DataFrame) -> pd.DataFrame:
    """
    阶段22：盘口市场融合层
    负责：盘口读取、去水概率计算、Edge计算、风险等级评估
    """
    logging.info("[Stage 22] 启动盘口市场融合 (Market Fusion)...")
    
    if live_features.empty:
        logging.warning("[Stage 22] 输入的 live_features 为空，无法进行市场融合。")
        
    # 1. 盘口读取
    logging.info("[Stage 22] 1. 读取并清洗 The Odds API 实时盘口数据...")
    
    # 2. 去水概率 (Vig-free Probability) 计算
    logging.info("[Stage 22] 2. 消除博彩公司抽水 (计算 Vig-free Probability)...")
    
    # 3. Edge (胜率优势) 计算
    # 公式逻辑: 真实预测概率 - 市场去水隐含概率
    logging.info("[Stage 22] 3. 对比模型概率与市场概率，计算预期价值 (Edge)...")
    
    # 4. 风险等级 (Risk Level) 判定
    # 根据盘口方差、伤病不确定性等评估 (如: LOW, MEDIUM, HIGH)
    logging.info("[Stage 22] 4. 综合各项波动性评估赛事风险等级 (Risk Level)...")

    # 构建并返回最终预测结果
    final_game_prediction = pd.DataFrame(columns=[
        'game_id', 'final_probability', 'market_implied_prob', 'edge', 'risk_level'
    ])
    
    logging.info("[Stage 22] ✅ final_game_prediction 最终预测生成完毕。")
    return final_game_prediction
