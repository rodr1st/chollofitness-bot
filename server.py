from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot de CholloFitness corriendo correctamente."
    from main import iniciar_bot
iniciar_bot()
