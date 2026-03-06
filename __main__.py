from services.query_service import get_offices, get_office_data
from services.table_service import generate_table

def main():
    offices = get_offices()

    for office in offices:
        df = get_office_data(office.office_id)

        if df.empty:
            continue

        generate_table(df, office.office_name)

if __name__ == "__main__":
    main()