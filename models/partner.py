from dataclasses import dataclass

@dataclass
class Partner:
    """
    Represents a partner entity.
    Attributes:
        partner_id (int): Unique identifier of the partner.
        partner_name (str): Name of the partner.
    """
    partner_id: int
    partner_name: str