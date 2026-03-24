import googlemaps
import googlemaps.maps

import os
import dotenv
from io import BytesIO

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox

def absolutePath(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

class Location:
    def __init__(self, zip_code: str, address: str, coordinates: tuple[float, float] = (39.0, -77.0)):
        self.zip_code = zip_code
        self.address = address
        self.coordinates = coordinates 
        self.mapImage: QPixmap | None = None

    def __str__(self):
        return self.getAddress()
    
    def __eq__(self, other: "Location"):
        return type(other) == Location and self.zip_code == other.zip_code and self.address == other.address
    
    def getMapImage(self):
        return QPixmap() if self.mapImage is None else self.mapImage
    
    def getZipCode(self):
        return self.zip_code

    def getAddress(self):
        return self.address

    def getCoordinates(self):
        return self.coordinates
    
    def requestMap(self, client: googlemaps.Client):
        map_args = {
            "size": (400, 300),
            "zoom": 15,
            "markers": ",".join((str(c) for c in self.coordinates)),
        }
        pixmap = QPixmap()

        if True: # try:
            with BytesIO() as img_buf:
                for chunk in client.static_map(**map_args): # type: ignore
                    if chunk: img_buf.write(chunk)

                if not pixmap.loadFromData(img_buf.getvalue()):
                    raise BufferError("Buffer could not load properly.")
        # except: pass
        
        self.mapImage = pixmap

    def requestLocation(self, client: googlemaps.Client):
        if not (0 < int(self.zip_code) < 100000): self.zip_code = "25443" # Default to Shepherdstown, WV

        result: dict = {}
        try:
            result = client.geocode(self.address, components={"country": "US", "postal_code": self.zip_code})[0] # type: ignore
        except googlemaps.exceptions.ApiError as apiError:
            print(apiError)
            return
        except Exception as error:
            QMessageBox.information(None, "Location Error", "There was an error requesting this address.\n\nPlease try again.")
            return

        front_address_components = result["address_components"][:1]

        if [obj["types"][0] for obj in front_address_components] == ["street_address", "route"]:
            self.address = " ".join([obj["short_name"] for obj in front_address_components])

        self.coordinates = tuple(result["geometry"]["location"].values())
        self.requestMap(client)


    @staticmethod
    def load():
        dotenv.load_dotenv(absolutePath("../.env"))
        apiKey = os.getenv("API_KEY")
        if apiKey is None:
            raise LookupError("Location API Key not found. Make sure the .env file is present with a valid API key.")
        return googlemaps.Client(key=apiKey)