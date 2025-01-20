import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove
import tmdbsimple as tmdb
from PIL import Image
from io import BytesIO
import requests
import random

#create telebot 
bot = telebot.TeleBot(token = "<YOUR_TELEBOT_TOKEN>")

#global variables
global category, searchType, genre_auswahl,chatID
items = []

genres = [{"id":28,"name":"Action"},{"id":12,"name":"Adventure"},{"id":16,"name":"Animation"},{"id":35,"name":"Comedy"},{"id":80,"name":"Crime"},{"id":99,"name":"Documentary"},{"id":18,"name":"Drama"},{"id":10751,"name":"Family"},{"id":14,"name":"Fantasy"},{"id":36,"name":"History"},{"id":27,"name":"Horror"},{"id":10402,"name":"Music"},{"id":9648,"name":"Mystery"},{"id":10749,"name":"Romance"},{"id":878,"name":"Science Fiction"},{"id":10770,"name":"TV Movie"},{"id":53,"name":"Thriller"},{"id":10752,"name":"War"},{"id":37,"name":"Western"}]

# TMDb-Funktionen ================================================================================================
tmdb.API_KEY = "<YOUR_TMDB_TOKEN>"

def discover_tmdb(media_type, genre,pages):
    discover = tmdb.Discover()
    params = {
        "language": "de-DE",
        "sort_by": "popularity.desc",
        "include_adult": True,
        "region":"DE",
        "page": pages,
        "watch_region":"DE",
        "with_watch_providers":"10|2|3|8|9|20|29|30|130",
    }
    if (genre != 0):
        params["with_genres"] = str(genre)
    if media_type == "Film":
        response = discover.movie(**params)
    elif media_type == "Serie":
        response = discover.tv(**params)
    else:
        response = {"results": []}

    return response.get("results", [])

def get_details(media_type, media_id):
    if media_type == "Film":
        movie = tmdb.Movies(media_id)
        details = movie.info(language="de-DE")
        providers = movie.watch_providers().get("results", {}).get("DE", {}).get("flatrate", [])
    elif media_type == "Serie":
        tv = tmdb.TV(media_id)
        details = tv.info(language="de-DE")
        #print(tv.watch_providers())
        #providers = tv.watch_providers().get("results", {}).get("DE", {}).get("flatrate", [])
        providers = []
    else:
        details = {}
        providers = []

    details["providers"] = providers
    return details

# TMDb-Funktionen ================================================================================================

def send_image_as_sticker(chat_id, result,index):
    poster_path = result.get("poster_path")
    title = result.get("title") or result.get("name", "Unbekannt")
    vote_average = result.get("vote_average", "Keine Bewertung")
    vote_count = result.get("vote_count", 0)
    
    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        btn_name =["btn1","btn2","btn3","btn4","btn5"]
        button = InlineKeyboardButton(text = title +"\n"+str(round(vote_average,1)), callback_data =btn_name[index])
        inline_keyboard = InlineKeyboardMarkup(row_width = 1)
        inline_keyboard.add(button)
        #bot.send_sticker(chat_id, output, reply_markup = inline_keyboard)
        bot.send_photo(chat_id, image, reply_markup = inline_keyboard)
    else:
        print("Bild konnte nicht heruntergeladen werden.")

#create Buttons for the genre selection
reply_keyboard_genre = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_genre.add("ALLE")
for index, genre in enumerate(genres):
    reply_keyboard_genre.add(genre["name"])

#create Keyboard for movie and Sereis
reply_keyboard_1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_1.add("Film","Serie")

#create Keyboard for Top 5 or genre
reply_keyboard_2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_2.add("Top 5","5 zufällige")

#create Keyboard to remove the Keyboard
reply_keyboard_Remove = ReplyKeyboardRemove(selective=False)

#massage handler for the startup
@bot.message_handler(commands=['start'])
def start_massage(message):
    global chatID
    chatID = message.chat.id
    bot.send_message(message.chat.id, "Film oder Serie?", reply_markup = reply_keyboard_1)
    bot.register_next_step_handler(message, process_genre)

#massage handler for genres
def process_genre(message):
    global searchType
    searchType = message.text
    bot.send_message(message.chat.id, "Genre auswählen:", reply_markup = reply_keyboard_genre)
    bot.register_next_step_handler(message, process_searchType)
    
#massage handler for the selection of movie oder Series
def process_searchType(message):
    global genre_auswahl
    genre_auswahl = message.text
    bot.send_message(message.chat.id, "Top 5 oder 5 zufällige", reply_markup = reply_keyboard_2)
    bot.register_next_step_handler(message, process_category)

