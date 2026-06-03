"""
数据库初始化 - 创建新案件
用法: python db_init_case.py
"""
import pymysql
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lijiayu123',
    'database': 'court_filing',
    'charset': 'utf8mb4'
}

def create_case(case_data):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 插入案件
    cursor.execute("""
        INSERT INTO cases (case_no, case_name, applicant_name, applicant_id, applicant_phone,
                          applicant_address, respondent_name, respondent_id, respondent_phone,
                          preserve_amount, court_name, court_code, guarantee_type, guarantee_value)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (case_data['case_no'], case_data['case_name'], case_data['applicant_name'],
          case_data['applicant_id'], case_data['applicant_phone'], case_data['applicant_address'],
          case_data['respondent_name'], case_data['respondent_id'], case_data['respondent_phone'],
          case_data['preserve_amount'], case_data['court_name'], case_data['court_code'],
          case_data['guarantee_type'], case_data['guarantee_value']))
    
    case_id = cursor.lastrowid
    
    # 插入财产线索
    for prop in case_data.get('properties', []):
        cursor.execute("""
            INSERT INTO property_clues (case_id, property_type, owner, bank_name, bank_account, amount, property_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (case_id, prop['property_type'], prop['owner'], prop['bank_name'],
              prop['bank_account'], prop['amount'], prop['property_value']))
    
    # 扫描材料目录并插入文件记录
    upload_dir = os.path.join(r"C:\court-auto-filing\uploads", case_data['case_no'])
    if os.path.exists(upload_dir):
        for folder_name in os.listdir(upload_dir):
            folder_path = os.path.join(upload_dir, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if not file_name.startswith('.'):
                        file_path = os.path.join(folder_path, file_name)
                        cursor.execute("""
                            INSERT INTO case_files (case_id, file_category, file_name, file_path)
                            VALUES (%s, %s, %s, %s)
                        """, (case_id, folder_name, file_name, file_path))
    
    conn.commit()
    conn.close()
    print(f"✅ 案件 {case_data['case_no']} 创建成功，ID: {case_id}")

if __name__ == "__main__":
    # 示例：创建新案件
    case_data = {
        'case_no': '保全2026002',
        'case_name': '测试保全案件002',
        'applicant_name': '张三',
        'applicant_id': '110101199003031234',
        'applicant_phone': '13800138002',
        'applicant_address': '北京市海淀区xxx街道',
        'respondent_name': '李四',
        'respondent_id': '110101199004041234',
        'respondent_phone': '13900139002',
        'preserve_amount': 200000.00,
        'court_name': '北京市海淀区人民法院',
        'court_code': '110108',
        'guarantee_type': '保证',
        'guarantee_value': 200000.00,
        'properties': [
            {
                'property_type': '银行存款',
                'owner': '李四',
                'bank_name': '中国建设银行北京分行',
                'bank_account': '6227001234567890123',
                'amount': 200000.00,
                'property_value': 200000.00
            }
        ]
    }
    
    create_case(case_data)
