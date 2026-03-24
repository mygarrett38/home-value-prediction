from dataclasses import dataclass, field

from location import Location

SQUARE_FEET_PER_ACRE = 43560

HOME_TYPES = {
    "Single-Family Home": "1Fam",
    "Multi-Family Home": "2fmCon",
    "Townhouse": "TwnhsE",
    "Duplex, Triplex, etc.": "Duplex"
}

HEAT_TYPES = {
    "Central": "GasA",
    "Forced Air": "GasA",
    "Steam": "GasW",
    "Floor": "Floor",
    "Wall": "Wall",
    "Gravity": "Grav",
    "Other": "OthW"
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
        if "coordinates" in obj:
            return Location.deserialize(obj)
        
        return Property(**obj)

    def serialize(self):
        return {
            **vars(self),
            "location": Location.serialize(self.location)
        }
    
    def totalBaths(self):
        return self.baths + self.baths_half
    
    def attributes(self):
        return [
            f"{self.square_feet:,} sq. ft.",
            f"{self.beds} bed",
            f"{self.totalBaths()} bath",
        ]

    def toAmesModel(self) -> list:
        return [
            HOME_TYPES.get(self.prop_type, "1Fam"),
            int(self.sys_ac),
            self.floors,
            self.garages,
            HEAT_TYPES.get(self.sys_heat, "GasA"), # type: ignore
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