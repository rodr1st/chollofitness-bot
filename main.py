import os
import logging
from amazon.paapi import AmazonAPI
from telegram import Bot
from telegram.error import TelegramError

# Configuración de entorno
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOC_TAG = os.getenv("AMAZON_ASSOC_TAG")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, "ES")
bot = Bot(token=TELEGRAM_TOKEN)

# Categorías de palabras clave
SUPLEMENTACION = [
    "creatina", "proteína", "glutamina", "bcaa", "preentreno", "multivitamínicos",
    "omega 3", "colágeno", "quemagrasas"
]

EQUIPAMIENTO = [
    "pesas", "bandas de resistencia", "mancuernas", "banco de musculación",
    "crossfit", "ropa gym", "under armour", "adidas training", "nike gym",
    "accesorios gimnasio", "rodillo abdominal", "kettlebell" , "hoka" , 
    "rodilleras" , "cinturon musculación" , "electroestimulador" , "compex",
]

# Función para buscar productos por keyword
def buscar_productos(keyword):
    try:
        result = amazon.search_items(
            keywords=keyword,
            item_count=3,
            search_index="All"
        )
        return result.items if result and result.items else []
    except Exception as e:
        logging.error(f"Error al buscar productos con '{keyword}': {e}")
        return []

# Calcula % de descuento si hay precio anterior
def calcular_descuento(oferta):
    try:
        actual = oferta.price.amount
        antes = oferta.savings.amount + actual if oferta.savings else None
        if antes and antes > actual:
            descuento = round((antes - actual) / antes * 100)
            return descuento
    except:
        return 0
    return 0

# Formatear producto
def formatear_producto(item, categoria):
    try:
        title = item.item_info.title.display_value
        url = item.detail_page_url
        image = item.images.primary.large.url
        stars = item.item_info.customer_reviews.star_rating.display_value if item.item_info.customer_reviews else "N/A"
        offer = item.offers.listings[0]
        price = offer.price.display_amount
        descuento = calcular_descuento(offer)

        if descuento < 30:
            return None, None

        caption = (
            f"🔥 *[{categoria.upper()}]*\n"
            f"{title}\n"
            f"⭐ {stars} – {price}\n"
            f"📉 Descuento: {descuento}%\n"
            f"🔗 {url}"
        )
        return caption, image
    except Exception as e:
        logging.error(f"Error al formatear producto: {e}")
        return None, None

# Publicar en Telegram
def publicar_en_telegram(texto, imagen_url):
    try:
        bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=imagen_url, caption=texto, parse_mode="Markdown")
    except TelegramError as e:
        logging.error(f"Error enviando a Telegram: {e}")

# Main
def main():
    for keyword in SUPLEMENTACION:
        productos = buscar_productos(keyword)
        for item in productos:
            texto, imagen = formatear_producto(item, "suplementación")
            if texto and imagen:
                publicar_en_telegram(texto, imagen)

    for keyword in EQUIPAMIENTO:
        productos = buscar_productos(keyword)
        for item in productos:
            texto, imagen = formatear_producto(item, "equipamiento")
            if texto and imagen:
                publicar_en_telegram(texto, imagen)

if __name__ == "__main__":
    main()
