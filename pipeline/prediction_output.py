import os
import logging
import pandas as pd

def save_to_bigquery(df: pd.DataFrame):
    logging.info("[Stage 23.8] BigQuery 上传接口已调用 (当前为预留占位，未执行真实写入)。")
    pass

def run_output(final_predictions: pd.DataFrame):
    try:
        if final_predictions is None or final_predictions.empty:
            logging.warning("[Stage 23.8] 输入的预测结果为空，取消输出。")
            return

        print("\n" + "="*40)
        print("         [FINAL PREDICTION]         ")
        print("="*40)
        
        for index, row in final_predictions.iterrows():
            game_id = row.get('game_id', 'N/A')
            home_team = row.get('home_team', 'N/A')
            away_team = row.get('away_team', 'N/A')
            model_prob = row.get('model_probability', 'N/A')
            market_prob = row.get('market_probability', 'N/A')
            edge = row.get('edge', 'N/A')
            risk_level = row.get('risk_level', 'N/A')

            print(f"Game ID: {game_id}")
            print(f"Home Team: {home_team}")
            print(f"Away Team: {away_team}")
            print(f"Model Probability: {model_prob}")
            print(f"Market Probability: {market_prob}")
            print(f"Edge: {edge}")
            print(f"Risk Level: {risk_level}")
            print("-" * 40)

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        csv_path = os.path.join(output_dir, "final_prediction.csv")
        final_predictions.to_csv(csv_path, index=False, encoding='utf-8')
        logging.info(f"[Stage 23.8] 预测结果已成功保存至本地: {csv_path}")

        save_to_bigquery(final_predictions)
        logging.info("[Stage 23.8] prediction_output 输出完成")
        
    except Exception as e:
        logging.error(f"[Stage 23.8] ERROR: prediction_output 执行失败 - {str(e)}")
        raise e
