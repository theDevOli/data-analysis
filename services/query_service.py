import pandas as pd
from sqlalchemy import text
from db_context import get_engine
from models.office import Office
from models.partner import Partner

engine = get_engine()

def get_offices()-> list[Office]:
    """
    Returns a list of offices from the database.
    Returns:
        list[Office]: A list of Office objects.
    """
    query = "SELECT office_id, office_name, city FROM customers.office;"
    df = pd.read_sql_query(query, engine)

    return [Office(row.office_id, row.office_name, row.city) for _, row in df.iterrows()]

def get_partners() -> list[Partner]:
    """
    Retrieves a list of partners from the database.
    Returns:
        list[Partner]: A list of Partner objects.
    """
    query = "SELECT partner_id, partner_name FROM customers.partner;"
    df = pd.read_sql_query(query, engine)
    return [Partner(row.partner_id, row.partner_name) for _, row in df.iterrows()]

def get_partner_data(partner_id: str) -> pd.DataFrame:
    """
    Retrieves financial data based on the provided partner_id.
    Args:
        partner_id (str): The ID of the partner for which to retrieve data.
    Returns:
        pd.DataFrame: A DataFrame containing the retrieved data for the specified partner.
    """
    query = text(""" 
                SELECT
                    p.protocol_id AS protocolo,
                    c.client_name AS cliente,
                    pt.partner_name AS projetista,
                    SUM(c2.price) - SUM(COALESCE(cf.total_paid, 0)) AS "Valor (R$)"

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
                    ON p.cash_flow_id = cf.cash_flow_id 

                WHERE 
                    EXTRACT(YEAR FROM p.entry_date) = 2026
                    AND p.partner_id = :partner_id
                    AND (
                        p.cash_flow_id IS NULL
                        OR cf.total_paid < 80
                    )

                GROUP BY GROUPING SETS (
                    (pt.partner_name, c.client_name, p.protocol_id),
                    (pt.partner_name)
                )

                ORDER BY    
                    pt.partner_name,
                    c.client_name,
                    p.protocol_id;
                 """)
    df = pd.read_sql_query(query, engine, params={"partner_id": partner_id})
    if not df.empty:
        df.iloc[-1, 0] = ""
        df.iloc[-1, 1] = "Total (R$)"
        df.iloc[-1, 2] = ""
        df['Valor (R$)'] = df['Valor (R$)'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    return df
    
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
        df.iloc[-1, 0] = "Total (R$)"
        df.iloc[-1, 1] = ""
        df['Valor (R$)'] = df['Valor (R$)'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    return df

def get_statistics(office_id: str) -> pd.DataFrame:
    """
    Retrieves statistical data based on the provided office_id.
    Args:
        office_id (str): The ID of the office for which to retrieve statistics.
    Returns:
        pd.DataFrame: A DataFrame containing the retrieved statistical data for the specified office.
    """
    query = text("""
                    SELECT
                        o.office_name AS "Escritório",
                        o.city AS "Cidade",

                        COUNT(p.protocol_id) AS "Total de Análises",

                        SUM(c2.price) AS "Total Previsto",

                        -- só pagamentos reais
                        SUM(
                            CASE 
                                WHEN c.client_tax_id != '00000000000'
                                THEN COALESCE(cf.total_paid, 0)
                                ELSE 0
                            END
                        ) AS "Total Pago",

                        -- crédito separado corretamente
                        SUM(
                            CASE 
                                WHEN c.client_tax_id = '00000000000'
                                    AND p.partner_id IS NOT NULL
                                THEN COALESCE(cf.total_paid, 0)
                                ELSE 0
                            END
                        ) AS "Crédito",

                        -- saldo devedor (sem considerar crédito)
                        GREATEST(
                            SUM(c2.price) - SUM(
                                CASE 
                                    WHEN c.client_tax_id != '00000000000'
                                    THEN COALESCE(cf.total_paid, 0)
                                    ELSE 0
                                END
                            ),
                            0
                        ) AS "Saldo Devedor",

                        -- percentual baseado só em pagamento real
                        CASE 
                            WHEN SUM(c2.price) = 0 THEN 0
                            ELSE ROUND(
                                SUM(
                                    CASE 
                                        WHEN c.client_tax_id != '00000000000'
                                        THEN COALESCE(cf.total_paid, 0)
                                        ELSE 0
                                    END
                                ) / SUM(c2.price) * 100,
                                2
                            )
                        END AS "Percentual Recebido"

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
                        ON p.cash_flow_id = cf.cash_flow_id 

                    WHERE 
                        EXTRACT(YEAR FROM p.entry_date) = 2026
                        AND o.office_id = :office_id

                    GROUP BY 
                        o.office_name, o.city
                 """)
    df = pd.read_sql_query(query, engine, params={"office_id": office_id})
    if not df.empty:
        df['Total Previsto'] = df['Total Previsto'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Total Pago'] = df['Total Pago'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Saldo Devedor'] = df['Saldo Devedor'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Crédito'] = df['Crédito'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Percentual Recebido'] = df['Percentual Recebido'].apply(lambda x: f"{x:.2f}%")
    return df