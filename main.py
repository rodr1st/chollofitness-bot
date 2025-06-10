import os
import json
import threading
import time
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Opcional

bot = Bot(token=TELEGRAM_TOKEN)

def calcular_descuento(precio_original, precio_actual):
    try:
        descuento = round((float(precio_original) - float(precio_actual)) / float(precio_original) * 100)
        return f"⚡ -{descuento}% de descuento"
    except:
        return ""

def publicar_producto(producto):
    nombre = producto.get("nombre", "Producto fitness")
    precio = producto.get("precio_actual", "¿?")
    estrellas = producto.get("valoracion", "¿?")
    enlace = producto.get("enlace", "")
    descuento = calcular_descuento(producto.get("precio_original", precio), precio)
    beneficio = producto.get("beneficio", "¡Ideal para tus entrenamientos!")

    mensaje = f"""🔥 ¡OFERTÓN FITNESS! 🔥
🏷️ Producto: {nombre}
⭐ Valoración: {estrellas} | 💰 Precio: {precio}
{descuento}
✅ {beneficio}

🛒 Consíguelo aquí 👉 {enlace}

#Fitness #Amazon #CholloDelDía #EntrenaEnCasa
"""
    bot.send_message(chat_id=CHAT_ID, text=mensaje)

def cargar_productos():
    with open("productos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def loop_publicaciones():
    productos = cargar_productos()
    while True:
        for producto in productos:
            publicar_producto(producto)
            time.sleep(3600)  # Publica cada hora

if __name__ == "__main__":
    t = threading.Thread(target=loop_publicaciones)
    t.start()
def iniciar bot():
    t=threading.Thread(target=loop_publicaciones)
    t.start()
