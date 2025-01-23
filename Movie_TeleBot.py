import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove
import tmdbsimple as tmdb
import requests
import random
import time

#create telebot 
bot = telebot.TeleBot(token = "7648000591:AAGCifCA6IGZNQbgWE3nYcAW6KLhhiLaxPg")

#tmdb TEY
tmdb.API_KEY = "b0c4a4e00c846e0322bbfea2f054f5a9"

#global variables
global category, searchType, genre_auswahl, func, message_deleted
items = []
message_deleted = -1

#available genres for movies and series
genres_movie = [{"id":28,"name":"Action"},{"id":12,"name":"Adventure"},{"id":16,"name":"Animation"},{"id":35,"name":"Comedy"},{"id":80,"name":"Crime"},{"id":99,"name":"Documentary"},{"id":18,"name":"Drama"},{"id":10751,"name":"Family"},{"id":14,"name":"Fantasy"},{"id":36,"name":"History"},{"id":27,"name":"Horror"},{"id":10402,"name":"Music"},{"id":9648,"name":"Mystery"},{"id":10749,"name":"Romance"},{"id":878,"name":"Science Fiction"},{"id":10770,"name":"TV Movie"},{"id":53,"name":"Thriller"},{"id":10752,"name":"War"},{"id":37,"name":"Western"}]
genres_series =[{"id":10759,"name":"Action & Adventure"},{"id":16,"name":"Animation"},{"id":35,"name":"Comedy"},{"id":80,"name":"Crime"},{"id":99,"name":"Documentary"},{"id":18,"name":"Drama"},{"id":10751,"name":"Family"},{"id":10762,"name":"Kids"},{"id":9648,"name":"Mystery"},{"id":10763,"name":"News"},{"id":10764,"name":"Reality"},{"id":10765,"name":"Sci-Fi & Fantasy"},{"id":10766,"name":"Soap"},{"id":10767,"name":"Talk"},{"id":10768,"name":"War & Politics"},{"id":37,"name":"Western"}]

#get Films and Series
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

#get details about movies and series
def get_details(media_type, media_id):
    if media_type == "Film":
        movie = tmdb.Movies(media_id)
        details = movie.info(language="de-DE")
        providers = movie.watch_providers().get("results", {}).get("DE", {}).get("flatrate", [])
    elif media_type == "Serie":
        tv = tmdb.TV(media_id)
        details = tv.info(language="de-DE")
        providers = []
    else:
        details = {}
        providers = []

    details["providers"] = providers
    return details

# send results
def send_Results(chat_id, results):
    for index, result in enumerate(results):
        
        # create message
        title = result.get("title") or result.get("name", "Unbekannt")
        button_info = InlineKeyboardButton(text = title, callback_data ="info"+str(index))
        button_description = InlineKeyboardButton(text = "Beschreibung", callback_data ="desc"+str(index))
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        inline_keyboard.add(button_info)
        inline_keyboard.add(button_description)
        
        # result data
        poster_path = result.get("poster_path")
        if poster_path != None:
            image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            bot.send_photo(chat_id, image_url, reply_markup = inline_keyboard)
        elif poster_path == None:
            bot.send_message(chat_id,"Kein Bild vorhanden.", reply_markup = inline_keyboard)

#create Buttons for the genre selection
reply_keyboard_genres_movie = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_genres_movie.add("ALLE")
for index, genre in enumerate(genres_movie):
    reply_keyboard_genres_movie.add(genre["name"])
    
reply_keyboard_genres_series = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_genres_series.add("ALLE")
for index, genre in enumerate(genres_series):
    reply_keyboard_genres_series.add(genre["name"])

#create Keyboard for statup
reply_keyboard_func = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_func.add("Empfehlung","Suche")

#create Keyboard for movie and Sereis
reply_keyboard_type = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_type.add("Film","Serie")

#create Keyboard for Top 5 or genre
reply_keyboard_category = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
reply_keyboard_category.add("Top 5","5 zufällige")

#create Keyboard to remove the Keyboard
reply_keyboard_Remove = ReplyKeyboardRemove(selective=False)

# create delete Keyoard
button_delete = InlineKeyboardButton(text = "❌", callback_data ="delete")
inline_keyboard_delete = InlineKeyboardMarkup(row_width=2)
inline_keyboard_delete.add(button_delete)

#massage handler for the startup
@bot.message_handler(commands=['start'])
def process_func(message):
    bot.send_message(message.chat.id, "Empfehlung oder Suche", reply_markup = reply_keyboard_func)
    bot.register_next_step_handler(message, process_type)

#massage handler for the function
def process_type(message):
    global func
    func = message.text
    if func != "Empfehlung" and func != "Suche":
        bot.send_message(message.chat.id, "Empfehlung oder Suche", reply_markup = reply_keyboard_func)
        bot.register_next_step_handler(message, process_type)
    else:
        bot.send_message(message.chat.id, "Film oder Serie?", reply_markup = reply_keyboard_type)
        bot.register_next_step_handler(message, process_genre)
    
#massage handler for the search type / media type
def process_genre(message):
    global searchType
    searchType = message.text
    if searchType != "Film" and searchType != "Serie":
        bot.send_message(message.chat.id, "Film oder Serie?", reply_markup = reply_keyboard_type)
        bot.register_next_step_handler(message, process_genre)
    else:
        if func == "Empfehlung":
            if searchType == "Film":
                bot.send_message(message.chat.id, "Genre auswählen:", reply_markup = reply_keyboard_genres_movie)
            if searchType == "Serie":
                bot.send_message(message.chat.id, "Genre auswählen:", reply_markup = reply_keyboard_genres_series)
            bot.register_next_step_handler(message, process_searchType)
        elif func == "Suche":
            bot.send_message(message.chat.id, "Geben Sie ein Suchbegriff ein.", reply_markup = reply_keyboard_Remove)
            bot.register_next_step_handler(message, process_Suche)

