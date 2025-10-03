使い方：
uv sync
uv pip install -e .
uv run scripts/main.py reb_month weight save_path

引数 : 
reb_month : リバランス頻度 (ex. 1 or 12)
weight : ウェイト (ex. equal or value)
save_path : 保存先パス

uv pip install -e .が上手くいかない時の対処法 : 
uv run -p 3.13 python -m pip install -e .
明示的にpipの元となるpythonのバージョンを指定する