from dataclasses import dataclass

SQUARE_FEET_PER_ACRE = 43560

STATE_DICT = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}


@dataclass
class Property:
    price: int = 0

    location_state: str = "WV"
    location_address: str = ""
    coords = [0.0, 0.0]

    prop_type: str = "Single-Family Home"
    acreage: float = 0.5
    year_built: int = 2000
    tax_annual: float = 1000.00

    square_feet: int = 2000
    floors: int = 2
    beds: int = 3
    baths: int = 2
    baths_half: int = 0

    sys_heat: str = "Central"
    sys_ac: str = "Central"
    garages: int = 0

    def __str__(self): return "Property!"

    @staticmethod
    def deserialize(obj: dict):
        return Property(**obj)

    def serialize(self):
        return vars(self)

    def toAmesModel(self) -> tuple:
        return (
            self.prop_type,
            self.sys_ac,
            self.floors,
            self.garages,
            self.sys_heat,
            *self.coords,
            self.acreage * SQUARE_FEET_PER_ACRE, 
            self.baths + self.baths_half / 2,
            self.beds,
            self.square_feet,
            self.year_built
        )
    
    def toLocationModel(self) -> tuple:
        return (
            self.beds,
            self.baths + self.baths_half / 2,
            self.acreage,
            self.square_feet,
            self.tax_annual,
            *self.coords
        )

if __name__ == "__main__":
    pass