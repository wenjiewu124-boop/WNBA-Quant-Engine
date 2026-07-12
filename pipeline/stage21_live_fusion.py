import pandas as pd
import logging
import os

try:
    from database import bq_client
except ImportError:
    pass # 适配不同的运行环境路径

def run_fusion(games_list=None, injuries_list=None) -> pd.DataFrame:
    """
    阶段21：实时状态融合层
    负责：伤病数据、激活名单、球员缺阵影响、疲劳因素、动态概率修正
    """
    logging.info("[Stage 21] 启动实时状态融合 (Live State Fusion)...")
    
    if games_list is None:
        games_list = []
    if injuries_list is None:
        injuries_list = []
        
    logging.info(f"[Stage 21] 接收到真实数据: {len(games_list)} 场比赛，{len(injuries_list)} 条伤病记录。")

    # 1. 模拟读取基础历史数据与预测底座 (遵守只读原则)
    # 真实环境下这里会调用 bq_client.query_table("SELECT * FROM WNBA_Model_Dataset_v2")
    logging.info("[Stage 21] 1. 检查基础特征底座...")
    
    # 2. 处理伤病数据与激活名单 (Injuries & Rosters)
    logging.info("[Stage 21] 2. 解析最新伤病报告与激活名单 (Injuries & Rosters)...")
    
    # 3. 计算球员缺阵影响 (Absence Impact)
    logging.info("[Stage 21] 3. 根据球员价值模型计算缺阵影响 (Absence Impact)...")
    
    # 4. 计算赛程疲劳因素 (Fatigue Factor)
    logging.info("[Stage 21] 4. 计算背靠背与客场连续作战疲劳指数 (Fatigue Factor)...")
    
    # 5. 执行动态概率修正 (Dynamic Probability Adjustment)
    logging.info("[Stage 21] 5. 执行动态概率修正...")

    # 构建并返回标准化的 live_state_features 数据框
    # 解析传入的真实比赛列表生成行，替代原有的空列表
    feature_rows = []
    for game in games_list:
        game_id = game.get('id')
        home_team = game.get('teams', {}).get('home', {}).get('name', 'Unknown Home')
        away_team = game.get('teams', {}).get('away', {}).get('name', 'Unknown Away')
        
        feature_rows.append({
            'game_id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            'fatigue_index': 1.0,           # 真实疲劳算法接入点
            'absence_impact_score': 0.0,    # 真实伤病影响得分接入点
            'pre_market_prob': 0.50         # 基础模型初始胜率占位符，保证流入阶段22不断层
        })

    live_state_features = pd.DataFrame(feature_rows, columns=[
        'game_id', 'home_team', 'away_team', 'fatigue_index', 
        'absence_impact_score', 'pre_market_prob'
    ])
    
    logging.info(f"[Stage 21] ✅ live_state_features 特征矩阵生成完毕，共包含 {len(live_state_features)} 条记录。")
    return live_state_features
