import telebot
import random
import time
import requests
import datetime
import requests
import threading
import json
import os

TOKEN = os.getenv("TOKEN")  # Replace with your bot token
bot = telebot.TeleBot(TOKEN)

warnings = {}
afk_users = {}
group_rules = "No spamming, be respectful!"
custom_welcome = "Welcome to the group! Follow the rules."

### 🚀 ADMIN COMMANDS ###



def get_zodiac_sign(day, month):
    zodiac_signs = [
        ("Capricorn", (1, 19)), ("Aquarius", (2, 18)), ("Pisces", (3, 20)),
        ("Aries", (4, 19)), ("Taurus", (5, 20)), ("Gemini", (6, 20)),
        ("Cancer", (7, 22)), ("Leo", (8, 22)), ("Virgo", (9, 22)),
        ("Libra", (10, 22)), ("Scorpio", (11, 21)), ("Sagittarius", (12, 21)),
        ("Capricorn", (12, 31))
    ]
    
    for sign, (m, d) in zodiac_signs:
        if (month == m and day <= d) or (month == m - 1 and day > d):
            return sign
    return "Unknown"

@bot.message_handler(commands=['horoscope'])
def horoscope_handler(message):
    try:
        # Extract date of birth from the message
        text = message.text.split()
        if len(text) != 3:
            bot.send_message(message.chat.id, "Usage: /horoscope DD MM (e.g. /horoscope 15 08)")
            return
        
        day, month = int(text[1]), int(text[2])
        if day < 1 or day > 31 or month < 1 or month > 12:
            bot.send_message(message.chat.id, "Invalid date! Please enter a valid day and month.")
            return
        
        zodiac_sign = get_zodiac_sign(day, month)
        bot.send_message(message.chat.id, f"Your Zodiac Sign is: {zodiac_sign}")

    except Exception as e:
        bot.send_message(message.chat.id, "❌ An error occurred. Please try again.")


import requests

@bot.message_handler(commands=['wiki'])
def wiki_search(message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            bot.reply_to(message, "❌ Please provide a topic to search on Wikipedia.\nExample: /wiki Python")
            return

        topic = args[1]
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown")
            extract = data.get("extract", "No summary available.")
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "No URL available.")

            bot.reply_to(message, f"📖 {title}\n\n{extract}\n{page_url}", disable_web_page_preview=True)
        else:
            bot.reply_to(message, "❌ No Wikipedia page found for that topic.")

    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")


@bot.message_handler(commands=['shorten'])
def shorten_url(message):
    try:
        args = message.text.split(" ", 1)  # Extract URL from the message
        if len(args) < 2:
            bot.reply_to(message, "❌ Please provide a URL to shorten.\nExample: /shorten https://example.com")
            return
        
        long_url = args[1]
        api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
        
        response = requests.get(api_url)
        if response.status_code == 200:
            short_url = response.text
            bot.reply_to(message, f"✅ Shortened URL: {short_url}", disable_web_page_preview=True)
        else:
            bot.reply_to(message, "❌ Failed to shorten the URL. Please try again later.")
    
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")


@bot.message_handler(commands=['qr'])
def generate_qr(message):
    text = message.text.split(" ", 1)
    if len(text) < 2:
        bot.send_message(message.chat.id, "❌ Please provide text or a URL to generate a QR code.\nExample: `/qr https://example.com`", parse_mode="Markdown")
        return

    qr_text = text[1]
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_text}"

    bot.send_photo(message.chat.id, qr_url, caption="✅ Here is your QR code!")


import telebot
import requests
from datetime import datetime
import pytz  # For handling time zones

# --- Weatherbit API Key and Base URL ---
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY")
BASE_URL_WEATHERBIT_CURRENT = 'https://api.weatherbit.io/v2.0/current?'

