from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile

from services.query_service import get_offices, get_office_data
# from processors.process_office import process_office
from config import OUTPUT_PATH
from services.table_service import generate_table

output_dir = Path(OUTPUT_PATH)
output_dir.mkdir(parents=True, exist_ok=True)

zip_path = Path("/tmp/relatorios.zip")

def main():
    offices = get_offices()

    for office in offices:
        df = get_office_data(office.office_id)
        if df.empty:
            continue

        generate_table(df, office)

    with ZipFile(zip_path, "w") as zipf:
        for file in output_dir.iterdir():
            if file.is_file():
                arcname = f"escritorios/{file.name}"

                zipf.write(file, arcname=arcname)

if __name__ == "__main__":
    main()