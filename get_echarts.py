import subprocess
import shutil
import os

print("Cloning echarts-for-weixin...")
subprocess.run(["git", "clone", "--depth", "1", "https://github.com/ecomfe/echarts-for-weixin.git", "temp_echarts"], check=True)

print("Moving ec-canvas to frontend/ec-canvas...")
src = os.path.join("temp_echarts", "ec-canvas")
dst = os.path.join("frontend", "ec-canvas")

if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.move(src, dst)

print("Cleaning up...")
shutil.rmtree("temp_echarts")

print("Done!")
