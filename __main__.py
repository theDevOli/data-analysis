from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
# from zipfile import ZipFile

from services.query_service import get_offices,get_partners, get_office_data,get_partner_data,get_statistics
# from processors.process_office import process_office
# from config import OUTPUT_PATH
from services.table_service import generate_offices_table, generate_partner_table

# output_dir = Path(OUTPUT_PATH)
# output_dir.mkdir(parents=True, exist_ok=True)

# zip_path = Path("/tmp/relatorios.zip")

def main():
    offices = get_offices()
    partners = get_partners()

    for office in offices:
        df_statistics = get_statistics(office.office_id)
        if df_statistics.empty:
            continue
        
        df_client_data = get_office_data(office.office_id)

        generate_offices_table(df_client_data, df_statistics, office)
    
    for partner in partners:
        df = get_partner_data(partner.partner_id)
        if df.empty:
            continue

        generate_partner_table(df, partner.partner_name)

    # with ZipFile(zip_path, "w") as zipf:
    #     for file in output_dir.iterdir():
    #         if file.is_file():
    #             arcname = f"escritorios/{file.name}"

    #             zipf.write(file, arcname=arcname)

if __name__ == "__main__":
    main()