#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量自动立案脚本
依次处理多个案件
"""

import subprocess
import sys
import time

def run_case(case_no):
    """运行单个案件"""
    print(f"\n{'='*60}")
    print(f"开始处理: {case_no}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ['python', 'final_auto_upload_db_v3.py', case_no],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=r'C:\court-auto-filing'
        )
        
        print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        
        if result.returncode != 0:
            print(f"✗ {case_no} 处理失败")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
        
        print(f"✓ {case_no} 处理完成")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"✗ {case_no} 超时")
        return False
    except Exception as e:
        print(f"✗ {case_no} 异常: {e}")
        return False

def main():
    # 12个案件列表
    case_nos = [f'保全2026{100+i:03d}' for i in range(1, 13)]
    
    print("="*60)
    print("批量自动立案 - 12个案件")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for i, case_no in enumerate(case_nos, 1):
        print(f"\n[{i}/{len(case_nos)}] ", end='')
        
        if run_case(case_no):
            success_count += 1
        else:
            fail_count += 1
        
        # 案件间间隔
        if i < len(case_nos):
            print(f"\n等待5秒后继续下一个案件...")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print("批量处理完成")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
