import pandas as pd
import logging

def run_fusion(games_list=None, injuries_list=None) -> pd.DataFrame:
    """
    阶段21：实时状态融合层
    接收 main.py 传递的真实数据并生成特征矩阵。
    """
    logging.info(f"[Stage 21] 开始融合: 收到 {len(games_list or [])} 场比赛, {len(injuries_list or [])} 条伤病数据。")
    
    # 处理数据异常：若为空则返回空DF，由 main.py 的 quality_check 拦截或处理
    if not games_list:
        return pd.DataFrame()
        
    feature_rows = []
    for game in games_list:
        game_id = game.get('id')
        home_team = game.get('teams', {}).get('home', {}).get('name', 'Unknown')
        away_team = game.get('teams', {}).get('away', {}).get('name', 'Unknown')
        
        feature_rows.append({
            'game_id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            'fatigue_index': 1.0,
            'absence_impact_score': 0.0,
            'pre_market_prob': 0.5
        })

    return pd.DataFrame(feature_rows)
