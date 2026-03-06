import matplotlib.pyplot as plt
import pandas as pd
from config import OUTPUT_PATH

def generate_table(df: pd.DataFrame, office_name: str)-> None:
    """
    Generates a report based on the provided DataFrame and office name, and saves it as an image.
    Args:
        df (pd.DataFrame): A DataFrame containing the data to be included in the report.
        office_name (str): The name of the office for which the report is generated.
    """
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis("off")

    table = ax.table(
                    cellText=df.values,
                    colLabels=df.columns,
                    cellLoc='left',
                    loc='center'
                    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.1, 1.6)

    n_linhas = len(df)
    n_colunas = len(df.columns)

    verde_escuro = "#1B5E20"
    verde_claro = "#E8F5E9"

    for (row, col), cell in table.get_celld().items():

        if row == 0:
            cell.set_facecolor(verde_escuro)
            cell.set_text_props(color="white", weight="bold", ha='center')

        elif row == n_linhas:
            cell.set_facecolor(verde_escuro)
            cell.set_text_props(color="white", weight="bold")

        elif row % 2 == 0:
            cell.set_facecolor(verde_claro)

        if col == n_colunas - 1:
            cell._text.set_ha('right')

        cell.set_linewidth(0)

    table.auto_set_column_width(col=list(range(n_colunas)))

    plt.savefig(
        f"{OUTPUT_PATH}/{office_name.replace(' ', '_')}.png",
        bbox_inches='tight',
        dpi=300
    )

    plt.close(fig)