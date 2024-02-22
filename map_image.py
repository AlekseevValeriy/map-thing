import requests
from enum import StrEnum
from typing import Optional


class MapType(StrEnum):
    SCHEMA = 'map'
    SATELLITE = 'sat'
    HYBRID = 'hyb'

class MapImage:
    SCALE_MAX = 35
    SCALE_MIN = 0.000125
    API = 'http://static-maps.yandex.ru/1.x/'

    def __init__(self):
        self._longitude: float = 37.530887
        self._lantitude: float = 55.703118
        self._scale: float = 0.002
        self._type: MapType = MapType.SCHEMA

    @property
    def image(self) -> bytes | None:
        params = {
            'll': ','.join(map(str, (self._longitude, self._lantitude))),
            'spn': ','.join(map(str, (self._scale, self._scale))),
            'l': self._type
        }
        response = requests.get(self.API, params=params)
        if not response:
            print('Ошибка Вполнения запроса:')
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return None
        return response.content

    def scaling(self, coeff: float) -> None:
        scale = self._scale * coeff
        if self.SCALE_MIN <= scale <= self.SCALE_MAX:
            self._scale = scale