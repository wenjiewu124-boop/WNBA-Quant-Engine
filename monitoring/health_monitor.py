import os
import csv
import time
import logging
from datetime import datetime
import pandas as pd

# 配置基础日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [HEALTH MONITOR] %(message)s'
)

HEALTH_LOG_FILE = "pipeline_health_log.csv"

# ==========================================
# 1. 日志记录模块
# ==========================================
def log_health_check(check_name: str, status: str, message: str) -> None:
    """
    生成 pipeline_health_log
    记录: timestamp, check_name, status, message
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "check_name": check_name,
        "status": status.upper(),
        "message": message
    }
    
    # 控制台输出警报
    if status.upper() != "PASS":
        logging.warning(f"🚨 异常报警 | 检查项: {check_name} | 状态: {status} | 信息: {message}")
    else:
        logging.info(f"✅ 检查通过 | 检查项: {check_name} | 信息: {message}")
        
    # 写入 CSV 日志持久化
    file_exists = os.path.isfile(HEALTH_LOG_FILE)
    with open(HEALTH_LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "check_name", "status", "message"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

# ==========================================
# 2. Pipeline 运行检查
# ==========================================
def check_pipeline_status(module_name: str, is_success: bool, error_msg: str = "") -> bool:
    """
    检测主流程及各模块是否成功完成并返回正常状态。
    """
    if is_success:
        log_health_check(f"Pipeline:{module_name}", "PASS", "模块运行正常")
        return True
    else:
        log_health_check(f"Pipeline:{module_name}", "FAIL", f"模块运行失败: {error_msg}")
        return False

# ==========================================
# 3. API 健康检查
# ==========================================
def check_api_health(api_name: str, status_code: int, response_time: float, data_count: int) -> None:
    """
    检测 API-Basketball 和 The Odds API 的健康度。
    """
    if status_code == 200 and data_count > 0:
        msg = f"响应时间: {response_time:.2f}s, 数据量: {data_count}条"
        log_health_check(f"API_Health:{api_name}", "PASS", msg)
    elif status_code == 200 and data_count == 0:
        msg = f"响应正常但无数据返回 (可能由于非比赛日), 响应时间: {response_time:.2f}s"
        log_health_check(f"API_Health:{api_name}", "WARNING", msg)
    else:
        msg = f"API请求异常! 状态码: {status_code}, 响应时间: {response_time:.2f}s"
        log_health_check(f"API_Health:{api_name}", "FAIL", msg)

# ==========================================
# 4. 数据质量检查
# ==========================================
def check_data_quality(df: pd.DataFrame, dataset_name: str) -> bool:
    """
    检测数据的完整性与合法性。
    包含：game_id 是否为空、比赛数量异常、NULL数量、重复数据。
    """
    if df.empty:
        log_health_check(f"Data_Quality:{dataset_name}", "FAIL", "数据框为空，无数据可检查")
        return False
        
    issues = []
    
    # 检查 game_id 是否为空
    if 'game_id' in df.columns and df['game_id'].isnull().any():
        issues.append("存在缺失的 game_id")
        
    # 检查数据量是否异常 (WNBA 每日比赛通常不会超过 6 场)
    if len(df) > 20: 
        issues.append(f"单日比赛数据量异常偏高: {len(df)} 场")
        
    # 检查全局 NULL 数量
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        issues.append(f"存在 {null_count} 个 NULL 值")
        
    # 检查重复数据
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        issues.append(f"存在 {duplicate_count} 条重复数据")
        
    if issues:
        log_health_check(f"Data_Quality:{dataset_name}", "WARNING", " | ".join(issues))
        return False
        
    log_health_check(f"Data_Quality:{dataset_name}", "PASS", f"质量达标，共 {len(df)} 条记录")
    return True

# ==========================================
# 5. 预测结果检查
# ==========================================
def check_prediction_results(df: pd.DataFrame) -> bool:
    """
    检测 final_probability、edge 和 risk_level 的合法边界。
    """
    if df.empty:
        log_health_check("Prediction_Quality:final_output", "FAIL", "预测结果为空")
        return False
        
    issues = []
    
    # 检查概率边界 (是否在 0.05 - 0.95 之间)
    if 'final_probability' in df.columns:
        out_of_bounds = df[(df['final_probability'] < 0.05) | (df['final_probability'] > 0.95)]
        if not out_of_bounds.empty:
            issues.append(f"存在 {len(out_of_bounds)} 条概率越界数据(小于0.05或大于0.95)")
    else:
        issues.append("缺失 final_probability 字段")
        
    # 检查 edge 异常值 (绝对值异常大，如 > 0.3)
    if 'edge' in df.columns:
        extreme_edge = df[df['edge'].abs() > 0.30]
        if not extreme_edge.empty:
            issues.append(f"存在 {len(extreme_edge)} 条胜率优势(edge)绝对值超过30%的异常数据")
            
    # 检查 risk_level
    if 'risk_level' in df.columns and df['risk_level'].isnull().any():
        issues.append("存在 risk_level 缺失的数据")
        
    if issues:
        log_health_check("Prediction_Quality:final_output", "ERROR", " | ".join(issues))
        return False
        
    log_health_check("Prediction_Quality:final_output", "PASS", "预测结果概率及风险值全部在合理区间内")
    return True
