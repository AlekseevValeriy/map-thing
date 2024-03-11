import io

import requests
from enum import StrEnum
from PIL import Image


class MapType(StrEnum):
    SCHEMA = 'map'
    SATELLITE = 'sat'
    HYBRID = 'skl'

class MapImage:
    SCALE_MAX = 35
    SCALE_MIN = 0.000125
    API = 'http://static-maps.yandex.ru/1.x/'

    def __init__(self):
        self._longitude: float = 37.530887
        self._latitude: float = 55.703118
        self._scale: float = 0.00005
        self._type: MapType = MapType.SCHEMA
        self.geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        self.flags = []

    def get_flags(self):
        return self.flags

    def change_position(self, place: str) -> None:
        geocoder_params = {
            "apikey": "996e91c0-34f6-4b50-a2c6-da63e579d3e3",
            "geocode": place,
            "format": "json"
        }

        response = requests.get(self.geocoder_api_server, params=geocoder_params)
        json_response = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            "pos"]
        self._longitude, self._latitude = map(float, json_response.split(" "))
        if (coordinate := (self._longitude, self._latitude)) not in self.flags:
            self.flags.append(coordinate)

    def get_current_address(self) -> str:
        geocoder_params = {
            "apikey": "996e91c0-34f6-4b50-a2c6-da63e579d3e3",
            "geocode": f'{self._longitude},{self._latitude}',
            "format": "json"
        }
        response = requests.get(self.geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        return json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['Address']['formatted']



    def  _get_image(self, _type):
        params = {
            'll': ','.join(map(str, (self._longitude, self._latitude))),
                'spn': ','.join(map(str, (self._scale, self._scale))),
            'l': self._type,
            'pt': '~'.join(f'{lo},{la},round' for lo, la in self.flags)
        }
        response = requests.get(self.API, params=params)
        if not response:
            print('Ошибка Вполнения запроса:')
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return None
        return response.content

    def drop_marks(self):
        self.flags = []

    @property
    def image(self) -> bytes | None:
        if self._type != MapType.HYBRID:
            return self._get_image(self._type)
        satellite_image = Image.open(io.BytesIO(self._get_image(MapType.SATELLITE)))
        hybrid_mask = Image.open(io.BytesIO(self._get_image(MapType.HYBRID)))
        satellite_image.paste(hybrid_mask, (0, 0), hybrid_mask)
        imh_byte_arr = io.BytesIO()
        satellite_image.save(imh_byte_arr, format='PNG')
        return imh_byte_arr.getvalue()

    def scaling(self, coeff: float) -> None:
        scale = self._scale * coeff
        if self.SCALE_MIN <= scale <= self.SCALE_MAX:
            self._scale = scale

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float):
        if not (-180.0 <= value <= 180.0):
            value += 180.0
            value %= 360.0
            value -= 180.0
        self._longitude = value

    @property
    def latitude(self) -> float:
        return self._latitude

    @longitude.setter
    def latitude(self, value: float):
        if -90.0 <= value <= 90.0:
            self._latitude = value

    def move(self, d_longitude: float, d_latitude: float):
        self._longitude += d_longitude
        self._latitude += d_latitude

    def screen_up(self):
        self.move(0, self._scale)

    def screen_down(self):
        self.move(0, -self._scale)

    def screen_left(self):
        self.move(-self._scale, 0)

    def screen_right(self):
        self.move(self._scale, 0)

    def set_type(self, _type):
        self._type = _type

