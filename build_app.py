import PyInstaller.__main__
import os

project_root = os.path.dirname(os.path.abspath(__file__))

# Data to include (source;destination on Windows)
datas = [
    (os.path.join(project_root, 'frontend'), 'frontend'),
    (os.path.join(project_root, 'data'), 'data'),
    (os.path.join(project_root, 'backend', 'function', 'logic', 'operators'), 'backend/function/logic/operators'),
]

# Convert to PyInstaller --add-data arguments
add_data_args = []
for src, dst in datas:
    add_data_args.append(f'--add-data={src}{os.pathsep}{dst}')

args = [
    'main_app.py',
    '--name=CupCalculation',
    '--windowed',
    '--clean',
    '--noconfirm',
] + add_data_args

print(f"Running PyInstaller with args: {args}")

PyInstaller.__main__.run(args)
