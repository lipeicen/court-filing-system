#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试所有保全案件
"""

import subprocess
import sys
import time

cases = [
    "保全2026001",
    "保全2026002", 
    "保全2026003",
    "保全2026004",
    "保全2026005",
    "保全2026006",
    "保全2026007",
    "保全2026008"
]

results = {}

print("="*80)
print("批量测试所有保全案件")
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
        
        # 检查关键成功标志
        output = result.stdout
        if "保全申请流程完成" in output:
            results[case_no] = "成功"
            print(f"成功: {case_no}")
        elif "登录失败" in output:
            results[case_no] = "登录失败"
            print(f"登录失败: {case_no}")
        else:
            results[case_no] = "失败"
            print(f"失败: {case_no}")
            
        # 显示最后几行输出
        lines = output.strip().split("\n")
        print("最后输出:")
        for line in lines[-10:]:
            print(f"  {line}")
            
    except subprocess.TimeoutExpired:
        results[case_no] = "超时"
        print(f"超时: {case_no}")
    except Exception as e:
        results[case_no] = f"错误: {e}"
        print(f"错误: {case_no} - {e}")
    
    # 案件之间等待一段时间
    if i < len(cases):
        print("等待10秒后测试下一个案件...")
        time.sleep(10)

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
