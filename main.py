import os
import time
import requests
from dotenv import load_dotenv
from amazon_paapi import AmazonApi

# ✅ Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
PARTNER_TAG = os.getenv("AMAZON_TAG")
LOCALE = "es"

# ✅ Instanciar Amazon API
amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, PARTNER_TAG, LOCALE)

# ✅ Keywords
SUPLEMENTOS_KEYWORDS = [
    "creatina", "proteína", "whey", "glutamina", "bcaa", "preentreno",
    "quemagrasas", "colágeno", "shaker", "suplemento"
]
MATERIAL_KEYWORDS = [
    "bandas", "rodillo", "kettlebell", "anillas", "cuerda", "trx", "rueda abdominal",
    "esterilla", "reloj deportivo", "chaleco lastrado", "zapatillas", "ropa deportiva",
    "leggins", "pesas", "guantes", "cinta de correr", "spinning", "crossfit"
]

# ✅ Clasificación
def clasificar_producto(nombre):
    nombre = nombre.lower()
    for kw in SUPLEMENTOS_KEYWORDS:
        if kw in nombre:
            return "suplemento"
    for kw in MATERIAL_KEYWORDS:
        if kw in nombre:
            return "material"
    return "otro"

# ✅ Generador de copy
def generar_texto(producto):
    titulo = producto.title or "Producto fitness"
    precio = producto.prices.price or "Sin precio"
    rating = f"{producto.reviews.rating}⭐" if producto.reviews else "Sin valoraciones"
    url = producto.url or ""

    tipo = clasificar_producto(titulo)

    if tipo == "suplemento":
        hashtags = "#NutriciónDeportiva #SuplementosFitness #GymLife"
        copy = f"🔥 {titulo}\nPotencia tus entrenos y tu recuperación 💪\n⭐ {rating}\n💰 {precio}\n🔗 {url}\n{hashtags}"
    elif tipo == "material":
        hashtags = "#EntrenaConEstilo #FitnessGear #CholloFitness"
        copy = f"🏋️ {titulo}\nIdeal para tus rutinas diarias 💥\n⭐ {rating}\n💰 {precio}\n🔗 {url}\n{hashtags}"
    else:
        copy = f"🛒 {titulo}\n⭐ {rating}\n💰 {precio}\n🔗 {url}\n#CholloFitness"

    return copy

# ✅ Enviar a Telegram
def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"})

# ✅ Lógica principal
def iniciar_bot():
    productos = amazon.search_items(keywords="fitness", search_index="All", item_count=10)
    for item in productos.items:
        if item.reviews and float(item.reviews.rating) >= 4.0:
            mensaje = generar_texto(item)
            enviar_telegram(mensaje)
            time.sleep(5)

if __name__ == "__main__":
    iniciar_bot()
