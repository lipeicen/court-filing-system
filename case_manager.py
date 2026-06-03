"""
案件管理工具 - 操作MySQL数据库
"""
import pymysql
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lijiayu123',
    'database': 'court_filing',
    'charset': 'utf8mb4'
}

def list_cases():
    """列出所有案件"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
    cases = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*100}")
    print(f"{'案件编号':<15} {'保全类型':<10} {'保全类别':<10} {'案件类型':<8} {'申请人':<10} {'状态':<8} {'创建时间'}")
    print(f"{'-'*100}")
    for c in cases:
        status = "已提交" if c['status'] == 1 else "待提交"
        print(f"{c['case_no']:<15} {c.get('preserve_type','') or '':<10} {c.get('preserve_category','') or '':<10} {c.get('case_type','') or '':<8} {c['applicant_name']:<10} {status:<8} {c['created_at']}")
    print(f"{'='*100}")

def show_case(case_no):
    """显示案件详情"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM cases WHERE case_no = %s", (case_no,))
    case = cursor.fetchone()
    
    if not case:
        print(f"未找到案件: {case_no}")
        conn.close()
        return
    
    print(f"\n{'='*60}")
    print(f"案件详情: {case['case_name']}")
    print(f"{'='*60}")
    
    # 基本信息
    print(f"\n【基本信息】")
    print(f"  案件编号: {case.get('case_no', '')}")
    print(f"  保全类型: {case.get('preserve_type', '')}")
    print(f"  保全类别: {case.get('preserve_category', '')}")
    
    # 诉讼保全才显示案件类型、案号、案由
    if case.get('preserve_category') == '诉讼保全':
        print(f"  案件类型: {case.get('case_type', '')}")
        print(f"  案号: {case.get('court_case_no', '')}")
        print(f"  案由: {case.get('case_reason', '')}")
    
    # 当事人信息
    print(f"\n【当事人信息】")
    print(f"  申请人: {case.get('applicant_name', '')} (身份证: {case.get('applicant_id', '')})")
    print(f"  申请人电话: {case.get('applicant_phone', '')}")
    print(f"  申请人地址: {case.get('applicant_address', '')}")
    print(f"  被申请人: {case.get('respondent_name', '')} (身份证: {case.get('respondent_id', '')})")
    print(f"  被申请人电话: {case.get('respondent_phone', '')}")
    
    # 保全信息
    print(f"\n【保全信息】")
    print(f"  保全金额: {case.get('preserve_amount', '')}")
    print(f"  法院: {case.get('court_name', '')} ({case.get('court_code', '')})")
    print(f"  担保方式: {case.get('guarantee_type', '')}")
    print(f"  担保价值: {case.get('guarantee_value', '')}")
    
    # 状态
    status = "已提交" if case.get('status') == 1 else "待提交"
    print(f"\n【状态】")
    print(f"  状态: {status}")
    print(f"  创建时间: {case.get('created_at', '')}")
    
    cursor.execute("SELECT * FROM property_clues WHERE case_id = %s", (case['id'],))
    props = cursor.fetchall()
    print(f"\n财产线索 ({len(props)} 条):")
    for p in props:
        print(f"  {p['property_type']}: {p['bank_name']} {p['bank_account']}")
    
    cursor.execute("SELECT * FROM case_files WHERE case_id = %s", (case['id'],))
    files = cursor.fetchall()
    print(f"\n材料文件 ({len(files)} 个):")
    for f in files:
        status = "已上传" if f['upload_status'] == 1 else "未上传"
        print(f"  [{status}] [{f['file_category']}] {f['file_name']}")
    
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python case_manager.py list          # 列出所有案件")
        print("  python case_manager.py show <编号>   # 显示案件详情")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "list":
        list_cases()
    elif cmd == "show" and len(sys.argv) > 2:
        show_case(sys.argv[2])
    else:
        print("未知命令")
