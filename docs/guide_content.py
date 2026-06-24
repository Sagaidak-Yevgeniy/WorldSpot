"""Содержание методички WorldSpot."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generate_html_guide import HtmlBuilder


def write_chapters(pdf: "HtmlBuilder", toc: list) -> None:
    ch = pdf.chapter

    ch("Введение: что такое WorldSpot", toc)
    pdf.paragraph(
        "WorldSpot — географическая игра, вдохновлённая GeoGuessr. Игрок видит панораму "
        "улицы или природы и должен указать на карте мира, где, по его мнению, сделан снимок. "
        "Чем ближе угадывание к реальной точке, тем больше очков."
    )
    pdf.paragraph(
        "Это пособие проведёт вас от пустой папки до работающего прототипа на Python и pygame "
        "и опубликованного репозитория на GitHub. Мы создаём не клон GeoGuessr, а свою игру "
        "с уникальной статистикой: процент успеха по странам и регионам вместо флагов."
    )
    pdf.heading("Особенности WorldSpot", level=2)
    pdf.bullet("Знакомый геймплей: панорама → догадка на карте → результат.")
    pdf.bullet("Минималистичный современный интерфейс.")
    pdf.bullet("Обычный и рейтинговый режимы.")
    pdf.bullet("Подробная статистика после каждого раунда.")
    pdf.bullet("Процент угадываний по странам и регионам (без флагов).")
    pdf.bullet("История игр, достижения и личные рекорды.")
    pdf.heading("Что вы создадите", level=2)
    pdf.bullet("Окно игры с панорамой и интерактивной картой мира.")
    pdf.bullet("Систему очков по расстоянию (формула Haversine).")
    pdf.bullet("Экран результатов с точностью в км и очками.")
    pdf.bullet("Таблицу статистики: % по странам, лучшие и худшие регионы.")
    pdf.bullet("Сохранение истории и достижений в JSON.")
    pdf.exercise(
        "Старт",
        [
            "Установите Python 3.10+ и создайте папку WorldSpot.",
            "Откройте проект в VS Code или Cursor.",
            "Прочитайте README.md в корне шаблона.",
        ],
    )

    ch("Анатомия игры в стиле GeoGuessr", toc)
    pdf.paragraph(
        "Классический раунд GeoGuessr состоит из пяти этапов: показ локации, исследование "
        "(поворот камеры, движение — в полной версии), выбор точки на карте, подсчёт очков, "
        "показ правильного ответа. WorldSpot реализует ядро этого цикла."
    )
    pdf.heading("Игровой цикл раунда", level=2)
    pdf.numbered_item(1, "PANORAMA — игрок изучает изображение локации.")
    pdf.numbered_item(2, "GUESS — клик по карте мира, подтверждение.")
    pdf.numbered_item(3, "REVEAL — линия от догадки до правды, расстояние, очки.")
    pdf.numbered_item(4, "STATS — обновление % по стране и региону.")
    pdf.numbered_item(5, "NEXT — следующая локация или итоги серии.")
    pdf.table(
        ["Система", "Назначение", "Сложность"],
        [
            ["Game Loop", "Сцены и переключение режимов", "Низкая"],
            ["Locations DB", "JSON с lat/lon, страной, панорамой", "Низкая"],
            ["Map Widget", "Клик → координаты", "Средняя"],
            ["Scoring", "Haversine + очки", "Средняя"],
            ["Stats Engine", "% по странам/регионам", "Средняя"],
            ["History + Achievements", "Прогресс игрока", "Низкая"],
        ],
    )
    pdf.tip(
        "Начните с 5–10 тестовых локаций в JSON. Панорамы — любые JPG 1280×720 "
        "с указанием координат в метаданных."
    )

    ch("Подготовка окружения", toc)
    pdf.code_block(
        "cd WorldSpot\n"
        "python3 -m venv .venv\n"
        "source .venv/bin/activate\n"
        "pip install pygame pillow\n"
        "pip freeze > requirements.txt"
    )
    pdf.code_block("python3 -c \"import pygame; from PIL import Image; print('OK')\"")
    pdf.warning(
        "Для реальных уличных панорам позже подключите Mapillary API или Google Street View "
        "Static API — нужны ключи и соблюдение лицензий."
    )

    ch("Структура проекта WorldSpot", toc)
    pdf.code_block(
        "WorldSpot/\n"
        "|-- assets/\n"
        "|   |-- panoramas/     # JPG панорамы локаций\n"
        "|   +-- ui/            # карта мира, иконки\n"
        "|-- data/\n"
        "|   |-- locations.json # база точек\n"
        "|   |-- achievements.json\n"
        "|   +-- config.json    # режимы, лимиты\n"
        "|-- src/\n"
        "|   |-- main.py\n"
        "|   |-- settings.py\n"
        "|   |-- game.py\n"
        "|   |-- scenes/        # menu, round, results, stats\n"
        "|   +-- systems/       # scoring, stats, save, locations\n"
        "|-- docs/              # эта методичка\n"
        "|-- .gitignore\n"
        "|-- requirements.txt\n"
        "+-- README.md"
    )
    pdf.code_block(
        "# src/settings.py\n"
        "WIDTH, HEIGHT = 1280, 720\n"
        "FPS = 60\n"
        "TITLE = 'WorldSpot'\n"
        "MAX_SCORE = 5000\n"
        "MAP_RECT = (40, 400, 500, 260)  # x,y,w,h\n"
        "PANORAMA_RECT = (40, 40, 800, 340)\n"
        "ROUND_TIME_RANKED = 180  # секунд"
    )

    ch("База локаций: data/locations.json", toc)
    pdf.paragraph(
        "Каждая локация — запись с координатами, страной, регионом и файлом панорамы. "
        "Именно здесь хранится «правда», с которой сравнивается догадка игрока."
    )
    pdf.code_block(
        "{\n"
        '  "locations": [\n'
        "    {\n"
        '      "id": "oslo_01",\n'
        '      "lat": 59.9139,\n'
        '      "lon": 10.7522,\n'
        '      "country": "Норвегия",\n'
        '      "region": "Скандинавия",\n'
        '      "panorama": "oslo_fjord.jpg",\n'
        '      "difficulty": "medium"\n'
        "    },\n"
        "    {\n"
        '      "id": "tokyo_01",\n'
        '      "lat": 35.6762,\n'
        '      "lon": 139.6503,\n'
        '      "country": "Япония",\n'
        '      "region": "Восточная Азия",\n'
        '      "panorama": "tokyo_street.jpg"\n'
        "    }\n"
        "  ]\n"
        "}"
    )
    pdf.code_block(
        "# src/systems/locations.py\n"
        "import json\n"
        "from pathlib import Path\n"
        "from random import shuffle\n\n"
        "def load_locations():\n"
        "    path = Path('data/locations.json')\n"
        "    return json.loads(path.read_text(encoding='utf-8'))['locations']\n\n"
        "def pick_round(locations, count=5):\n"
        "    pool = locations.copy()\n"
        "    shuffle(pool)\n"
        "    return pool[:count]"
    )

    ch("Игровой цикл и сцены", toc)
    pdf.code_block(
        "# src/main.py\n"
        "import pygame\n"
        "from game import Game\n"
        "from settings import WIDTH, HEIGHT, FPS, TITLE\n\n"
        "def main():\n"
        "    pygame.init()\n"
        "    screen = pygame.display.set_mode((WIDTH, HEIGHT))\n"
        "    pygame.display.set_caption(TITLE)\n"
        "    clock = pygame.time.Clock()\n"
        "    game = Game(screen)\n"
        "    running = True\n"
        "    while running:\n"
        "        dt = clock.tick(FPS) / 1000.0\n"
        "        for e in pygame.event.get():\n"
        "            if e.type == pygame.QUIT: running = False\n"
        "            game.handle_event(e)\n"
        "        game.update(dt)\n"
        "        game.draw()\n"
        "        pygame.display.flip()\n"
        "    pygame.quit()"
    )
    pdf.paragraph(
        "Game переключает сцены: MenuScene → RoundScene → ResultsScene → StatsScene. "
        "Каждая сцена знает, как рисовать UI и обрабатывать клики."
    )

    ch("Панорама: отображение локации", toc)
    pdf.paragraph(
        "В прототипе панорама — изображение JPG, загруженное через pygame.image.load. "
        "Масштабируйте его под PANORAMA_RECT, сохраняя пропорции (letterbox)."
    )
    pdf.code_block(
        "def load_panorama(filename):\n"
        "    path = ASSETS / 'panoramas' / filename\n"
        "    img = pygame.image.load(str(path)).convert()\n"
        "    return pygame.transform.smoothscale(img, (w, h))\n\n"
        "def draw_panorama(surface, image, rect):\n"
        "    surface.blit(image, rect.topleft)\n"
        "    pygame.draw.rect(surface, (255,255,255), rect, 2)"
    )
    pdf.tip(
        "Добавьте затемнённые полосы по краям и подпись «Где это?» — "
        "минималистичный UI сразу выглядит современнее."
    )

    ch("Карта мира и выбор точки", toc)
    pdf.paragraph(
        "Карта — прямоугольное изображение мира (экваториальная проекция). "
        "Клик (mx, my) внутри MAP_RECT переводится в широту и долготу."
    )
    pdf.code_block(
        "def pixel_to_latlon(mx, my, map_rect):\n"
        "    x = (mx - map_rect.x) / map_rect.w\n"
        "    y = (my - map_rect.y) / map_rect.h\n"
        "  lon = x * 360.0 - 180.0\n"
        "  lat = 90.0 - y * 180.0\n"
        "  return lat, lon\n\n"
        "def latlon_to_pixel(lat, lon, map_rect):\n"
        "    x = (lon + 180.0) / 360.0\n"
        "    y = (90.0 - lat) / 180.0\n"
        "    px = map_rect.x + x * map_rect.w\n"
        "    py = map_rect.y + y * map_rect.h\n"
        "    return int(px), int(py)"
    )
    pdf.paragraph(
        "После клика покажите маркер (красный круг). Кнопка «Угадать» фиксирует выбор."
    )
    pdf.exercise(
        "Карта",
        [
            "Нарисуйте карту мира 500×250 или используйте assets/ui/world_map.png.",
            "По клику ставьте маркер и выводите lat/lon в углу экрана.",
            "Заблокируйте повторный клик после подтверждения.",
        ],
    )

    ch("Система очков: формула Haversine", toc)
    pdf.paragraph(
        "GeoGuessr начисляет до 5000 очков. Чем меньше расстояние между догадкой и правдой, "
        "тем выше счёт. Расстояние считают по сфере Земли — формула Haversine."
    )
    pdf.code_block(
        "import math\n\n"
        "def haversine_km(lat1, lon1, lat2, lon2):\n"
        "    R = 6371.0\n"
        "    p = math.pi / 180\n"
        "    a = (math.sin((lat2-lat1)*p/2)**2 +\n"
        "         math.cos(lat1*p)*math.cos(lat2*p)*math.sin((lon2-lon1)*p/2)**2)\n"
        "    return 2 * R * math.asin(math.sqrt(a))\n\n"
        "def score_from_distance(km, max_score=5000):\n"
        "    if km <= 0.05: return max_score\n"
        "    return max(0, int(max_score * math.exp(-km / 2000)))"
    )
    pdf.paragraph(
        "Подберите делитель (2000) под желаемую сложность: меньше — щедрее очки."
    )

    ch("Экран результатов раунда", toc)
    pdf.paragraph(
        "После угадывания покажите: расстояние в км, заработанные очки, правильную точку "
        "и линию между догадкой и истиной на карте."
    )
    pdf.code_block(
        "class ResultsScene:\n"
        "    def __init__(self, game, location, guess_latlon, distance_km, score):\n"
        "        self.location = location\n"
        "        self.guess = guess_latlon\n"
        "        self.distance_km = distance_km\n"
        "        self.score = score\n\n"
        "    def draw(self, surface):\n"
        "        draw_map_with_markers(surface, self.guess, self.truth)\n"
        "        draw_text(surface, f'{self.distance_km:.0f} км · {self.score} очков')"
    )

    ch("Статистика по странам и регионам", toc)
    pdf.paragraph(
        "Вместо флагов WorldSpot показывает процент успешных угадываний. "
        "Успех — если расстояние меньше порога (например, 500 км) или очки выше 4000."
    )
    pdf.code_block(
        "# src/systems/stats.py\n"
        "class RegionStats:\n"
        "    def __init__(self):\n"
        "        self.by_country = {}  # страна -> {correct, total, avg_km}\n\n"
        "    def record(self, country, region, distance_km, score):\n"
        "        c = self.by_country.setdefault(country, {'ok':0,'n':0,'km':[]})\n"
        "        c['n'] += 1\n"
        "        c['km'].append(distance_km)\n"
        "        if distance_km < 500 or score >= 4000:\n"
        "            c['ok'] += 1\n\n"
        "    def percent(self, country):\n"
        "        c = self.by_country[country]\n"
        "        return 0 if c['n']==0 else round(100*c['ok']/c['n'])"
    )
    pdf.heading("Что показывать игроку", level=2)
    pdf.bullet("Процент угадываний по каждой стране.")
    pdf.bullet("Средняя точность (среднее расстояние в км).")
    pdf.bullet("Лучшие регионы (высокий %) и худшие (низкий %).")
    pdf.bullet("График прогресса по датам (из history.json).")
    pdf.table(
        ["Страна", "Игр", "Успех %", "Ср. км"],
        [
            ["Норвегия", "12", "67%", "420"],
            ["Япония", "8", "38%", "2100"],
            ["Бразилия", "5", "80%", "310"],
        ],
    )

    ch("Режимы: обычный и рейтинговый", toc)
    pdf.paragraph(
        "Обычный режим — без таймера, можно изучать панораму сколько угодно. "
        "Рейтинговый — лимит времени на раунд (3 минуты), бонус за скорость."
    )
    pdf.code_block(
        "class RoundScene:\n"
        "    def __init__(self, game, location, ranked=False):\n"
        "        self.ranked = ranked\n"
        "        self.time_left = ROUND_TIME_RANKED if ranked else None\n\n"
        "    def update(self, dt):\n"
        "        if self.ranked and self.time_left is not None:\n"
        "            self.time_left -= dt\n"
        "            if self.time_left <= 0:\n"
        "                self.auto_submit_worst_guess()"
    )

    ch("История игр и анализ", toc)
    pdf.code_block(
        "# savegame / history.json\n"
        "{\n"
        '  "games": [\n'
        "    {\n"
        '      "date": "2026-06-15",\n'
        '      "mode": "ranked",\n'
        '      "total_score": 18420,\n'
        '      "rounds": [\n'
        '        {"country": "Норвегия", "km": 120, "score": 4850}\n'
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    pdf.paragraph(
        "Экран «История» читает этот файл и рисует список прошлых сессий с датой, "
        "режимом и суммой очков. Клик — детали каждого раунда."
    )

    ch("Достижения и рекорды", toc)
    pdf.code_block(
        "{\n"
        '  "achievements": [\n'
        '    {"id": "first_5000", "title": "Идеально!", "desc": "5000 очков в раунде"},\n'
        '    {"id": "globe_trotter", "title": "Глобус", "desc": "10 разных стран"},\n'
        '    {"id": "europe_master", "title": "Европа", "desc": "80% в Европе"}\n'
        "  ]\n"
        "}"
    )
    pdf.paragraph(
        "После каждого раунда проверяйте условия и разблокируйте достижения. "
        "Рекорды: лучший суммарный счёт за 5 раундов, минимальное среднее расстояние."
    )

    ch("Минималистичный интерфейс", toc)
    pdf.bullet("Фон: тёмно-серый #1a1a2e, текст белый, акцент зелёный #1a6b4a.")
    pdf.bullet("Шрифт: системный sans-serif, крупные заголовки, мало декора.")
    pdf.bullet("Кнопки: прямоугольники с тонкой обводкой, hover — светлее.")
    pdf.bullet("Никаких лишних рамок — панорама и карта занимают 90% экрана.")
    pdf.code_block(
        "COLORS = {\n"
        "    'bg': (26, 26, 46),\n"
        "    'accent': (26, 107, 74),\n"
        "    'text': (240, 240, 245),\n"
        "    'muted': (160, 160, 180),\n"
        "    'marker_guess': (239, 68, 68),\n"
        "    'marker_truth': (34, 197, 94),\n"
        "}"
    )

    ch("Полный цикл раунда в коде", toc)
    pdf.numbered_item(1, "MenuScene: выбор «Играть» / «Рейтинг» / «Статистика».")
    pdf.numbered_item(2, "RoundScene: загрузка location, показ панорамы и карты.")
    pdf.numbered_item(3, "Игрок кликает карту → нажимает «Угадать».")
    pdf.numbered_item(4, "scoring.haversine_km + score_from_distance.")
    pdf.numbered_item(5, "stats.record(country, region, km, score).")
    pdf.numbered_item(6, "ResultsScene → кнопка «Далее» или итог серии.")
    pdf.tip("В шаблоне WorldSpot этот цикл уже работает — запустите python -m src.main.")

    ch("Продвинутый уровень: API панорам", toc)
    pdf.paragraph(
        "Для настоящих уличных панорам используйте Mapillary API (бесплатный tier) "
        "или Google Street View Static API. Запрос по lat/lon возвращает изображение."
    )
    pdf.code_block(
        "# Псевдокод Mapillary\n"
        "url = f'https://graph.mapillary.com/images?access_token=TOKEN'\n"
        "      f'&fields=id&closeto={lon},{lat}'\n"
        "# Скачать thumb URL и кэшировать в assets/panoramas/"
    )
    pdf.warning("Храните API-ключи в .env, не коммитьте в git.")

    ch("Git и публикация на GitHub", toc)
    pdf.code_block(
        "git init\n"
        "git add .\n"
        "git commit -m 'WorldSpot: geographic guessing game prototype'\n"
        "git remote add origin https://github.com/USER/WorldSpot.git\n"
        "git push -u origin main"
    )
    pdf.code_block(
        "# .gitignore\n"
        ".venv/\n"
        "__pycache__/\n"
        ".env\n"
        "savegame.json\n"
        "history.json"
    )

    ch("Дорожная карта развития", toc)
    pdf.table(
        ["Неделя", "Задача", "Результат"],
        [
            ["1", "Окно + панорама + карта", "Клик по карте"],
            ["2", "Haversine + очки", "Счёт раунда"],
            ["3", "Статистика %", "Таблица стран"],
            ["4", "Режимы + таймер", "Рейтинг"],
            ["5", "История + достижения", "Прогресс"],
            ["6", "GitHub + UI полировка", "Релиз"],
        ],
    )

    ch("Приложение: управление в шаблоне", toc)
    pdf.table(
        ["Действие", "Управление"],
        [
            ["Клик по карте", "ЛКМ"],
            ["Подтвердить угадывание", "Enter / Пробел"],
            ["Меню", "Esc"],
            ["Следующий раунд", "N"],
        ],
    )
    pdf.bullet("Документация pygame: https://www.pygame.org/docs/")
    pdf.bullet("GeoGuessr для вдохновения: https://www.geoguessr.com/")
    pdf.bullet("Mapillary API: https://www.mapillary.com/developer")
    pdf.bullet("OpenStreetMap: https://www.openstreetmap.org/")

    ch("Заключение", toc)
    pdf.paragraph(
        "WorldSpot — это исследование мира через код. Вы научились строить панорамы, карту, "
        "географический скоринг и аналитику по странам. Развивайте географическую интуицию "
        "в игре и делитесь проектом с друзьями на GitHub."
    )
    pdf.paragraph(
        "Запустите шаблон, пройдите 5 раундов, откройте статистику — и добавьте свою первую "
        "локацию в data/locations.json. Удачи в разработке!"
    )