def get_weatherbit(city):
    params = {
        'city': city,
        'key': WEATHERBIT_API_KEY,
        'units': 'M'
    }
    try:
        response = requests.get(BASE_URL_WEATHERBIT_CURRENT, params=params)
        response.raise_for_status()
        data = response.json()
        if data and 'data' in data and len(data['data']) > 0:
            weather_data = data['data'][0]
            temperature = weather_data['temp']
            feels_like = weather_data['app_temp']
            humidity = weather_data['rh']
            description = weather_data['weather']['description']
            wind_speed = weather_data['wind_spd']
            wind_direction_deg = weather_data['wind_dir']
            pressure = weather_data['slp']
            visibility = weather_data['vis']
            uv_index = weather_data['uv']
            sunrise_ts = weather_data.get('sunrise_ts')  # Use .get() to avoid errors if not present
            sunset_ts = weather_data.get('sunset_ts')

            # Convert wind direction degrees to cardinal direction (optional)
            def deg_to_compass(deg):
                val = int((deg/22.5)+.5)
                arr = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
                return arr[(val % 16)]

            wind_direction = deg_to_compass(wind_direction_deg)

            # Format sunrise and sunset times (adjusting for India's timezone)
            india_tz = pytz.timezone('Asia/Kolkata')
            if sunrise_ts:
                sunrise_time = datetime.fromtimestamp(sunrise_ts, tz=pytz.utc).astimezone(india_tz).strftime('%I:%M %p')
            else:
                sunrise_time = "N/A"

            if sunset_ts:
                sunset_time = datetime.fromtimestamp(sunset_ts, tz=pytz.utc).astimezone(india_tz).strftime('%I:%M %p')
            else:
                sunset_time = "N/A"

            weather_report = f"Weather in {city}:\n"
            weather_report += f"Temperature: {temperature}°C (Feels like: {feels_like}°C)\n"
            weather_report += f"Description: {description.capitalize()}\n"
            weather_report += f"Humidity: {humidity}%\n"
            weather_report += f"Wind: {wind_speed} m/s from {wind_direction}\n"
            weather_report += f"Pressure: {pressure} hPa\n"
            weather_report += f"Visibility: {visibility} km\n"
            weather_report += f"UV Index: {uv_index}\n"
            weather_report += f"Sunrise: {sunrise_time} IST\n"
            weather_report += f"Sunset: {sunset_time} IST"
            return weather_report
        else:
            return "City not found or more detailed weather data unavailable."
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "Failed to get more detailed weather data."

@bot.message_handler(commands=['weather'])
def send_weatherbit(message):
    try:
        city = message.text.split()[1]
        weather_info = get_weatherbit(city)
        bot.reply_to(message, weather_info)
    except IndexError:
        bot.reply_to(message, "please specify a city")


import telebot
import json
import os


WARNINGS_FILE = "warnings.json"

# Load warnings from JSON file
def load_warnings():
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, "r") as file:
            return json.load(file)
    return {}

# Save warnings to JSON file
def save_warnings(warnings):
    with open(WARNINGS_FILE, "w") as file:
        json.dump(warnings, file, indent=4)

# Initialize warnings from file
warnings = load_warnings()

# Function to check if a user is an admin
def is_admin(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_admins = bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in chat_admins)

# Command to warn a user (only for admins)
@bot.message_handler(commands=["warn"])
def warn_user(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ You must be an admin to use this command!")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to a user’s message to warn them!")
        return

    warned_user = str(message.reply_to_message.from_user.id)
    chat_id = str(message.chat.id)

    if chat_id not in warnings:
        warnings[chat_id] = {}

    if warned_user not in warnings[chat_id]:
        warnings[chat_id][warned_user] = 0

    warnings[chat_id][warned_user] += 1
    warn_count = warnings[chat_id][warned_user]

    save_warnings(warnings)

    bot.reply_to(message, f"⚠️ {message.reply_to_message.from_user.first_name} has been warned! ({warn_count}/3)")

    if warn_count >= 3:
        bot.kick_chat_member(int(chat_id), int(warned_user))
        bot.send_message(chat_id, f"🚨 {message.reply_to_message.from_user.first_name} has been banned for exceeding 3 warnings!")
        del warnings[chat_id][warned_user]
        save_warnings(warnings)

# Command to clear warnings (only for admins)
@bot.message_handler(commands=["clearwarn"])
def clear_warn(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ You must be an admin to use this command!")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to a user's message to clear their warnings!")
        return

    warned_user = str(message.reply_to_message.from_user.id)
    chat_id = str(message.chat.id)

    if chat_id in warnings and warned_user in warnings[chat_id]:
        del warnings[chat_id][warned_user]
        save_warnings(warnings)
        bot.reply_to(message, f"✅ Warnings for {message.reply_to_message.from_user.first_name} have been cleared!")
    else:
        bot.reply_to(message, f"ℹ️ {message.reply_to_message.from_user.first_name} has no warnings.")




