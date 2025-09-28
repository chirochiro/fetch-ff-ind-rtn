import io
from pathlib import Path
import polars as pl
import requests
import zipfile

class FFIndRtnProvider:
    """
    Fama-French 12 Industry Portfolios リターンを取得するクラス
    reb: 1 (Monthly) or 12 (Annual)
    weight: "value" or "equal"
    """
    def __init__(self, reb_month: int, weight: str, ):
        self.reb_month = int(reb_month)
        self.weight = weight.lower().strip()

    def _section_title(self) -> str:
        """reb と weight に応じて見出し文字列を返す"""
        mapping = {
            (1, "value"): "Average Value Weighted Returns -- Monthly",
            (1, "equal"): "Average Equal Weighted Returns -- Monthly",
            (12, "value"): "Average Value Weighted Returns -- Annual",
            (12, "equal"): "Average Equal Weighted Returns -- Annual",
        }
        title = mapping.get((self.reb_month, self.weight))
        if title is None:
            raise ValueError("reb_month は 1 か 12, weight は 'value' か 'equal' を指定してください。")
        return title

    def download(self, save_path: str):
        """
        Ken French サイトからデータを取得して該当セクションを CSV 保存
        save_path: 保存先のファイルパス
        """
        url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/12_Industry_Portfolios_CSV.zip"
        print("Downloading Fama-French 12 ind rtns ...")
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception(f"Failed to download data. Status code: {resp.status_code}")

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            filename = zf.namelist()[0]
            with zf.open(filename) as f:
                lines = f.read().decode("latin1").splitlines()

        title = self._section_title()
        try:
            title_idx = next(i for i, line in enumerate(lines) if line.strip().startswith(title))
        except StopIteration:
            raise RuntimeError(f"指定セクションが見つかりません: '{title}'")

        print(f"Section found: {lines[title_idx].strip()}")

        # ヘッダーとデータ行を抽出
        header_raw = lines[title_idx + 1]
        columns = [c.strip() for c in header_raw.split(",")]
        columns[0] = "date"

        records = []
        for line in lines[title_idx + 2:]:
            if line.strip() == "":
                break
            row = [x.strip() for x in line.split(",")]
            if len(row) != len(columns) or any(cell == "" for cell in row):
                break
            records.append(row)

        if not records:
            raise ValueError("データ行が取得できませんでした。")

        df = pl.DataFrame(records, schema=columns, orient="row")

        # 数値列を % → 小数に変換
        num_cols = [c for c in df.columns if c.lower() != "date"]
        df = df.with_columns([(pl.col(c).cast(pl.Float64) / 100.0) for c in num_cols])

        # 保存
        save_path_results = Path(save_path)
        save_path_dir = save_path_results / "FF_Ind_Rtn"
        save_path = save_path_dir / f"FF_Ind_Rtn_{self.reb_month}_{self.weight}.csv"
        
        save_path_dir.mkdir(parents=True, exist_ok=True)
        df.write_csv(str(save_path))
        print(f"Saved to {save_path.resolve()}")

        return df

"""
class FFFactorRtnProvider():
    \"\"\"Fama-French 3 Factor リターンを取得するクラス
    reb_month: 1 (Monthly) or 12 (Annual)
    weight: "value" or "equal"
    \"\"\"
    def __init__(self, reb_month: int, weight: str):
        self.reb_month = int(reb_month)
        self.weight = weight.lower().strip()

"""