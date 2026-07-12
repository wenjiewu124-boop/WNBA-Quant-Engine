import csv
import os
from datetime import datetime

LOG_FILE = "api_refresh_history.csv"

def log_api_request(api_name: str, request_status: str, data_count: int, error_message: str = "") -> dict:
    """
    记录 API 请求日志。
    输出至终端（供 GitHub Actions 捕获）并追加至本地 CSV 文件。
    """
    # 统一使用 ISO 格式时间戳
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "api_name": api_name,
        "request_status": request_status,
        "data_count": data_count,
        "error_message": error_message
    }
    
    # 打印至标准输出，方便 GitHub Actions 日志面板直接监控
    status_icon = "✅" if request_status.upper() == "SUCCESS" else "❌"
    print(f"{status_icon} [API MONITOR] {timestamp} | {api_name} | Status: {request_status} | Count: {data_count} | Error: {error_message}")
    
    # 写入 CSV 持久化
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "api_name", "request_status", "data_count", "error_message"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)
        
    return log_entry