@bot.message_handler(commands=['allpfp'])
def send_all_pfp(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split(maxsplit=1)
        if len(args) == 2:
            try:
                user = bot.get_chat(args[1])  # Fetch user details
                user_id = user.id
            except Exception as e:
                bot.reply_to(message, f"❌ Error: {e}")
                return
        else:
            user_id = message.from_user.id  # Default to sender
    
    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count == 0:
            bot.reply_to(message, "❌ No profile pictures found!")
            return
        
        for photo in photos.photos:
            bot.send_photo(message.chat.id, photo[-1].file_id)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")




bad_words = {"fuck", "bakchodi", "bitch", "bastard", "asshole", "shit", "dick", "chutiya", "bhosdike", "gaand", "madarchod", "behenchod", "haraamkhor", "teri maa ki", "teri bhen ki", "gandu", "randi", "chut", "bc", "mc", "bisi", "iski maa ka", "iski behen ka", "iski ma ka", "chodu", "chod", "chaatu", "raand", "rand"}  # Replace with actual bad words

def is_bad_word(message):
    words = message.lower().split()
    
    # Special Exception for "Ikshit"
    if "ikshit" in words:
        return False  # Allows "Ikshit" even if other words are blocked
    
    for word in words:
        if word in bad_words:
            return True
    return False

@bot.message_handler(func=lambda message: is_bad_word(message.text))
def filter_bad_words(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "⚠️ Please avoid using inappropriate language.")

import yt_dlp
from telebot.types import Message

# Function to fetch song link
def get_song_link(song_name):
    search_query = f"ytsearch:{song_name}"
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)['entries'][0]
            return info['webpage_url']
        except Exception as e:
            return None

