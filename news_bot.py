import asyncio
import schedule
import time
from datetime import datetime
import pytz
import requests
from telegram import Bot

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = "8387772390:AAHuxuKoiZ8wlLTsPomGnL0zLxk_X7nMI5o"
CHAT_ID = "8043528126"
ANTHROPIC_API_KEY = "VOTRE_CLE_ANTHROPIC_ICI"  # Optionnel si vous voulez utiliser Claude

# Fuseau horaire Martinique
MARTINIQUE_TZ = pytz.timezone('America/Martinique')

# ========== FONCTIONS ==========

def get_news_from_web():
    """Récupère les actualités du jour via une API d'actualités"""
    # Option 1: NewsAPI (gratuit jusqu'à 100 requêtes/jour)
    # Inscrivez-vous sur https://newsapi.org/ pour obtenir une clé
    NEWS_API_KEY = "a24114a715eb420faf44a0b89d055de4"  # À remplacer

    url = f"https://newsapi.org/v2/top-headlines?country=fr&pageSize=10&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'ok':
            articles = data['articles']
            news_text = "📰 **Actualités du jour**\n\n"

            for i, article in enumerate(articles[:8], 1):
                title = article['title']
                source = article['source']['name']
                news_text += f"{i}. **{title}**\n   _{source}_\n\n"

            return news_text
        else:
            return "Impossible de récupérer les actualités pour le moment."
    except Exception as e:
        return f"Erreur lors de la récupération des news: {str(e)}"

def generate_summary_with_claude(news_text):
    """Utilise Claude pour créer un résumé concis (optionnel)"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"Voici les titres d'actualités du jour. Crée un résumé concis et structuré en français, lisible en 5 minutes maximum:\n\n{news_text}"
                }]
            }
        )

        data = response.json()
        return data['content'][0]['text']
    except:
        return news_text  # Retourne les news brutes si Claude échoue

async def send_daily_message():
    """Envoie le message quotidien via Telegram"""
    bot = Bot(token=TELEGRAM_TOKEN)

    # Récupère les actualités
    news = get_news_from_web()

    # Option: utiliser Claude pour améliorer le résumé
    # summary = generate_summary_with_claude(news)
    summary = news  # Sans Claude

    # Ajoute la date
    now = datetime.now(MARTINIQUE_TZ)
    message = f"🌅 **Bonjour !**\n\n📅 {now.strftime('%A %d %B %Y')}\n\n{summary}"

    # Envoie le message
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode='Markdown'
    )
    print(f"Message envoyé à {now.strftime('%H:%M')}")

def job():
    """Wrapper pour exécuter la fonction async"""
    asyncio.run(send_daily_message())

# ========== PLANIFICATION ==========

# ===== TEST IMMÉDIAT =====
print("🧪 Test immédiat : envoi du message maintenant...")
job()
print("✅ Message envoyé ! Vérifiez Telegram.\n")
# ===== FIN DU TEST =====

# Programme l'envoi à 6h30 heure Martinique
schedule.every().day.at("06:30").do(job)

print("🤖 Bot démarré ! En attente de 6h30 (heure Martinique)...")
print(f"Heure actuelle: {datetime.now(MARTINIQUE_TZ).strftime('%H:%M')}")

# Boucle principale
while True:
    schedule.run_pending()
    time.sleep(60)  # Vérifie toutes les minutes
