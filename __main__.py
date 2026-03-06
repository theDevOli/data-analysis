from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile

from services.query_service import get_offices
from processors.process_office import process_office
from config import OUTPUT_PATH

output_dir = Path(OUTPUT_PATH)
output_dir.mkdir(parents=True, exist_ok=True)

zip_path = Path("/tmp/relatorios.zip")

def main():
    offices = get_offices()

    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(process_office, offices)

    with ZipFile(zip_path, "w") as zipf:
        for file in output_dir.iterdir():
            if file.is_file():
                arcname = f"escritorios/{file.name}"

                zipf.write(file, arcname=arcname)

if __name__ == "__main__":
    main()