# Handler for /song command
@bot.message_handler(commands=['song'])
def send_song_link(message: Message):
    query = message.text.replace("/song", "").strip()
    
    if not query:
        bot.reply_to(message, "Please provide a song name! Example: `/song Despacito`", parse_mode="Markdown")
        return

    song_link = get_song_link(query)

    if song_link:
        bot.reply_to(message, f"Here's your song: [Click Here]({song_link})", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Sorry, I couldn't find that song. Try another one!")

import time
start_time = time.time()

@bot.message_handler(commands=['uptime'])
def uptime(message):
    uptime_seconds = int(time.time() - start_time)
    bot.reply_to(message, f"⏱️ Uptime: {uptime_seconds} seconds")

@bot.message_handler(commands=['commands'])
def send_commands(message):
    commands_list = """
🛠️ *Bot Commands*:

**General:**
- `/ping` - Check bot status
- `/about` - Bot info
- `/time` - Show server time
- `/uptime` - Bot uptime
- `/commands` - Show all commands

**Admin:**
- `/warn` - Warn user
- `/clearwarn` - Clear warnings
- `/ban` - Ban user
- `/tagall` - Tag all admins

**AFK:**
- `/afk` - Set AFK with reason

**Fun:**
- `/roll` - Roll dice
- `/coinflip` - Flip coin
- `/joke` - Random joke
- `/fact` - Random fact
- `/love` - Love calculator
- `/dog` - Random dog
- `/cat` - Random cat
- `/askme` - Ask if confused
- `/hug` - Try it
- `/rizz` - Find your flirting skill
- `/meme` - How funny you are
- `/best` - Try it
- `/roast` - To roast someone
- `/simp` - Try it
- `/quote` - Get motivated
- `/reverse` - Try it
- `/calculate` - If stuck
- `/mock` - Try it
- `/rate` - Rate things
- `/wouldyourather` - Try it
- `/rps` - Rock paper scissors
- `/trivia` - Ask a random trivia
- `/mathquiz` - Try math quiz
- `/scramble` - Play
- `/gif` - Get a random gif
- `/define` - Get word definition
- `/predict` - Predict future
- `/guess` - Play with numbers

**Utility:**
- `/spamm <times> <message>` - Spam a message (limit: 10)
- `/whois` - Get info about a user
- `/avatar` - Get a user profile photo
- `/id` - Get your Telegram ID
- `/getid <username>` - Get ID by username
- '/qr <text>' - Get qr code of text
- '/shorten <url>' - to shorten url
- '/wiki <text>' - to get wiki
- '/horoscope DD MM' - to get zodiac
- '/ai <text>' - command in development
⚡ *More updates coming soon!* ⚡
"""
    bot.send_message(message.chat.id, commands_list, parse_mode="Markdown")


@bot.message_handler(commands=['best'])
def best_person(message):
    members = [message.chat.id]
    bot.reply_to(message, f"🏆 {random.choice(members)} is the best!")

# /id Command - Get user ID
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: <code>{message.from_user.id}</code>")

# /whois Command - Get user info
@bot.message_handler(commands=['whois'])
def whois(message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    info = f"👤 User Info\n\n"
    info += f"🔹 Name {user.first_name} {user.last_name or ''}\n"
    info += f"🔹 Username: @{user.username if user.username else 'None'}\n"
    info += f"🔹 User ID: <code>{user.id}</code>\n"
    info += f"🔹 Is Bot: {'Yes' if user.is_bot else 'No'}"
    bot.reply_to(message, info)

# /avatar Command - Get user's profile picture
@bot.message_handler(commands=['avatar'])
def get_avatar(message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    photos = bot.get_user_profile_photos(user.id)

    if photos.total_count > 0:
        bot.send_photo(message.chat.id, photos.photos[0][0].file_id)
    else:
        bot.reply_to(message, "❌ No profile picture found.")

# /getid Command - Get ID from username
@bot.message_handler(commands=['getid'])
def get_id_from_username(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "⚠️ Please provide a username. Example: /getid @username")
        return
    
    username = message.text.split()[1].strip("@")  # Remove '@' if included
    try:
        user = bot.get_chat(username)
        bot.reply_to(message, f"🆔 User ID of @{username}: <code>{user.id}</code>")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

import random

# /mock command (Alternates uppercase/lowercase)
@bot.message_handler(commands=['mock'])
def mock_message(message):
    if message.reply_to_message:
        text = message.reply_to_message.text
        mocked_text = ''.join(random.choice([c.upper(), c.lower()]) for c in text)
        bot.send_message(message.chat.id, mocked_text)
    else:
        bot.send_message(message.chat.id, "Reply to a message to mock it!")

# /wouldyourather command (Random Would You Rather question)
would_you_rather_questions = [
    "Would you rather have the ability to fly or be invisible?",
    "Would you rather be rich but alone or poor but have many friends?",
    "Would you rather live in space or under the ocean?",
    "Would you rather never eat your favorite food again or only eat that forever?",
    "Would you rather always have to sing instead of speaking or dance everywhere you go?"
]

@bot.message_handler(commands=['wouldyourather'])
def would_you_rather(message):
    bot.send_message(message.chat.id, random.choice(would_you_rather_questions))

# /rate command (Rates something from 1 to 10)
@bot.message_handler(commands=['rate'])
def rate_something(message):
    if len(message.text.split()) > 1:
        thing = message.text.split(maxsplit=1)[1]
        rating = random.randint(1, 10)
        bot.send_message(message.chat.id, f"I rate {thing} a {rating}/10! 🎯")
    else:
        bot.send_message(message.chat.id, "Tell me what to rate! Example: /rate pizza")

import random  

# Trivia Game  
TRIVIA_QUESTIONS = {  
    "What is the capital of France?": "Paris",  
    "Who wrote 'To Kill a Mockingbird'?": "Harper Lee",  
    "What is the square root of 64?": "8",  
    "Which planet is known as the Red Planet?": "Mars",  
}  

import random

@bot.message_handler(commands=['rps'])
def rock_paper_scissors(message):
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    
    bot.reply_to(message, "🤖 Choose: Rock, Paper, or Scissors!")
    
    @bot.message_handler(func=lambda msg: msg.text.lower() in choices)
    def check_rps(msg):
        user_choice = msg.text.lower()
        
        if user_choice == bot_choice:
            result = "It's a tie! 😶"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            result = f"You win! 🎉 (I chose {bot_choice})"
        else:
            result = f"I win! 😈 (I chose {bot_choice})"
        
        bot.reply_to(msg, result)

import random

quiz_data = {}

@bot.message_handler(commands=['trivia'])
def trivia_game(message):
    global quiz_data
    questions = {
        "What is the capital of India?": "New Delhi",
        "Who wrote 'Hamlet'?": "Shakespeare",
        "What is 387+1882?": "2269",
        "What is the chemical symbol for water?": "H2O",
    }
    
    question, answer = random.choice(list(questions.items()))
    quiz_data[message.chat.id] = answer.lower()  # Store answer
    
    bot.reply_to(message, f"🧠 Trivia Time!\n\n{question}\n\nReply with your answer.")

@bot.message_handler(commands=['mathquiz'])
def math_quiz(message):
    global quiz_data
    num1, num2 = random.randint(10, 100), random.randint(11, 40)
    question = f"{num1} × {num2} = ?"
    answer = str(num1 * num2)
    
    quiz_data[message.chat.id] = answer  # Store answer
    bot.reply_to(message, f"🤓 Solve this: {question}")

import random

scramble_answers = {}

@bot.message_handler(commands=["scramble"])
def scramble_game(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Please reply to a message to play the scramble game!")
        return

    words = [
        "python", "telegram", "coding", "scramble", "bot", "developer", "algorithm",
        "variable", "function", "keyboard", "database", "software", "hardware",
        "internet", "programming", "debugging", "compiler", "syntax", "terminal",
        "processor", "encryption", "loop", "recursion", "framework", "frontend",
        "backend", "server", "client", "authentication", "deployment", "script",
        "library", "module", "iteration", "hashing", "protocol", "command",
        "execution", "bitwise", "boolean", "cybersecurity", "malware"
    ]

    word = random.choice(words)
    scrambled_word = "".join(random.sample(word, len(word)))

    scramble_answers[message.chat.id] = word  # Store the correct word

    bot.reply_to(message.reply_to_message, f"🔀 Unscramble this: **{scrambled_word}**\n\nReply with your answer!")

@bot.message_handler(func=lambda message: message.chat.id in scramble_answers)
def check_scramble_answer(message):
    correct_answer = scramble_answers.get(message.chat.id, "").lower()
    user_answer = message.text.strip().lower()

    if user_answer == correct_answer:
        bot.reply_to(message, "✅ Correct! 🎉")
        del scramble_answers[message.chat.id]  # Remove after correct answer
    else:
        bot.reply_to(message, "❌ Wrong! Try again!")

# Number Guessing Game  
guessing_game = {}  

@bot.message_handler(commands=['guess'])  
def start_guessing_game(message):  
    guessing_game[message.chat.id] = random.randint(1, 100)  
    bot.send_message(message.chat.id, "I've picked a number between 1 and 100. Reply with your guess!")  

@bot.message_handler(func=lambda msg: msg.chat.id in guessing_game and msg.reply_to_message is not None)  
def check_guess(message):  
    try:  
        guess = int(message.text)  
        target = guessing_game[message.chat.id]  
        if guess < target:  
            bot.send_message(message.chat.id, "Too low! Try again.")  
        elif guess > target:  
            bot.send_message(message.chat.id, "Too high! Try again.")  
        else:  
            bot.send_message(message.chat.id, "Correct! You guessed the number!")  
            del guessing_game[message.chat.id]  
    except ValueError:  
        bot.send_message(message.chat.id, "Please send a valid number.")

import requests
import random

@bot.message_handler(commands=['gif'])
def send_gif(message):
    query = message.text.replace("/gif", "").strip() or "funny"
    url = f"https://g.tenor.com/v1/search?q={query}&key=LIVDSRZULELA&limit=1"  
    response = requests.get(url).json()
    
    if response.get("results"):
        gif_url = response["results"][0]["media"][0]["gif"]["url"]
        bot.send_animation(message.chat.id, gif_url)
    else:
        bot.send_message(message.chat.id, "No GIFs found!")

import random

predictions = [
    "Yes, definitely!",
    "No way, not happening!",
    "The future is unclear... try again.",
    "Absolutely!",
    "Not in a million years.",
    "The signs point to yes.",
    "Ask again later.",
    "Chances are slim.",
    "It's looking good!",
    "Don't count on it."
]

@bot.message_handler(commands=['predict'])
def predict_future(message):
    prediction = random.choice(predictions)
    bot.send_message(message.chat.id, f"🔮 {prediction}")

import requests

@bot.message_handler(commands=['define'])
def define_word(message):
    words = message.text.split(maxsplit=1)
    if len(words) < 2:
        bot.send_message(message.chat.id, "Please provide a word to define. Example: `/define python`")
        return
    
    word = words[1]
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    
    response = requests.get(url).json()
    
    if isinstance(response, list):
        definition = response[0]['meanings'][0]['definitions'][0]['definition']
        bot.send_message(message.chat.id, f"📖 **Definition of {word}:**\n{definition}")
    else:
        bot.send_message(message.chat.id, "❌ Word not found.")



import time

@bot.message_handler(commands=['spamm'])
def spam_message(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /spamm <count> <message>")
        return

    try:
        count = int(args[1])
        if count > 10:
            count = 10  # Limit max spam to 50 messages
        spam_text = args[2]
        for _ in range(count):
            bot.send_message(message.chat.id, spam_text)
            time.sleep(0.5)  # Adds a 0.5-second delay between messages
    except ValueError:
        bot.reply_to(message, "Invalid number. Usage: /spam <count> <message>")

@bot.message_handler(commands=['hug'])
def hug_user(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.first_name
        sender = message.from_user.first_name
        bot.reply_to(message, f"🤗 {sender} gives {user} a big hug!")
    else:
        bot.reply_to(message, "🤗 Who do you want to hug? Reply to their message!")

roasts = ["You're like a cloud... when you disappear, it's a beautiful day! 🌤️",
          "You're proof that even evolution takes a step back sometimes. 🦴",
          "You bring everyone so much joy… when you leave the chat. 😆"
    "You're proof that even evolution takes a step backward sometimes.",
    "Your secrets are safe with me. I never even listen when you tell me them.",
    "You're like a cloud… when you disappear, it’s a beautiful day.",
    "You're not stupid; you just have bad luck thinking.",
    "You bring everyone so much joy… when you leave the room.",
    "You're like a penny—two-faced and not worth much.",
    "Your brain is like a web browser with 50 tabs open, and all of them are frozen.",
    "You have something on your chin… no, the third one down.",
    "Your Wi-Fi signal is stronger than your personality.",
    "You bring people together... to talk about how annoying you are.",
    "I'd agree with you, but then we’d both be wrong.",
    "Your secrets are safe with me. I just forget them instantly.",
    "You have something on your face—oh wait, that’s just your personality.",
    "You bring everyone together… against you.",
    "You're like a software update—no one wants you, but we’re forced to put up with you.",
    "You're so slow, even a snail would tell you to hurry up.",
    "You have the perfect face for radio.",
    "You're like a cloud... full of hot air and ruining the sunshine.",
    "I’d explain it to you, but I left my crayons at home.",
    "You have something on your chin… no, the third one down.",
    "Your jokes are like expired milk—no one enjoys them, but they make people sick.",
    "You have so many gaps in your knowledge, even Swiss cheese is jealous.",
    "Your presence is like a speed bump—unnecessary and slowing everyone down.",
    "You're like a candle in the wind... mostly just smoke and an occasional flicker.",
    "You make onions cry.",
    "You're like a Wi-Fi signal—weak and constantly dropping.",
    "You're proof that even artificial intelligence has limits.",
    "You're about as useful as a screen door on a submarine.",
    "I’d call you a tool, but even tools have a purpose.",
    "You remind me of a penny—always getting picked up and dropped again.",
    "You bring balance to the room—by making everyone else look smarter.",
    "Your personality is like an elevator—either up or down, never interesting.",
    "You're like an expired coupon—once useful, now just a waste of space.",
    "You're about as reliable as a weather forecast.",
    "You're like a participation trophy—present, but not impressive.",
    "Even Google can’t find what’s right about you.",
    "Your ideas are so original, even copy-paste gets tired of you.",
    "You're so extra, even unnecessary things feel overused.",
    "Your intelligence is like a broken clock—right twice a day, but still broken.",
    "You're like a one-star review—loud, annoying, and mostly ignored.",
    "You're a rare breed… of disappointment.",
    "Your talent is like a mirage—looks promising but disappears up close.",
    "If I had a dollar for every smart thought you had, I’d still be broke.",
    "You bring people together… to leave the conversation.",
    "Your sarcasm detector is as broken as your logic.",
    "You're like a pop-up ad—annoying, useless, and always in the way.",
    "Your comebacks are like boomerangs—they never really hit the mark.",
    "You're like an old phone battery—constantly draining and barely working.",
    "Your voice is like an alarm clock—loud, repetitive, and something people try to avoid.",
    "You have the same energy as an unplugged toaster.",
    "You're living proof that common sense isn’t so common."]

@bot.message_handler(commands=['roast'])
def roast_user(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.first_name
        bot.reply_to(message, f"{user}, {random.choice(roasts)}")
    else:
        bot.reply_to(message, "🔥 Reply to someone to roast them!")

@bot.message_handler(commands=['tagall'])
def tag_all_members(message):
    if message.chat.type == "private":
        bot.reply_to(message, "⚠ This command can only be used in a group!")
        return

    chat_id = message.chat.id
    try:
        members = bot.get_chat_administrators(chat_id)  # Get all admins (alternative to all members)
        tags = [f"@{admin.user.username}" for admin in members if admin.user.username]  # Mention admins
        tag_message = "🚀 Attention Everyone! " + " ".join(tags)

        bot.send_message(chat_id, tag_message, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠ I don't have permission to access member lists!")

# List of commonly used bad words in English and Hindi


@bot.message_handler(commands=['time'])
def server_time(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.reply_to(message, f"⏳ Current time: {current_time}")


import time

@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    sent_message = bot.send_message(message.chat.id, "🏓 Pinging...")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    bot.edit_message_text(f"🏓 Pong! `{ping_time}ms`", message.chat.id, sent_message.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['about'])
def about_bot(message):
    bot.reply_to(message, "I'm a Telegram Bot created to managw group and do some fun commands. My owner is @Hokage_xMinato. Hope u like me!!  🚀")
### 🚀 AFK SYSTEM (Now Responds to Mentions) ###

@bot.message_handler(commands=['rizz'])
def rizz_meter(message):
    rizz_percent = random.randint(1, 100)
    bot.reply_to(message, f"😏 Rizz Level: {rizz_percent}%")

@bot.message_handler(commands=['simp'])
def simp_meter(message):
    simp_percent = random.randint(1, 100)
    bot.reply_to(message, f"❤️ Simp Level: {simp_percent}%")



BAN_FILE = "banned_users.json"

# Load existing bans
if os.path.exists(BAN_FILE):
    with open(BAN_FILE, "r") as f:
        banned_users = json.load(f)
else:
    banned_users = {}

def is_admin(message):
    """Check if the user is an admin"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_admins = bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in chat_admins)

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ You must be an admin to use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "❌ Reply to a user's message to ban them.")
        return

    user_id = message.reply_to_message.from_user.id
    chat_id = str(message.chat.id)

    bot.ban_chat_member(message.chat.id, user_id)
    
    # Store ban in JSON
    if chat_id not in banned_users:
        banned_users[chat_id] = []
    if user_id not in banned_users[chat_id]:
        banned_users[chat_id].append(user_id)
    
    with open(BAN_FILE, "w") as f:
        json.dump(banned_users, f, indent=4)
    
    bot.reply_to(message, f"✅ Banned user <b>{message.reply_to_message.from_user.first_name}</b>.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ You must be an admin to use this command.")
        return

    try:
        user_id = int(message.text.split()[1])
        chat_id = str(message.chat.id)

        bot.unban_chat_member(message.chat.id, user_id)

        # Remove from JSON
        if chat_id in banned_users and user_id in banned_users[chat_id]:
            banned_users[chat_id].remove(user_id)
            with open(BAN_FILE, "w") as f:
                json.dump(banned_users, f, indent=4)

        bot.reply_to(message, f"✅ Unbanned user with ID: <b>{user_id}</b>.")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Please provide a valid user ID.\nExample: <code>/unban 123456789</code>")






@bot.message_handler(commands=['meme'])
def send_meme(message):
    try:
        meme = requests.get("https://meme-api.com/gimme").json()
        bot.send_photo(message.chat.id, meme["url"])
    except:
        bot.reply_to(message, "⚠ Could not fetcheme right now!")

### 🚀 FUN COMMANDS ###

@bot.message_handler(commands=['askme'])
def eight_ball(message):
    responses = ["Yes", "No", "Maybe", "Ask again later", "Definitely", "I don't think so"]
    bot.reply_to(message, random.choice(responses))

@bot.message_handler(commands=['roll'])
def roll_dice(message):
    bot.reply_to(message, f"🎲 You rolled a {random.randint(1, 6)}!")

@bot.message_handler(commands=['coinflip'])
def coin_flip(message):
    bot.reply_to(message, f"🪙 Coin flip: {random.choice(['Heads', 'Tails'])}")

@bot.message_handler(commands=['joke'])
def tell_joke(message):
    jokes = ["Why did the chicken cross the road? To get to the other side!", "I told my wife she was drawing her eyebrows too high. She looked surprised."]
    bot.reply_to(message, random.choice(jokes))

@bot.message_handler(commands=['quote'])
def send_quote(message):
    quotes = ["Believe in yourself!", "Dream big and never give up!", "Hard work pays off."]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['fact'])
def random_fact(message):
    facts = ["Honey never spoils.", "Bananas are berries, but strawberries are not.", "Octopuses have three hearts."]
    bot.reply_to(message, random.choice(facts))

@bot.message_handler(commands=['love'])
def love_calc(message):
    names = message.text[6:].strip()
    love_percentage = random.randint(10, 100)
    bot.reply_to(message, f"❤️ Love score for {names}: {love_percentage}%")

@bot.message_handler(commands=['reverse'])
def reverse_text(message):
    text = message.text[9:].strip()
    if not text:
        bot.reply_to(message, "⚠ Please provide text to reverse.")
        return
    bot.reply_to(message, f"🔄 {text[::-1]}")

@bot.message_handler(commands=['calculate'])
def calculate_expression(message):
    expression = message.text[11:].strip()
    try:
        result = eval(expression)
        bot.reply_to(message, f"🧮 Result: {result}")
    except:
        bot.reply_to(message, "⚠ Invalid mathematical expression.")

### 🚀 CUSTOM MESSAGE RESPONSES ###

@bot.message_handler(func=lambda message: message.text.lower() in ["hi", "hello", "bye"])
def custom_greetings(message):
    responses = {
        "hi": "👋 Hi there!",
        "hello": "😊 Hello!How are u doing today?",
        "bye": "👋 Goodbye! See you soon!",
        "kiss":"Aww!U want to kiss me umahhh!!"
    }
    bot.reply_to(message, responses[message.text.lower()])

### 🚀 IMAGE COMMANDS ###

@bot.message_handler(commands=['dog', 'cat'])
def send_animal_photo(message):
    animal = "dog" if message.text == "/dog" else "cat"
    response = requests.get(f"https://random.dog/woof.json" if animal == "dog" else "https://api.thecatapi.com/v1/images/search").json()
    bot.send_photo(message.chat.id, response['url'] if animal == "dog" else response[0]['url'])

### 🚀 GENERAL COMMANDS ###

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "📌 Use /commands to see all available commands.")

import telebot
import requests
import io
from PIL import Image

# Replace with your Hugging Face API token
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
# Choose an image generation model on Hugging Face (replace with the actual endpoint)
HUGGINGFACE_MODEL_ENDPOINT = "https://router.huggingface.co/fal-ai/fal-ai/stable-diffusion-v35-large"

# Assuming your TeleBot instance 'bot' is already created in your main script
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def generate_image(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HUGGINGFACE_MODEL_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        image_bytes = response.content
        return image_bytes
    except requests.exceptions.RequestException as e:
        return f"Error generating image: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@bot.message_handler(commands=['image'])
def image_command(message):
    try:
        prompt = ' '.join(message.text.split()[1:])  # Get the prompt after /image
        if not prompt:
            bot.reply_to(message, "Please provide a prompt after the /image command (e.g., /image A majestic cat painting)")
            return

        bot.reply_to(message, "Generating image...")
        image_data = generate_image(prompt)

        if isinstance(image_data, str):  # Check if it's an error message
            bot.reply_to(message, f"Sorry, there was an issue generating the image: {image_data}")
        else:
            with io.BytesIO(image_data) as img_io:
                img_io.seek(0)
                bot.send_photo(message.chat.id, img_io)

    except Exception as e:
        bot.reply_to(message, f"An unexpected error occurred: {e}")

# You would typically have your main bot polling loop in your main script
# if __name__ == '__main__':
#     print("Bot is running...")
#     bot.polling(none_stop=True)



import requests



HF_TOKEN = os.getenv("HF_TOKEN")  # Replace with your Hugging Face API token
HF_MODEL = "google/gemma-2b"  # Replace with your chosen model name

def query_huggingface_api(prompt):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_length": 100}
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Error: {response.status_code}, {response.text}"

@bot.message_handler(commands=['ai'])
def handle_ai_command(message):
    user_input = message.text[4:].strip()
    if user_input:
        response = query_huggingface_api(user_input)
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Please provide a prompt after the /ai command.")

import json
import os
import time

AFK_FILE = "afk_users.json"

# Load AFK users from JSON
def load_afk_users():
    if not os.path.exists(AFK_FILE):
        return {}
    with open(AFK_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

# Save AFK users to JSON
def save_afk_users(afk_users):
    with open(AFK_FILE, "w") as file:
        json.dump(afk_users, file, indent=4)

# Load existing AFK data
afk_users = load_afk_users()

# Command to set AFK
@bot.message_handler(commands=["afk"])
def set_afk(message):
    user_id = message.from_user.id
    reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "No reason provided"
    
    afk_users[user_id] = {
        "reason": reason,
        "time": int(time.time())  # Store the timestamp
    }
    save_afk_users(afk_users)
    
    bot.reply_to(message, f"{message.from_user.first_name} is now AFK: {reason}")

# Remove AFK status when user sends a message
@bot.message_handler(func=lambda message: message.from_user.id in afk_users)
def remove_afk(message):
    user_id = message.from_user.id
    afk_data = afk_users.pop(user_id, None)

    if afk_data:
        afk_time = int(time.time()) - afk_data["time"]
        minutes = afk_time // 60
        seconds = afk_time % 60
        save_afk_users(afk_users)
        
        bot.reply_to(message, f"Welcome back, {message.from_user.first_name}! You were AFK for {minutes} min {seconds} sec.")

# Notify when replying or mentioning an AFK user
@bot.message_handler(func=lambda message: message.reply_to_message or message.entities)
def check_afk(message):
    mentioned_users = []

    # Check if someone is mentioned in the message
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                user_id = entity.user.id if hasattr(entity, 'user') else None
                if user_id:
                    mentioned_users.append(user_id)

    # Check if the message is a reply
    if message.reply_to_message:
        mentioned_users.append(message.reply_to_message.from_user.id)

    # Notify if any mentioned or replied user is AFK
    for user_id in mentioned_users:
        if user_id in afk_users:
            afk_info = afk_users[user_id]
            afk_duration = int(time.time()) - afk_info["time"]
            minutes = afk_duration // 60
            seconds = afk_duration % 60

            bot.reply_to(message, f"{message.reply_to_message.from_user.first_name} is AFK: {afk_info['reason']} (AFK for {minutes} min {seconds} sec).")
        bot.polling(none_stop=True)