#massage handler for the search of movies and series
def process_Suche(message):
    global searchType
    items.clear()
    search = tmdb.Search()
    if searchType == "Film":
        results = search.movie(query=message.text, language="de-DE").get("results", [])
    elif searchType == "Serie":
        results = search.tv(query=message.text, language="de-DE").get("results", [])
        
    if results != []:
        for result in results[:10]:
            items.append(result)
        send_Results(message.chat.id,items)
    else:
        if searchType == "Film":
            bot.send_message(message.chat.id, "Kein Film gefunden.", reply_markup = reply_keyboard_Remove)
        elif searchType == "Serie":
            bot.send_message(message.chat.id, "Keine Serie gefunden.", reply_markup = reply_keyboard_Remove)
        bot.send_message(message.chat.id, "Geben Sie ein Suchbegriff ein.", reply_markup = reply_keyboard_Remove)
        bot.register_next_step_handler(message, process_Suche)

#massage handler for the selection genre
def process_searchType(message):
    global genre_auswahl,  searchType
    if searchType == "Film":
        genres = genres_movie
    elif searchType == "Serie":
        genres = genres_series
    genre_auswahl = message.text
    genre_good = False
    if genre_auswahl == "ALLE":
        genre_good = True
    else:
        for index, genre in enumerate(genres):
            if genre_auswahl == genre["name"]:
                genre_good = True
    if not genre_good:
        process_searchType(message)
    else:
        bot.send_message(message.chat.id, "Top 5 oder 5 zufällige", reply_markup = reply_keyboard_category)
        bot.register_next_step_handler(message, process_category)

#massage handler for the selection of top 5 or genre
def process_category(message):
    global category, searchType, genre
    items.clear()
    category = message.text
    if category != "Top 5" and category != "5 zufällige":
        process_searchType(message)
    else:
        if searchType == "Film":
            genres = genres_movie
        elif searchType == "Serie":
            genres = genres_series
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
                send_Results(message.chat.id,items)
                
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
                send_Results(message.chat.id,items)

#callback handler for the delete button
@bot.callback_query_handler(func=lambda call: call.data == "delete")
def delete_message(call):
    # Lösche die Nachricht
    bot.delete_message(call.message.chat.id, call.message.message_id)
    time.sleep(1)
    
#callback handler for the detailed information
@bot.callback_query_handler(func=lambda call:True)
def check_button(call):
    global category, searchType, genre_auswahl
    if call.data[:4] == "info":
        index = int(call.data[4:])
        details = get_details(searchType, items[index].get("id"))
        title = items[index].get("title") or items[index].get("name", "Unbekannt")
        vote_average = items[index].get("vote_average", "Keine Bewertung")
        vote_count = items[index].get("vote_count", index)
        if searchType == "Film":
            providers = details.get("providers", [])
            runtime = details.get("runtime", "")
            genres_details = details.get("genres", [])
            genre_string = ""
            if genres_details != []:
                genre_string=genres_details[0]["name"]
                for genre_detail in genres_details[1:]:
                    genre_string =genre_string+ ", "+genre_detail["name"]
            release_date = details.get("release_date", "")[:4]
            provider_names = ", ".join([provider.get("provider_name", "Unbekannt") for provider in providers]) or "Keine Anbieter verfügbar"
            message = title+"\nLänge: "+str(runtime)+"min\n"+release_date+"\nGenre: "+genre_string+"\n"+str(round(vote_average,1))+ "/10 ("+str(vote_count)+" Bewertungen)"+"\n"+provider_names
        elif searchType == "Serie":
            providers = details.get("providers", [])
            number_of_episodes = details.get("number_of_episodes", "")
            number_of_seasons = details.get("number_of_seasons", "")
            genres_details = details.get("genres", [])
            genre_string = ""
            if genres_details != []:
                genre_string=genres_details[0]["name"]
                for genre_detail in genres_details[1:]:
                    genre_string =genre_string+ ", "+genre_detail["name"]
            first_air_date = details.get("first_air_date", "")[:4]
            provider_names = ", ".join([provider.get("provider_name", "Unbekannt") for provider in providers]) or "Keine Anbieter verfügbar"
            message = title+"\nseit: "+first_air_date+"\nGenre: "+genre_string+"\nStaffeln: "+str(number_of_seasons)+", Episoden: "+str(number_of_episodes)+"\n"+str(round(vote_average,1))+ "/10 ("+str(vote_count)+" Bewertungen)"+"\n"+provider_names
        if len(message) > 200:
            message = message[:197]+"..."
        bot.answer_callback_query(call.id, message,show_alert=True)
    elif call.data[:4] == "desc":
        index = int(call.data[4:])
        details = get_details(searchType, items[index].get("id"))
        description = details.get("overview")
        if description =="":
            description = "Keine Beschreibung vorhanden."
        title = items[index].get("title") or items[index].get("name", "Unbekannt")
        bot.send_message(call.message.chat.id,title+":\n"+description , reply_markup = inline_keyboard_delete)

#loop for the telegram bot
bot.polling()