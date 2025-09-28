# script/main.py
import click
import sys
from pathlib import Path
from fetch_ff_ind_rtn.provider import FFIndRtnProvider

@click.command()
@click.argument("reb_month", type=click.Choice(["1", "12"], case_sensitive=False))
@click.argument("weight", type=click.Choice(["value", "equal"], case_sensitive=False))
@click.argument("save_path", type=click.Path(), required=False)

def main(reb_month: int, weight: str, save_path = "./results"):
    """
    Download Fama-French 12 Industry Returns.

    reb_month: 1 (Monthly) or 12 (Annual)
    WEIGHT: "value" or "equal"
    """
    # プロジェクトのルートディレクトリを取得
    current_file = Path(__file__).resolve()
    current_dir = current_file.parent.parent

    print(current_dir)

    # save_path = current_dir / "results" / f"FF_Ind_Rtn_{reb}_{weight}.csv"
    ff_provider = FFIndRtnProvider(reb_month=reb_month, weight=weight)
    ff_provider.download(str(save_path))
    print("Download and processing complete.")


if __name__ == "__main__":
    main()