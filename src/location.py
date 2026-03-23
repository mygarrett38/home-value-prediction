import googlemaps
import dotenv
import os

from PySide6.QtWidgets import QMessageBox

from config import absolutePath
from property import Property

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

class Location:
    def __init__(self, **kwargs):
        self.address: str = kwargs["formatted_address"]
        self.coordinates: tuple[float, float] = tuple(kwargs["geometry"]["location"].values())
        self.args = kwargs

    def __str__(self):
        return self.getFullAddress()

    def getFullAddress(self):
        return self.address

    def getCoordinates(self):
        return self.coordinates

    @staticmethod
    def requestLocation(client: googlemaps.Client, prop: Property):
        if not (0 <= prop.location_state <= 50): prop.location_state = 48 # Default to WV
        address_str = f"{prop.location_address}, {list(STATE_DICT.keys())[prop.location_state]}"

        result = []
        try:
            result = client.geocode(address_str, components={"country": "US"}) # type: ignore
        except googlemaps.exceptions.ApiError as apiError:
            print(apiError)
        except Exception as error:
            QMessageBox.information(None, "Location Error", "There was an error requesting this address.\n\nPlease try again.")

        print(result)
        return [Location(**entry) for entry in result]

    @staticmethod
    def load():
        dotenv.load_dotenv(absolutePath("../.env"))
        apiKey = os.getenv("API_KEY")
        if apiKey is None:
            raise LookupError("Location API Key not found. Make sure the .env file is present with a valid API key.")
        return googlemaps.Client(key=apiKey)