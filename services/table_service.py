import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from models.office import Office
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pathlib as pl
import pandas as pd

from config import OUTPUT_OFFICE_PATH, OUTPUT_PARTNER_PATH

def calculate_figure_height(df_client_data: pd.DataFrame) -> float:
    base_height = 2
    row_height = 0.35
    return base_height + (len(df_client_data) * row_height)

def generate_table(df: pd.DataFrame,fig: Figure, ax: Axes)-> None:
    """
    Generates a report based on the provided DataFrame and office name, and saves it as an image.
    Args:
        df (pd.DataFrame): A DataFrame containing the data to be included in the report.
        fig (Figure): The matplotlib figure on which to generate the table.
    """
    if df is None or df.empty:
        return
    
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

def generate_offices_table(df_client_data: pd.DataFrame,df_statistics: pd.DataFrame, office: Office)-> None:
    """
    Generates a report based on the provided DataFrame and office name, and saves it as an image.
    Args:
        df_client_data (pd.DataFrame): A DataFrame containing the data to be included in the report.
        df_statistics (pd.DataFrame): A DataFrame containing statistical data for the report.
        office (Office): The office entity for which the report is generated.
    """
    has_data = df_client_data is not None and not df_client_data.empty

    fig_height = calculate_figure_height(df_client_data) if has_data else 3

    fig = plt.figure(figsize=(12, fig_height))

    if has_data:
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 4], hspace=0.02)
        ax_top = fig.add_subplot(gs[0])
        ax_bottom = fig.add_subplot(gs[1])
    else:
        gs = fig.add_gridspec(1, 1)
        ax_top = fig.add_subplot(gs[0])
        ax_bottom = None

    generate_table(df_statistics, fig, ax_top)

    if has_data:
        generate_table(df_client_data, fig, ax_bottom)

    output_dir = pl.Path(OUTPUT_OFFICE_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.savefig(
        output_dir / f"{office.office_name.replace(' ', '_')}-{office.city[:3].upper()}.png",
        bbox_inches='tight',
        dpi=300
    )

    plt.close(fig)

def generate_partner_table(df: pd.DataFrame, partner_name: str) -> None:
    """
    Generates a report based on the provided DataFrame and office name, and saves it as an image.
    Args:
        df (pd.DataFrame): A DataFrame containing the data to be included in the report.
        partner_name (str): The name of the partner for which the report is generated.
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    generate_table(df, fig, ax)

    output_dir = pl.Path(OUTPUT_PARTNER_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.savefig(
        output_dir / f"{partner_name.replace(' ', '_')}.png",
        bbox_inches='tight',
        dpi=300
    )

    plt.close(fig)