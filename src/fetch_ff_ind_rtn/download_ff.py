from pathlib import Path
import requests
import zipfile
import io
import polars as pl

def download_ff_ind_monthly(save_path: str):
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/12_Industry_Portfolios_CSV.zip"

    print("Downloading Fama-French 12 ind rtns ...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download data. Status code: {response.status_code}")

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        filename = zf.namelist()[0]
        with zf.open(filename) as file:
            lines = file.read().decode("latin1").splitlines()

    # 11行目の説明文を取得（1-index → 0-index）
    monthly_info = lines[10].strip()
    

    # 12行目をヘッダー
    header_raw = lines[11]
    columns = [c.strip() for c in header_raw.split(",")]

    # データ行を読み取り
    records = []
    for line in lines[12:]:
        if line.strip() == "":
            break
        row = [x.strip() for x in line.split(",")]
        if len(row) != len(columns) or any(cell == "" for cell in row):
            break
        records.append(row)


    df = pl.DataFrame(records, schema=columns, orient="row")

    # 数値列の変換（％ → 小数）
    df = df.with_columns([
        pl.col(col).cast(pl.Float64) / 100.0 for col in columns[1:]
    ])

    # 保存
    save_path_obj = Path(save_path)
    df.write_csv(str(save_path_obj))  # polarsはstr型を要求する
    print(f"Saved to {save_path_obj.resolve()}")