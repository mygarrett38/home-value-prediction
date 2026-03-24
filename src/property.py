from dataclasses import dataclass, field

from location import Location

SQUARE_FEET_PER_ACRE = 43560

HEAT_TYPES = {
    "Central",
    "Baseboard",
    "Floor / Wall",
    "Solar",
    "Gravity",
    "Other"
}

@dataclass
class Property:
    price: float = 0

    location: Location = field(default_factory=lambda: Location("25443", "123 Main St"))

    prop_type: str = "Single-Family Home"
    acreage: float = 0.5
    year_built: int = 2000
    tax_annual: float = 2000.00

    square_feet: int = 1000
    floors: int = 2
    beds: int = 0
    baths: int = 0
    baths_half: int = 0

    sys_heat: str | None = "Central"
    sys_ac: bool = True
    garages: int = 0

    @staticmethod
    def deserialize(obj: dict):
        return Property(**obj)

    def serialize(self):
        return vars(self)
    
    def totalBaths(self):
        return self.baths + self.baths_half
    
    def attributes(self):
        return [
            f"{self.square_feet:,} sq. ft.",
            f"{self.beds} bed",
            f"{self.totalBaths():.1f} bath",
        ]

    def toAmesModel(self) -> list:
        return [
            "1Fam", #self.prop_type,
            int(self.sys_ac),
            self.floors,
            self.garages,
            "GasA", #self.sys_heat,
            self.acreage * SQUARE_FEET_PER_ACRE, 
            self.totalBaths(),
            self.beds,
            self.square_feet,
            self.year_built
        ]
    
    def toLocationModel(self) -> list:
        return [
            self.beds,
            self.totalBaths(),
            self.acreage,
            self.square_feet,
            self.tax_annual,
            *self.location.getCoordinates()
        ]

if __name__ == "__main__":
    pass