# WorldSpot — GeoGuessr в браузере

Бесплатная игра «угадай место по панораме». Работает на сайте — **React + Leaflet + Photo Sphere Viewer**, без API-ключей.

## Быстрый старт (веб)

```bash
# 1. Скачать фото локаций (один раз, нужен интернет)
python3 scripts/download_assets.py

# 2. Запустить веб-версию
cd web
npm install
npm run dev
```

Откройте http://localhost:5173

## Сборка для сайта

```bash
cd web
npm run build
```

Папка `web/dist/` — загрузите на любой хостинг (Vercel, Netlify, nginx).

## Что внутри

| Компонент | Технология |
|-----------|------------|
| Карта | Leaflet + OpenStreetMap (стабильно в браузере) |
| Панорама 360° | Photo Sphere Viewer |
| Обычные фото | Плавный pan/zoom |
| Очки | Формула GeoGuessr |
| Языки | ru / en / kk |

## Десктоп (старая версия)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Управление

- **Панорама** — тянуть мышью, `+` / `−` справа
- **Карта** — клик = метка, `⤢` = развернуть
- **Угадать** — зелёная кнопка внизу
