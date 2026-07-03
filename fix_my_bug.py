import os
import glob

def fix_my_bug():
    op_dir = "backend/function/logic/operators"
    files = glob.glob(os.path.join(op_dir, "*.py"))
    
    fixes = 0
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        
        # fix the bug I introduced
        content = content.replace("skill_(duration or 0)", "skill_duration")
        
        if content != original_content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            fixes += 1
            print(f"Fixed bug in {fpath}")

if __name__ == "__main__":
    fix_my_bug()
