import pandas as pd
from sqlalchemy import text
from db_context import get_engine
from models.office import Office

engine = get_engine()

def get_offices()-> list[Office]:
    """
    Returns a list of offices from the database.
    Returns:
        list[Office]: A list of Office objects.
    """
    query = "SELECT office_id, office_name FROM customers.office;"
    df = pd.read_sql_query(query, engine)

    return [Office(row.office_id, row.office_name) for _, row in df.iterrows()]


def get_office_data(office_id: str) -> pd.DataFrame:
    """
    Retrieves financial data based on the provided office_id.
    Args:
        office_id (str): The ID of the office for which to retrieve data.
    Returns:
        pd.DataFrame: A DataFrame containing the retrieved data for the specified office.
    """
    query = text(""" 
                SELECT
                    o.office_name AS "Escritório",
                    c.client_name AS "Cliente",
                    pt.partner_name AS "Projetista",
                    SUM(c2.price - COALESCE(cf.total_paid,0)) AS "Valor (R$)"
                FROM document.protocol p
                INNER JOIN customers.client c 
                    ON c.client_id = p.client_id
                INNER JOIN customers.property pr
                    ON p.property_id = pr.property_id
                INNER JOIN customers.partner pt 
                    ON pt.partner_id = p.partner_id
                INNER JOIN customers.office o
                    ON o.office_id = pt.office_id
                INNER JOIN parameters."catalog" c2
                    ON p.catalog_id = c2.catalog_id
                LEFT JOIN cash_flow.cash_flow cf 
                ON p.cash_flow_id  = cf.cash_flow_id 
                WHERE 
                    EXTRACT(YEAR FROM p.entry_date) = 2026
                    AND p.partner_id IS NOT NULL
                    AND(
                        p.cash_flow_id IS NULL
                        OR 
                        cf.total_paid < 80
                    )
                    AND o.office_id = :office_id
                GROUP BY GROUPING SETS (
                    (o.office_name, pt.partner_name, c.client_name),
                    (o.office_name),                
                    ()                        
                )
                HAVING SUM(c2.price - COALESCE(cf.total_paid,0)) > 0
                ORDER BY
                    GROUPING(o.office_name),      
                    o.office_name,
                    GROUPING(c.client_name),       
                    c.client_name;
                """
                )
    df = pd.read_sql_query(query, engine, params={"office_id": office_id})
    if not df.empty:
        df = df.drop(df.index[-1])
        df.iloc[-1, 0] = ""
        df.iloc[-1, 1] = "Total (R$)"
        df.iloc[-1, 2] = ""
        df['Valor (R$)'] = df['Valor (R$)'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    return df