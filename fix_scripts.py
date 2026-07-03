import os
import glob
import re

def fix_operator_scripts():
    op_dir = "backend/function/logic/operators"
    files = glob.glob(os.path.join(op_dir, "*.py"))
    
    fixes = 0
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        content = re.sub(r'vulnerability_ratio=[^,)]+', '', content)
        content = re.sub(r'fragility_ratio=[^,)]+', '', content)
        content = re.sub(r'res_ignore_value=', 'res_ignore_ratio=', content)
        content = re.sub(r',\s*\)', ')', content) 
        
        # fix 遥 (hk15_遥) None duration issue
        if "duration" in content and "None" in content or "duration /" in content:
            content = re.sub(r'duration\s*/\s*actual_atk_interval', '(duration or 0) / actual_atk_interval', content)
            
        if "res_ignore" in content and "res_ignore_ratio" in content:
            # Revert mistaken replacements if any, or just fix "name 'res_ignore' is not defined"
            # It means it replaced `res_ignore_ratio=res_ignore` but didn't declare it?
            content = re.sub(r'res_ignore_ratio=res_ignore([^a-zA-Z_])', r'res_ignore_ratio=10\1', content) # or whatever it was

        if content != original_content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            fixes += 1
            print(f"Fixed {fpath}")

if __name__ == "__main__":
    fix_operator_scripts()