#massage handler for the selection of top 5 or genre
def process_category(message):
    global category, searchType, genre
    items.clear()
    category = message.text
    genre_ID = 0
    if (genre_auswahl != "ALLE"):
        for genre in genres:
            if genre["name"] == genre_auswahl:
                genre_ID = genre["id"]

    if category == "5 zufällige":
        bot.send_message(message.chat.id, "5 zufällige werden gesucht.", reply_markup = reply_keyboard_Remove)
        
        #get Top 100 Films
        results = discover_tmdb(searchType, genre_ID,1)
        for i in range(2, 6):
            results = results +discover_tmdb(searchType, genre_ID,i)
        
        if results == []:
            if searchType =="Serie":
                bot.send_message(message.chat.id, "Keine Serie von dem Genre "+genre_auswahl+" gefunden.", reply_markup = reply_keyboard_Remove)
            if searchType =="Film":
                bot.send_message(message.chat.id, "Kein Film von dem Genre "+genre_auswahl+" gefunden.", reply_markup = reply_keyboard_Remove)
        else:
            #pick 5 random numbers
            random_index = set()
            while len(random_index) < 5:
                number = random.randint(1, len(results))
                random_index.add(number)
                
            for i in range(0,5):
                result = results[list(random_index)[i]]
                items.append(result)
                send_image_as_sticker(chatID,result,i)
            
    elif category == "Top 5":
        bot.send_message(message.chat.id, "Top 5 werden gesucht.", reply_markup = reply_keyboard_Remove)
        results = discover_tmdb(searchType, genre_ID,1)
        if results == []:
            if searchType =="Serie":
                bot.send_message(message.chat.id, "Keine Serie von dem Genre "+genre_auswahl+" gefunden.", reply_markup = reply_keyboard_Remove)
            if searchType =="Film":
                bot.send_message(message.chat.id, "Kein Film von dem Genre "+genre_auswahl+" gefunden.", reply_markup = reply_keyboard_Remove)
        else:
            for index,result in enumerate(results):
                if index >= 5:  # Abbrechen, wenn mehr als 5 Elemente verarbeitet wurden
                    break
                items.append(result)
                send_image_as_sticker(chatID,result,index)
    
#callback handler for the detailed information
@bot.callback_query_handler(func=lambda call:True)
def check_button(call):
    global category, searchType, genre_auswahl
    if call.data == "btn1":
        details = get_details(searchType, items[0].get("id"))
        title = items[0].get("title") or items[0].get("name", "Unbekannt")
        vote_average = items[0].get("vote_average", "Keine Bewertung")
        vote_count = items[0].get("vote_count", 0)
    elif call.data == "btn2":
        details = get_details(searchType, items[1].get("id"))
        title = items[1].get("title") or items[1].get("name", "Unbekannt")
        vote_average = items[1].get("vote_average", "Keine Bewertung")
        vote_count = items[1].get("vote_count", 0)
    elif call.data == "btn3":
        details = get_details(searchType, items[2].get("id"))
        title = items[2].get("title") or items[2].get("name", "Unbekannt")
        vote_average = items[2].get("vote_average", "Keine Bewertung")
        vote_count = items[2].get("vote_count", 0)
    elif call.data == "btn4":
        details = get_details(searchType, items[3].get("id"))
        title = items[3].get("title") or items[3].get("name", "Unbekannt")
        vote_average = items[3].get("vote_average", "Keine Bewertung")
        vote_count = items[3].get("vote_count", 0)
    elif call.data == "btn5":
        details = get_details(searchType, items[4].get("id"))
        title = items[4].get("title") or items[4].get("name", "Unbekannt")
        vote_average = items[4].get("vote_average", "Keine Bewertung")
        vote_count = items[4].get("vote_count", 0)
    if call.data == "btn1" or call.data == "btn2" or call.data == "btn3" or call.data == "btn4" or call.data == "btn5":
        if searchType == "Film":
            providers = details.get("providers", [])
            runtime = details.get("runtime", "")
            release_date = details.get("release_date", "")[:4]
            provider_names = ", ".join([provider.get("provider_name", "Unbekannt") for provider in providers]) or "Keine Anbieter verfügbar"
            message = title+"\nLänge: "+str(runtime)+"min\n"+release_date+"\n"+str(round(vote_average,1))+ "/10 ("+str(vote_count)+" Bewertungen)"+"\n"+provider_names
        elif searchType == "Serie":
            providers = details.get("providers", [])
            number_of_episodes = details.get("number_of_episodes", "")
            number_of_seasons = details.get("number_of_seasons", "")
            first_air_date = details.get("first_air_date", "")[:4]
            provider_names = ", ".join([provider.get("provider_name", "Unbekannt") for provider in providers]) or "Keine Anbieter verfügbar"
            message = title+"\nseit: "+first_air_date+"\nSeasons: "+str(number_of_seasons)+" Episodes: "+str(number_of_episodes)+"\n"+str(round(vote_average,1))+ "/10 ("+str(vote_count)+" Bewertungen)"+"\n"+provider_names
        bot.answer_callback_query(call.id, message,show_alert=True)
    
#loop for the massage handlers
bot.polling()
