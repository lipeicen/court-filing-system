#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试新案件 (保全2026099-2026102)
"""

import subprocess
import sys
import time

cases = [
    "保全2026099",
    "保全2026100",
    "保全2026101",
    "保全2026102"
]

results = {}

print("="*80)
print("批量测试新保全案件")
print("="*80)

for i, case_no in enumerate(cases, 1):
    print()
    print("="*80)
    print(f"[{i}/{len(cases)}] 测试案件: {case_no}")
    print("="*80)
    
    try:
        result = subprocess.run(
            ["python", "final_auto_upload_db_v3.py", case_no],
            cwd=r"C:\court-auto-filing",
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout + result.stderr
        
        # 检查关键成功标志
        if "保全申请流程完成" in output:
            results[case_no] = "成功"
            print(f"✓ 成功: {case_no}")
            # 更新案件状态为已立案
            import pymysql
            conn = pymysql.connect(
                host='localhost', user='root', password='lijiayu123',
                database='court_filing', charset='utf8mb4'
            )
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE cases SET status = 1 WHERE case_no = %s", (case_no,))
                    conn.commit()
                    print(f"  状态已更新为已立案")
            finally:
                conn.close()
        elif "登录失败" in output:
            results[case_no] = "登录失败"
            print(f"✗ 登录失败: {case_no}")
        else:
            results[case_no] = "失败"
            print(f"✗ 失败: {case_no}")
            
        # 显示最后几行输出
        lines = output.strip().split("\n")
        print("最后输出:")
        for line in lines[-15:]:
            print(f"  {line}")
            
    except subprocess.TimeoutExpired:
        results[case_no] = "超时"
        print(f"✗ 超时: {case_no}")
    except Exception as e:
        results[case_no] = f"错误: {e}"
        print(f"✗ 错误: {case_no} - {e}")
    
    # 案件之间等待
    if i < len(cases):
        print("等待15秒后测试下一个案件...")
        time.sleep(15)

print()
print("="*80)
print("测试总结")
print("="*80)

success_count = sum(1 for v in results.values() if v == "成功")
fail_count = len(results) - success_count

for case_no, result in results.items():
    print(f"{case_no}: {result}")

print()
print(f"总计: {len(results)} 个案件")
print(f"成功: {success_count}")
print(f"失败: {fail_count}")
