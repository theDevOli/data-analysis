from dataclasses import dataclass

@dataclass
class Office:
    """
    Represents an office entity.

    Attributes:
        office_id (str): Unique identifier of the office.
        office_name (str): Name of the office.
        city (str): City where the office is located.
    """
    office_id: str
    office_name: str
    city: str