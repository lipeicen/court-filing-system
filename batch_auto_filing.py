"""
批量自动立案脚本
查询所有 status=0 且有文件的案件，逐个提交
"""
import subprocess
import time
import pymysql
import logging
import json
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r'C:\court-auto-filing\batch_auto_filing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

STATUS_FILE = r'C:\court-auto-filing\auto_filing_progress.json'
STOP_FILE = r'C:\\court-auto-filing\\auto_filing_stop.flag'


def write_progress(data):
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def check_stop():
    return os.path.exists(STOP_FILE)


def get_db_connection():
    return pymysql.connect(
        host='localhost', user='root', password='lijiayu123',
        database='court_filing', charset='utf8mb4'
    )


def get_pending_cases():
    """获取待立案且有文件的案件"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.case_no, c.applicant_name, c.respondent_name
        FROM cases c
        WHERE c.status = 0
        ORDER BY c.id
    """)
    cases = cursor.fetchall()
    cursor.close()
    conn.close()
    return cases


def update_status(case_no, status=1):
    """更新案件状态"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status = %s WHERE case_no = %s", (status, case_no))
    conn.commit()
    cursor.close()
    conn.close()


def run_single_case(case_no):
    """执行单个案件立案"""
    logger.info("开始立案: %s", case_no)
    try:
        result = subprocess.run(
            ['python', 'final_auto_upload_db_v3.py', case_no],
            cwd=r'C:\court-auto-filing',
            capture_output=True,
            text=True,
            timeout=600
        )
        logger.info("案件 %s 返回码: %d", case_no, result.returncode)
        if result.returncode != 0:
            logger.error("案件 %s 失败: %s", case_no, result.stderr[:500])
            return False
        logger.info("案件 %s 执行成功", case_no)
        return True
    except subprocess.TimeoutExpired:
        logger.error("案件 %s 超时", case_no)
        return False
    except Exception as e:
        logger.error("案件 %s 异常: %s", case_no, e)
        return False


def main():
    cases = get_pending_cases()
    logger.info("发现 %d 个待立案案件", len(cases))
    total = len(cases)

    write_progress({
        'running': True,
        'total': total,
        'current': 0,
        'current_case': None,
        'completed': [],
        'failed': [],
        'start_time': datetime.now().isoformat()
    })

    if not cases:
        logger.info("没有待立案案件，退出")
        write_progress({'running': False, 'total': 0, 'current': 0, 'current_case': None, 'completed': [], 'failed': []})
        return

    completed = []
    failed = []

    for idx, case in enumerate(cases, 1):
        case_no = case['case_no']
        logger.info("[%d/%d] 处理案件: %s (%s vs %s)",
                    idx, total, case_no,
                    case['applicant_name'], case['respondent_name'])

        write_progress({
            'running': True,
            'total': total,
            'current': idx,
            'current_case': case_no,
            'completed': completed,
            'failed': failed,
            'start_time': datetime.now().isoformat()
        })

        success = run_single_case(case_no)
        if success:
            update_status(case_no, 1)
            completed.append(case_no)
            logger.info("案件 %s 状态已更新为已立案", case_no)
        else:
            failed.append(case_no)
            logger.warning("案件 %s 立案失败，状态保持未立案", case_no)

        write_progress({
            'running': True,
            'total': total,
            'current': idx,
            'current_case': case_no if idx < total else None,
            'completed': completed,
            'failed': failed,
            'start_time': datetime.now().isoformat()
        })

        if check_stop():
            logger.info("检测到停止标志，终止批量立案")
            write_progress({
                'running': False,
                'total': total,
                'current': idx,
                'current_case': None,
                'completed': completed,
                'failed': failed,
                'start_time': datetime.now().isoformat(),
                'stopped': True
            })
            os.remove(STOP_FILE)
            return

        if idx < total:
            logger.info("休眠5秒后继续...")
            time.sleep(5)

    write_progress({
        'running': False,
        'total': total,
        'current': total,
        'current_case': None,
        'completed': completed,
        'failed': failed,
        'start_time': datetime.now().isoformat()
    })
    logger.info("批量立案完成，共处理 %d 个案件", total)


if __name__ == '__main__':
    main()
