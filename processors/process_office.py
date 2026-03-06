from services.query_service import get_office_data
from services.table_service import generate_table

def process_office(office):

    df = get_office_data(office.office_id)

    if df.empty:
        return

    generate_table(df, office.office_name)