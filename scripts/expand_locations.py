#!/usr/bin/env python3
"""Append extra cities to reach 110+ locations. Commons names are Wikimedia file titles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOC = ROOT / "data" / "locations.json"
WEB_DATA = ROOT / "web" / "public" / "data"

# (id, lat, lon, country, region, file, commons)
EXTRA = [
    ("munich_01", 48.1372, 11.5755, "Германия", "Западная Европа", "munich.jpg", "Munich skyline.jpg"),
    ("frankfurt_01", 50.1109, 8.6821, "Германия", "Западная Европа", "frankfurt.jpg", "Frankfurt am Main, Skyline.jpg"),
    ("hamburg_01", 53.5511, 9.9937, "Германия", "Западная Европа", "hamburg.jpg", "Hamburg HafenCity Panorama.jpg"),
    ("cologne_01", 50.9375, 6.9603, "Германия", "Западная Европа", "cologne.jpg", "Köln - Dom - Hohenzollernbrücke.jpg"),
    ("dresden_01", 51.0504, 13.7373, "Германия", "Западная Европа", "dresden.jpg", "Dresden Frauenkirche night.jpg"),
    ("zurich_01", 47.3769, 8.5417, "Швейцария", "Западная Европа", "zurich.jpg", "Zürich - Grossmünster - Münsterbrücke - Limmat - Wühre 2010-10-21 16-39-08.JPG"),
    ("geneva_01", 46.2044, 6.1432, "Швейцария", "Западная Европа", "geneva.jpg", "Geneva Jet d'Eau.jpg"),
    ("brussels_01", 50.8466, 4.3528, "Бельгия", "Западная Европа", "brussels.jpg", "Grand Place, Brussels.jpg"),
    ("edinburgh_01", 55.9533, -3.1883, "Великобритания", "Западная Европа", "edinburgh.jpg", "Edinburgh Castle from Princes Street.jpg"),
    ("manchester_01", 53.4808, -2.2426, "Великобритания", "Западная Европа", "manchester.jpg", "Manchester Town Hall from St Peter's Square.jpg"),
    ("liverpool_01", 53.4084, -2.9916, "Великобритания", "Западная Европа", "liverpool.jpg", "Liverpool Pier Head.jpg"),
    ("milan_01", 45.4642, 9.19, "Италия", "Западная Европа", "milan.jpg", "Milano Duomo dal Palazzo Reale.jpg"),
    ("venice_01", 45.4343, 12.3388, "Италия", "Западная Европа", "venice.jpg", "Venice Grand Canal from Rialto Bridge.jpg"),
    ("florence_01", 43.7696, 11.2558, "Италия", "Западная Европа", "florence.jpg", "Florence Cathedral from Michelangelo Hill.jpg"),
    ("naples_01", 40.8518, 14.2681, "Италия", "Западная Европа", "naples.jpg", "Naples from Castel Sant'Elmo.jpg"),
    ("porto_01", 41.1579, -8.6291, "Португалия", "Западная Европа", "porto.jpg", "Porto - Cais da Ribeira.jpg"),
    ("seville_01", 37.3891, -5.9845, "Испания", "Западная Европа", "seville.jpg", "Seville - Plaza de España.jpg"),
    ("valencia_01", 39.4699, -0.3763, "Испания", "Западная Европа", "valencia.jpg", "Ciudad de las Artes y las Ciencias, Valencia.jpg"),
    ("lyon_01", 45.764, 4.8357, "Франция", "Западная Европа", "lyon.jpg", "Lyon - Basilique Notre-Dame de Fourvière.jpg"),
    ("marseille_01", 43.2965, 5.3698, "Франция", "Западная Европа", "marseille.jpg", "Marseille Vieux-Port.jpg"),
    ("nice_01", 43.7102, 7.262, "Франция", "Западная Европа", "nice.jpg", "Nice Promenade des Anglais.jpg"),
    ("zagreb_01", 45.815, 15.9819, "Хорватия", "Западная Европа", "zagreb.jpg", "Zagreb Cathedral and Kaptol.jpg"),
    ("belgrade_01", 44.7866, 20.4489, "Сербия", "Восточная Европа", "belgrade.jpg", "Belgrade Fortress and Kalemegdan.jpg"),
    ("bucharest_01", 44.4268, 26.1025, "Румыния", "Восточная Европа", "bucharest.jpg", "Palace of the Parliament, Bucharest.jpg"),
    ("sofia_01", 42.6977, 23.3219, "Болгария", "Восточная Европа", "sofia.jpg", "Alexander Nevsky Cathedral, Sofia.jpg"),
    ("tallinn_01", 59.437, 24.7536, "Эстония", "Восточная Европа", "tallinn.jpg", "Tallinn Old Town panorama.jpg"),
    ("riga_01", 56.9496, 24.1052, "Латвия", "Восточная Европа", "riga.jpg", "Riga Old Town from St Peter's Church.jpg"),
    ("vilnius_01", 54.6872, 25.2797, "Литва", "Восточная Европа", "vilnius.jpg", "Vilnius Cathedral Square.jpg"),
    ("ljubljana_01", 46.0569, 14.5058, "Словения", "Западная Европа", "ljubljana.jpg", "Ljubljana Triple Bridge.jpg"),
    ("bratislava_01", 48.1486, 17.1077, "Словакия", "Восточная Европа", "bratislava.jpg", "Bratislava Castle.jpg"),
    ("beijing_01", 39.9042, 116.4074, "Китай", "Восточная Азия", "beijing.jpg", "Forbidden City Beijing.jpg"),
    ("shanghai_01", 31.2304, 121.4737, "Китай", "Восточная Азия", "shanghai.jpg", "Shanghai Pudong skyline.jpg"),
    ("osaka_01", 34.6937, 135.5023, "Япония", "Восточная Азия", "osaka.jpg", "Osaka Castle.jpg"),
    ("kyoto_01", 35.0116, 135.7681, "Япония", "Восточная Азия", "kyoto.jpg", "Kiyomizu-dera Kyoto.jpg"),
    ("busan_01", 35.1796, 129.0756, "Южная Корея", "Восточная Азия", "busan.jpg", "Busan Haeundae Beach.jpg"),
    ("taipei_01", 25.033, 121.5654, "Тайвань", "Восточная Азия", "taipei.jpg", "Taipei 101 from Elephant Mountain.jpg"),
    ("manila_01", 14.5995, 120.9842, "Филиппины", "Юго-Восточная Азия", "manila.jpg", "Manila Bay sunset.jpg"),
    ("jakarta_01", -6.2088, 106.8456, "Индонезия", "Юго-Восточная Азия", "jakarta.jpg", "Jakarta skyline.jpg"),
    ("kuala_lumpur_01", 3.139, 101.6869, "Малайзия", "Юго-Восточная Азия", "kuala_lumpur.jpg", "Petronas Towers KL.jpg"),
    ("hanoi_01", 21.0285, 105.8542, "Вьетнам", "Юго-Восточная Азия", "hanoi.jpg", "Hoan Kiem Lake Hanoi.jpg"),
    ("ho_chi_minh_01", 10.8231, 106.6297, "Вьетнам", "Юго-Восточная Азия", "ho_chi_minh.jpg", "Ho Chi Minh City skyline.jpg"),
    ("colombo_01", 6.9271, 79.8612, "Шри-Ланка", "Южная Азия", "colombo.jpg", "Colombo skyline.jpg"),
    ("kathmandu_01", 27.7172, 85.324, "Непал", "Южная Азия", "kathmandu.jpg", "Kathmandu Durbar Square.jpg"),
    ("tashkent_01", 41.2995, 69.2401, "Узбекистан", "Центральная Азия", "tashkent.jpg", "Tashkent Independence Square.jpg"),
    ("almaty_01", 43.222, 76.8512, "Казахстан", "Центральная Азия", "almaty.jpg", "Almaty Kok Tobe.jpg"),
    ("baku_01", 40.4093, 49.8671, "Азербайджан", "Кавказ", "baku.jpg", "Baku Flame Towers.jpg"),
    ("tbilisi_01", 41.7151, 44.8271, "Грузия", "Кавказ", "tbilisi.jpg", "Tbilisi Old Town.jpg"),
    ("yerevan_01", 40.1792, 44.4991, "Армения", "Кавказ", "yerevan.jpg", "Yerevan Cascade.jpg"),
    ("boston_01", 42.3601, -71.0589, "США", "Северная Америка", "boston.jpg", "Boston skyline from Cambridge.jpg"),
    ("miami_01", 25.7617, -80.1918, "США", "Северная Америка", "miami.jpg", "Miami Beach skyline.jpg"),
    ("seattle_01", 47.6062, -122.3321, "США", "Северная Америка", "seattle.jpg", "Seattle skyline from Kerry Park.jpg"),
    ("denver_01", 39.7392, -104.9903, "США", "Северная Америка", "denver.jpg", "Denver skyline.jpg"),
    ("las_vegas_01", 36.1699, -115.1398, "США", "Северная Америка", "las_vegas.jpg", "Las Vegas Strip at night.jpg"),
    ("washington_dc_01", 38.9072, -77.0369, "США", "Северная Америка", "washington_dc.jpg", "Washington Monument and Capitol.jpg"),
    ("philadelphia_01", 39.9526, -75.1652, "США", "Северная Америка", "philadelphia.jpg", "Philadelphia skyline from Camden.jpg"),
    ("new_orleans_01", 29.9511, -90.0715, "США", "Северная Америка", "new_orleans.jpg", "New Orleans French Quarter.jpg"),
    ("atlanta_01", 33.749, -84.388, "США", "Северная Америка", "atlanta.jpg", "Atlanta skyline.jpg"),
    ("vancouver_01", 49.2827, -123.1207, "Канада", "Северная Америка", "vancouver.jpg", "Vancouver skyline from Stanley Park.jpg"),
    ("montreal_01", 45.5017, -73.5673, "Канада", "Северная Америка", "montreal.jpg", "Montreal Old Port.jpg"),
    ("quebec_city_01", 46.8139, -71.208, "Канада", "Северная Америка", "quebec_city.jpg", "Quebec City Château Frontenac.jpg"),
    ("sao_paulo_01", -23.5505, -46.6333, "Бразилия", "Южная Америка", "sao_paulo.jpg", "São Paulo skyline.jpg"),
    ("santiago_01", -33.4489, -70.6693, "Чили", "Южная Америка", "santiago.jpg", "Santiago de Chile skyline.jpg"),
    ("bogota_01", 4.711, -74.0721, "Колумбия", "Южная Америка", "bogota.jpg", "Bogotá La Candelaria.jpg"),
    ("quito_01", -0.1807, -78.4678, "Эквадор", "Южная Америка", "quito.jpg", "Quito historic center.jpg"),
    ("montevideo_01", -34.9011, -56.1645, "Уругвай", "Южная Америка", "montevideo.jpg", "Montevideo Rambla.jpg"),
    ("lagos_01", 6.5244, 3.3792, "Нигерия", "Западная Африка", "lagos.jpg", "Lagos skyline.jpg"),
    ("accra_01", 5.6037, -0.187, "Гана", "Западная Африка", "accra.jpg", "Independence Arch Accra.jpg"),
    ("casablanca_01", 33.5731, -7.5898, "Марокко", "Северная Африка", "casablanca.jpg", "Hassan II Mosque Casablanca.jpg"),
    ("tunis_01", 36.8065, 10.1815, "Тунис", "Северная Африка", "tunis.jpg", "Tunis Medina.jpg"),
    ("addis_ababa_01", 9.032, 38.7469, "Эфиопия", "Восточная Африка", "addis_ababa.jpg", "Addis Ababa skyline.jpg"),
    ("dar_es_salaam_01", -6.7924, 39.2083, "Танзания", "Восточная Африка", "dar_es_salaam.jpg", "Dar es Salaam harbour.jpg"),
    ("perth_01", -31.9505, 115.8605, "Австралия", "Океания", "perth.jpg", "Perth skyline from Kings Park.jpg"),
    ("melbourne_01", -37.8136, 144.9631, "Австралия", "Океания", "melbourne.jpg", "Melbourne skyline from Yarra River.jpg"),
    ("brisbane_01", -27.4698, 153.0251, "Австралия", "Океания", "brisbane.jpg", "Brisbane skyline.jpg"),
    ("christchurch_01", -43.5321, 172.6362, "Новая Зеландия", "Океания", "christchurch.jpg", "Christchurch Cathedral Square.jpg"),
    ("wellington_01", -41.2865, 174.7762, "Новая Зеландия", "Океания", "wellington.jpg", "Wellington harbour.jpg"),
    ("doha_01", 25.2854, 51.531, "Катар", "Ближний Восток", "doha.jpg", "Doha skyline.jpg"),
    ("riyadh_01", 24.7136, 46.6753, "Саудовская Аравия", "Ближний Восток", "riyadh.jpg", "Riyadh Kingdom Centre.jpg"),
    ("tehran_01", 35.6892, 51.389, "Иран", "Ближний Восток", "tehran.jpg", "Tehran Milad Tower.jpg"),
    ("amman_01", 31.9454, 35.9284, "Иордания", "Ближний Восток", "amman.jpg", "Amman Citadel.jpg"),
    ("beirut_01", 33.8938, 35.5018, "Ливан", "Ближний Восток", "beirut.jpg", "Beirut Raouche Rocks.jpg"),
    ("minsk_01", 53.9045, 27.5615, "Беларусь", "Восточная Европа", "minsk.jpg", "Minsk Independence Square.jpg"),
    ("kiev_01", 50.4501, 30.5234, "Украина", "Восточная Европа", "kiev.jpg", "Kyiv Maidan Nezalezhnosti.jpg"),
    ("st_petersburg_01", 59.9343, 30.3351, "Россия", "Восточная Европа", "st_petersburg.jpg", "Saint Petersburg Palace Bridge.jpg"),
    ("novosibirsk_01", 55.0084, 82.9357, "Россия", "Восточная Европа", "novosibirsk.jpg", "Novosibirsk Opera and Ballet Theatre.jpg"),
    ("vladivostok_01", 43.1332, 131.9113, "Россия", "Восточная Азия", "vladivostok.jpg", "Vladivostok Golden Bridge.jpg"),
    ("ulaanbaatar_01", 47.8864, 106.9057, "Монголия", "Восточная Азия", "ulaanbaatar.jpg", "Ulaanbaatar Sükhbaatar Square.jpg"),
    ("phnom_penh_01", 11.5564, 104.9282, "Камбоджа", "Юго-Восточная Азия", "phnom_penh.jpg", "Phnom Penh Royal Palace.jpg"),
    ("yangon_01", 16.8661, 96.1951, "Мьянма", "Юго-Восточная Азия", "yangon.jpg", "Shwedagon Pagoda Yangon.jpg"),
    ("dhaka_01", 23.8103, 90.4125, "Бангладеш", "Южная Азия", "dhaka.jpg", "Dhaka Lalbagh Fort.jpg"),
    ("islamabad_01", 33.6844, 73.0479, "Пакистан", "Южная Азия", "islamabad.jpg", "Faisal Mosque Islamabad.jpg"),
    ("karachi_01", 24.8607, 67.0011, "Пакистан", "Южная Азия", "karachi.jpg", "Karachi Clifton Beach.jpg"),
    ("portland_01", 45.5152, -122.6784, "США", "Северная Америка", "portland.jpg", "Portland Oregon skyline.jpg"),
    ("austin_01", 30.2672, -97.7431, "США", "Северная Америка", "austin.jpg", "Austin Texas skyline.jpg"),
    ("nashville_01", 36.1627, -86.7816, "США", "Северная Америка", "nashville.jpg", "Nashville skyline.jpg"),
    ("detroit_01", 42.3314, -83.0458, "США", "Северная Америка", "detroit.jpg", "Detroit skyline from Windsor.jpg"),
    ("minneapolis_01", 44.9778, -93.265, "США", "Северная Америка", "minneapolis.jpg", "Minneapolis skyline.jpg"),
    ("calgary_01", 51.0447, -114.0719, "Канада", "Северная Америка", "calgary.jpg", "Calgary skyline.jpg"),
    ("ottawa_01", 45.4215, -75.6972, "Канада", "Северная Америка", "ottawa.jpg", "Parliament Hill Ottawa.jpg"),
    ("caracas_01", 10.4806, -66.9036, "Венесуэла", "Южная Америка", "caracas.jpg", "Caracas Avila.jpg"),
    ("medellin_01", 6.2476, -75.5658, "Колумбия", "Южная Америка", "medellin.jpg", "Medellín skyline.jpg"),
    ("cusco_01", -13.5319, -71.9675, "Перу", "Южная Америка", "cusco.jpg", "Cusco Plaza de Armas.jpg"),
    ("la_paz_01", -16.5, -68.15, "Боливия", "Южная Америка", "la_paz.jpg", "La Paz Bolivia panorama.jpg"),
    ("reykjanes_01", 63.985, -22.6056, "Исландия", "Скандинавия", "reykjanes.jpg", "Blue Lagoon Iceland.jpg"),
    ("bergen_01", 60.3913, 5.3221, "Норвегия", "Скандинавия", "bergen.jpg", "Bryggen Bergen.jpg"),
    ("gothenburg_01", 57.7089, 11.9746, "Швеция", "Скандинавия", "gothenburg.jpg", "Gothenburg harbour.jpg"),
    ("turku_01", 60.4518, 22.2666, "Финляндия", "Скандинавия", "turku.jpg", "Turku Cathedral.jpg"),
    ("luxembourg_01", 49.6116, 6.1319, "Люксембург", "Западная Европа", "luxembourg.jpg", "Luxembourg City Grund.jpg"),
    ("monaco_01", 43.7384, 7.4246, "Монако", "Западная Европа", "monaco.jpg", "Monaco harbour.jpg"),
    ("malta_valletta_01", 35.8989, 14.5146, "Мальта", "Западная Европа", "valletta.jpg", "Valletta Malta panorama.jpg"),
    ("nicosia_01", 35.1856, 33.3823, "Кипр", "Западная Европа", "nicosia.jpg", "Nicosia old town.jpg"),
    ("sarajevo_01", 43.8563, 18.4131, "Босния и Герцеговина", "Западная Европа", "sarajevo.jpg", "Sarajevo Baščaršija.jpg"),
    ("skopje_01", 41.9981, 21.4254, "Северная Македония", "Восточная Европа", "skopje.jpg", "Skopje Macedonia Square.jpg"),
    ("tirana_01", 41.3275, 19.8187, "Албания", "Восточная Европа", "tirana.jpg", "Tirana Skanderbeg Square.jpg"),
    ("chisinau_01", 47.0105, 28.8638, "Молдова", "Восточная Европа", "chisinau.jpg", "Chișinău Cathedral.jpg"),
    ("bahrain_manama_01", 26.2235, 50.5876, "Бахрейн", "Ближний Восток", "manama.jpg", "Manama Bahrain skyline.jpg"),
    ("muscat_01", 23.588, 58.3829, "Оман", "Ближний Восток", "muscat.jpg", "Sultan Qaboos Grand Mosque.jpg"),
    ("kuwait_city_01", 29.3759, 47.9774, "Кувейт", "Ближний Восток", "kuwait_city.jpg", "Kuwait Towers.jpg"),
    ("abu_dhabi_01", 24.4539, 54.3773, "ОАЭ", "Ближний Восток", "abu_dhabi.jpg", "Sheikh Zayed Grand Mosque.jpg"),
    ("nepal_pokhara_01", 28.2096, 83.9856, "Непал", "Южная Азия", "pokhara.jpg", "Pokhara Phewa Lake.jpg"),
    ("fiji_suva_01", -18.1248, 178.4501, "Фиджи", "Океания", "suva.jpg", "Suva Fiji harbour.jpg"),
    ("honolulu_01", 21.3069, -157.8583, "США", "Океания", "honolulu.jpg", "Waikiki Beach Honolulu.jpg"),
    ("anchorage_01", 61.2181, -149.9003, "США", "Северная Америка", "anchorage.jpg", "Anchorage Alaska skyline.jpg"),
    ("reykjavik_harbour_01", 64.1505, -21.9405, "Исландия", "Скандинавия", "reykjavik_harbour.jpg", "Reykjavik harbour panorama.jpg"),
]


def main() -> None:
    data = json.loads(LOC.read_text(encoding="utf-8"))
    existing_ids = {loc["id"] for loc in data["locations"]}
    added = 0
    for row in EXTRA:
        lid, lat, lon, country, region, file, commons = row
        if lid in existing_ids:
            continue
        data["locations"].append(
            {
                "id": lid,
                "lat": lat,
                "lon": lon,
                "country": country,
                "region": region,
                "panoramas": [{"file": file, "commons": commons}],
            }
        )
        existing_ids.add(lid)
        added += 1
    LOC.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOC, WEB_DATA / "locations.json")
    print(f"Added {added} cities. Total: {len(data['locations'])}")


if __name__ == "__main__":
    main()
