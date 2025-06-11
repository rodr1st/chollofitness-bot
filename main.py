import os
import logging
import time
import schedule
from dotenv import load_dotenv
from python_amazon_paapi import AmazonAPI
from telegram import Bot
from telegram.error import TelegramError

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de entorno
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
AMAZON_ASSOC_TAG = os.getenv("AMAZON_ASSOC_TAG")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Validar variables de entorno
required_vars = [AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
if not all(required_vars):
    logger.error("Faltan variables de entorno requeridas")
    exit(1)

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
    "accesorios gimnasio", "rodillo abdominal", "kettlebell", "hoka", 
    "rodilleras", "cinturon musculación", "electroestimulador", "compex",
]

# Función para buscar productos por keyword
def buscar_productos(keyword):
    try:
        logger.info(f"Buscando productos para: {keyword}")
        result = amazon.search_items(
            keywords=keyword,
            item_count=3,
            search_index="All"
        )
        return result.items if result and result.items else []
    except Exception as e:
        logger.error(f"Error al buscar productos con '{keyword}': {e}")
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
        image = item.images.primary.large.url if item.images and item.images.primary else None
        stars = item.item_info.customer_reviews.star_rating.display_value if item.item_info.customer_reviews else "N/A"
        offer = item.offers.listings[0] if item.offers and item.offers.listings else None
        
        if not offer:
            return None, None
            
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
        logger.error(f"Error al formatear producto: {e}")
        return None, None

# Publicar en Telegram
def publicar_en_telegram(texto, imagen_url):
    try:
        if imagen_url:
            bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=imagen_url, caption=texto, parse_mode="Markdown")
        else:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto, parse_mode="Markdown")
        logger.info("Mensaje enviado exitosamente")
        time.sleep(2)  # Evitar spam
    except TelegramError as e:
        logger.error(f"Error enviando a Telegram: {e}")

# Función principal de búsqueda
def buscar_ofertas():
    logger.info("Iniciando búsqueda de ofertas...")
    ofertas_encontradas = 0
    
    # Buscar suplementación
    for keyword in SUPLEMENTACION:
        productos = buscar_productos(keyword)
        for item in productos:
            texto, imagen = formatear_producto(item, "suplementación")
            if texto and imagen:
                publicar_en_telegram(texto, imagen)
                ofertas_encontradas += 1
    
    # Buscar equipamiento
    for keyword in EQUIPAMIENTO:
        productos = buscar_productos(keyword)
        for item in productos:
            texto, imagen = formatear_producto(item, "equipamiento")
            if texto and imagen:
                publicar_en_telegram(texto, imagen)
                ofertas_encontradas += 1
    
    logger.info(f"Búsqueda completada. Ofertas encontradas: {ofertas_encontradas}")

# Main con programación
def main():
    logger.info("🚀 Bot de chollos iniciado")
    
    # Programar ejecuciones
    schedule.every(4).hours.do(buscar_ofertas)
    
    # Ejecutar una vez al inicio
    buscar_ofertas()
    
    # Mantener el bot corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto

if __name__ == "__main__":
    main()
