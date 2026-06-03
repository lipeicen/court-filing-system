
"""
法院自动立案系统 - MySQL数据库版本
从数据库读取案件信息，自动填写在线立案/保全
"""
import os
import sys
import time
import pymysql
from playwright.sync_api import sync_playwright

# ========== 数据库配置 ==========
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lijiayu123',
    'database': 'court_filing',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def get_case_data(case_no):
    """获取案件完整数据"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 案件信息
    cursor.execute("SELECT * FROM cases WHERE case_no = %s", (case_no,))
    case = cursor.fetchone()
    
    if not case:
        conn.close()
        return None
    
    # 财产线索
    cursor.execute("SELECT * FROM property_clues WHERE case_id = %s", (case['id'],))
    properties = cursor.fetchall()
    
    # 材料文件
    cursor.execute("SELECT * FROM case_files WHERE case_id = %s", (case['id'],))
    files = cursor.fetchall()
    
    conn.close()
    
    return {
        'case': case,
        'properties': properties,
        'files': files
    }

def update_case_status(case_no, status=1):
    """更新案件状态"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cases SET status = %s WHERE case_no = %s",
        (status, case_no)
    )
    conn.commit()
    conn.close()

def update_file_status(file_id, status=1):
    """更新文件上传状态"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE case_files SET upload_status = %s WHERE id = %s",
        (status, file_id)
    )
    conn.commit()
    conn.close()

# ========== 自动立案逻辑 ==========
def auto_filing_from_db(case_no, headless=False):
    """从数据库读取数据并自动立案"""
    
    # 获取案件数据
    data = get_case_data(case_no)
    if not data:
        print(f"❌ 未找到案件: {case_no}")
        return False
    
    case = data['case']
    properties = data['properties']
    files = data['files']
    
    print(f"\n{'='*60}")
    print(f"案件: {case['case_name']} ({case['case_no']})")
    print(f"申请人: {case['applicant_name']}")
    print(f"被申请人: {case['respondent_name']}")
    print(f"保全金额: {case['preserve_amount']}")
    print(f"{'='*60}\n")
    
    # TODO: 集成原有的浏览器自动化逻辑
    # 这里可以复用 final_auto_upload_v3.py 的代码
    
    print("✅ 数据读取成功，准备填写...")
    return True

if __name__ == "__main__":
    case_no = sys.argv[1] if len(sys.argv) > 1 else "保全2026001"
    auto_filing_from_db(case_no)
