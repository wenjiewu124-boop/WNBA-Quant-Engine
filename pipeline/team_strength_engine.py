"""
WNBA 球队实力计算引擎
Team Strength Calculation Engine

阶段 24.1: 模型组件工程化整理
职责: 从已有逻辑中拆分出基础的球队实力计算模块
"""

import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TeamStrengthEngine:
    """
    球队实力计算引擎
    
    输入 DataFrame 字段: team, points_for, points_against, ortg, drtg, win
    输出 DataFrame 字段: team, offense_score, defense_score, recent_form_score, home_advantage, strength_score
    """
    
    def __init__(self):
        logger.info("TeamStrengthEngine 初始化完成")
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算球队实力评分
        
        参数:
            df (pd.DataFrame): 必须包含列: team, points_for, points_against, ortg, drtg, win
            
        返回:
            pd.DataFrame: 包含列: team, offense_score, defense_score, recent_form_score, home_advantage, strength_score
        """
        logger.info("开始计算球队实力评分")
        
        # 校验输入字段（严格遵守数据架构交接信息）
        required_cols = ['team', 'points_for', 'points_against', 'ortg', 'drtg', 'win']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"输入 DataFrame 缺少必要列: {missing_cols}")
            raise ValueError(f"缺少必要列: {missing_cols}")
            
        result_df = df[['team']].copy()
        logger.info(f"接收到 {len(result_df)} 支球队数据")
        
        # 1. 计算进攻评分 (基于 ortg 归一化)
        logger.info("计算 offense_score")
        ortg_min = df['ortg'].min()
        ortg_max = df['ortg'].max()
        if ortg_max > ortg_min:
            result_df['offense_score'] = ((df['ortg'] - ortg_min) / (ortg_max - ortg_min)) * 100
        else:
            result_df['offense_score'] = 50.0
            
        # 2. 计算防守评分 (基于 drtg 归一化，drtg越低得分越高)
        logger.info("计算 defense_score")
        drtg_min = df['drtg'].min()
        drtg_max = df['drtg'].max()
        if drtg_max > drtg_min:
            result_df['defense_score'] = ((drtg_max - df['drtg']) / (drtg_max - drtg_min)) * 100
        else:
            result_df['defense_score'] = 50.0
            
        # 3. 计算近期表现评分 (基于 win 胜率)
        logger.info("计算 recent_form_score")
        result_df['recent_form_score'] = df['win'] * 100
        
        # 4. 主场优势 (当前阶段使用固定值，后续阶段细化)
        logger.info("赋值 home_advantage")
        result_df['home_advantage'] = 3.0
        
        # 5. 综合实力评分 (加权平均)
        logger.info("计算综合 strength_score")
        result_df['strength_score'] = (
            result_df['offense_score'] * 0.4 + 
            result_df['defense_score'] * 0.4 + 
            result_df['recent_form_score'] * 0.2
        )
        
        logger.info("球队实力评分计算完成")
        return result_df


if __name__ == "__main__":
    print("=" * 60)
    print("TeamStrengthEngine 独立导入与运行测试")
    print("=" * 60)
    
    # 1. 独立import测试
    try:
        from pipeline.team_strength_engine import TeamStrengthEngine
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        exit(1)
        
    # 2. DataFrame 处理测试
    print("\n开始测试 DataFrame 处理...")
    test_data = {
        'team': ['LAS', 'NYL', 'CHI'],
        'points_for': [85.2, 82.1, 78.5],
        'points_against': [79.3, 80.0, 81.2],
        'ortg': [108.5, 105.2, 102.1],
        'drtg': [98.3, 101.5, 104.2],
        'win': [0.65, 0.55, 0.45]
    }
    df_input = pd.DataFrame(test_data)
    
    # 3. 执行计算
    engine = TeamStrengthEngine()
    df_output = engine.calculate(df_input)
    
    # 4. 校验输出字段
    expected_cols = ['team', 'offense_score', 'defense_score', 'recent_form_score', 'home_advantage', 'strength_score']
    if list(df_output.columns) == expected_cols:
        print("✅ 输出字段验证通过")
    else:
        print(f"❌ 输出字段验证失败: {list(df_output.columns)}")
        
    print("\n" + "=" * 60)
    print("测试完成，模块可独立运行")
    print("=" * 60)
