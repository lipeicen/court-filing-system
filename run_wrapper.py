
import sys
sys.path.insert(0, r'C:\court-auto-filing')

# Redirect stdout to file
sys.stdout = open(r'C:\court-auto-filing\run_output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

import final_auto_upload_db_v3 as script

# Run main with case argument
sys.argv = ['script.py', '保全2026001']
script.main()
