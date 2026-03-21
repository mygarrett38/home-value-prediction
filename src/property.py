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
    price: float = 0

    location_state: int = 47
    location_address: str = "New Property"
    coords = [0.0, 0.0]

    prop_type: int = 0
    acreage: float = 0.5
    year_built: int = 1985
    tax_annual: float = 800.00

    square_feet: int = 2000
    floors: int = 2
    beds: int = 3
    baths: int = 2
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
        return self.baths + self.baths_half / 2
    
    def attributes(self):
        return [
            f"{self.square_feet:,} sq. ft.",
            f"{self.beds} bed",
            f"{self.totalBaths():.1f} bath",
        ]

    def toAmesModel(self) -> tuple:
        return (
            self.prop_type,
            self.sys_ac,
            self.floors,
            self.garages,
            self.sys_heat,
            *self.coords,
            self.acreage * SQUARE_FEET_PER_ACRE, 
            self.totalBaths(),
            self.beds,
            self.square_feet,
            self.year_built
        )
    
    def toLocationModel(self) -> tuple:
        return (
            self.beds,
            self.totalBaths(),
            self.acreage,
            self.square_feet,
            self.tax_annual,
            *self.coords
        )

if __name__ == "__main__":
    pass