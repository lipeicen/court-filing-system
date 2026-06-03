import subprocess
import os
import time

os.chdir(r'C:\court-auto-filing')

cases = [
    '保全2026001', '保全2026002', '保全2026003', '保全2026004',
    '保全2026005', '保全2026006', '保全2026007', '保全2026008',
    '保全2026009', '保全2026010', '保全2026011', '保全2026012'
]

results = {}

for case in cases:
    print(f"\n{'='*60}")
    print(f"开始测试: {case}")
    print(f"{'='*60}")
    
    start = time.time()
    try:
        result = subprocess.run(
            ['python', 'final_auto_upload_db_v3.py', case],
            capture_output=True, text=True, timeout=300
        )
        elapsed = time.time() - start
        
        success = '保全申请流程完成!' in result.stdout
        results[case] = {
            'success': success,
            'elapsed': elapsed,
            'error': result.stderr[-500:] if result.stderr else None
        }
        
        status = "OK" if success else "FAIL"
        print(f"{case}: {status} ({elapsed:.1f}s)")
        
        if not success:
            print("错误:")
            print(result.stdout[-800:])
            
    except subprocess.TimeoutExpired:
        results[case] = {'success': False, 'elapsed': 300, 'error': '超时'}
        print(f"{case}: FAIL 超时")
    except Exception as e:
        results[case] = {'success': False, 'elapsed': 0, 'error': str(e)}
        print(f"{case}: FAIL 异常: {e}")
    
    # 每个案件之间等待5秒，确保浏览器完全关闭
    time.sleep(5)

print(f"\n{'='*60}")
print("批量测试完成")
print(f"{'='*60}")

success_count = sum(1 for r in results.values() if r['success'])
print(f"\n总计: {success_count}/{len(cases)} 成功")
print(f"\n详细结果:")
for case, r in results.items():
    status = "OK" if r['success'] else "FAIL"
    print(f"  {status} {case} ({r['elapsed']:.1f}s)")
    if r['error']:
        print(f"     错误: {r['error'][:100]}")
