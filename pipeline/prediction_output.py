import os
import logging
import pandas as pd

def save_to_bigquery(df: pd.DataFrame):
    """
    预留的 BigQuery 上传接口。
    阶段 23.8 要求：暂时不真正上传，只保留接口和日志提示。
    """
    logging.info("[Stage 23.8] BigQuery 上传接口已调用 (当前为预留占位，未执行真实写入)。")
    pass

def run_output(final_predictions: pd.DataFrame):
    """
    阶段 23.8: 预测结果输出模块
    功能：控制台打印摘要、保存本地 CSV、触发 BigQuery 接口。
    """
    try:
        if final_predictions is None or final_predictions.empty:
            logging.warning("[Stage 23.8] 输入的预测结果为空，取消输出。")
            return

        # ==========================================
        # A. 控制台打印预测结果摘要
        # ==========================================
        print("\n" + "="*40)
        print("         [FINAL PREDICTION]         ")
        print("="*40)
        
        for index, row in final_predictions.iterrows():
            # 使用 .get() 确保哪怕上游没有传队伍名称也不会报错退出
            game_id = row.get('game_id', 'N/A')
            home_team = row.get('home_team', 'N/A')
            away_team = row.get('away_team', 'N/A')
            final_prob = row.get('final_probability', 'N/A')
            market_prob = row.get('market_implied_prob', 'N/A')
            edge = row.get('edge', 'N/A')
            risk_level = row.get('risk_level', 'N/A')

            print(f"Game ID: {game_id}")
            print(f"Home Team: {home_team}")
            print(f"Away Team: {away_team}")
            print(f"Final Probability: {final_prob}")
            print(f"Market Probability: {market_prob}")
            print(f"Edge: {edge}")
            print(f"Risk Level: {risk_level}")
            print("-" * 40)

        # ==========================================
        # B. 保存 CSV 文件
        # ==========================================
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        csv_path = os.path.join(output_dir, "final_prediction.csv")
        final_predictions.to_csv(csv_path, index=False, encoding='utf-8')
        logging.info(f"[Stage 23.8] 预测结果已成功保存至本地: {csv_path}")

        # ==========================================
        # C. 预留 BigQuery 上传接口
        # ==========================================
        save_to_bigquery(final_predictions)

        # 成功日志
        logging.info("[Stage 23.8] prediction_output 输出完成")
        
    except Exception as e:
        # 失败日志
        logging.error(f"[Stage 23.8] ERROR: prediction_output 执行失败 - {str(e)}")
        raise e
