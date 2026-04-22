from dataclasses import dataclass, field

from location import Location

# These are conversion dictionaries that help convert display values to ML model values
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

# The dataclass is used to make initialization and access easier throughout the program
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

    def serialize(self):
        return {
            **vars(self),
            "location": Location.serialize(self.location)
        }
    
    def totalBaths(self):
        """ Returns the total number of bathrooms, including the half bathroom weights. """
        return self.baths + self.baths_half / 2.0
    
    def attributes(self):
        """ Returns the attributes listed below the property on the property manager screen. """
        return [
            f"{self.square_feet:,} sq. ft.",
            f"{self.beds} bed",
            f"{self.totalBaths()} bath",
        ]

    def toAmesModel(self) -> list:
        """ Converts this property into a format that the Ames ML model can use. """
        return [
            HOME_TYPES.get(self.prop_type, "1Fam"),
            int(self.sys_ac),
            self.floors,
            self.garages,
            HEAT_TYPES.get(self.sys_heat, "GasA"), # type: ignore
            self.acreage * SQUARE_FEET_PER_ACRE, 
            self.baths + self.baths_half,
            self.beds,
            self.square_feet,
            self.year_built
        ]
    
    def toLocationModel(self) -> list:
        """ Converts this property into a format that the Location ML model can use. """
        return [
            self.beds,
            self.baths + self.baths_half,
            self.acreage,
            self.square_feet,
            self.tax_annual,
            *self.location.getCoordinates()
        ]

if __name__ == "__main__":
    pass