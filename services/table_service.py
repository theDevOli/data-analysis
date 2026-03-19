import matplotlib

from models.office import Office
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pathlib as pl
import pandas as pd

from config import OUTPUT_PATH

def generate_table(df: pd.DataFrame, office: Office)-> None:
    """
    Generates a report based on the provided DataFrame and office name, and saves it as an image.
    Args:
        df (pd.DataFrame): A DataFrame containing the data to be included in the report.
        office (Office): The office entity for which the report is generated.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
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

    row_number = len(df)
    column_number = len(df.columns)

    dark_green = "#1B5E20"
    light_green = "#E8F5E9"

    for (row, col), cell in table.get_celld().items():

        if row == 0:
            cell.set_facecolor(dark_green)
            cell.set_text_props(color="white", weight="bold", ha='center')

        elif row == row_number:
            cell.set_facecolor(dark_green)
            cell.set_text_props(color="white", weight="bold")

        elif row % 2 == 0:
            cell.set_facecolor(light_green)

        if col == column_number - 1:
            cell._text.set_ha('right')

        cell.set_linewidth(0)

    table.auto_set_column_width(col=list(range(column_number)))

    output_dir = pl.Path(OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.savefig(
        output_dir / f"{office.office_name.replace(' ', '_')}-{office.city[:3].upper()}.png",
        bbox_inches='tight',
        dpi=300
    )

    plt.close(fig)