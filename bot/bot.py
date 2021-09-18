import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# import spotipy.oauth2 as oauth2
import telebot
# from telebot import types

bot = telebot.TeleBot('1777796225:AAFtRFarfoko16uzRTe5hYjZA2ZSZ2o_DEA')
CLIENT_ID = "58c3f1f57a244975b57fab6a61f3094c"
CLIENT_SECRET = "cf2212c09dc54a2980f05106672cdcb8"
REDIRECT_URI = "http://example.com"

# year = input("Which year do you want to travel to? Type date in this format YYYY-MM-DD: ")


@bot.message_handler(commands = ['start', 'help'])
def command_help(message):
    bot.reply_to(message, "Hello, I can help you create Spotify playlist from certain period of time.\n"
                          "Which year do you want to travel to? Type date in this format YYYY-MM-DD: ")


@bot.message_handler(regexp = '^[0-9]+-(0?[1-9]|[1][0-2])-[0-9]+$')
def get_text_messages(message):
    try:
        response = requests.get("https://www.billboard.com/charts/hot-100/" + message.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        song_names_spans = soup.find_all("span", class_ = "chart-element__information__song")
        song_names = [song.getText() for song in song_names_spans]

        # Spotify Authentication
        sp = spotipy.Spotify(
            auth_manager = SpotifyOAuth(scope = "playlist-modify-private", redirect_uri = "http://example.com",
                client_id = "58c3f1f57a244975b57fab6a61f3094c", client_secret = "cf2212c09dc54a2980f05106672cdcb8",
                show_dialog = True, cache_path = "token.txt"))
        user_id = sp.current_user()["id"]
        print(user_id)

        # Searching Spotify for songs by title
        song_uris = []
        year = message.text.split("-")[0]
        for song in song_names:
            result = sp.search(q = f"track:{song} year:{year}", type = "track")
            # print(result)
            print("Still Running")
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                bot.reply_to(message, f"{song} doesn't exist in Spotify. Skipped.")

        # Creating a new private playlist in Spotify
        playlist = sp.user_playlist_create(user = user_id, name = f"{year} Billboard 100", public = False)
        bot.reply_to(message, playlist["external_urls"]["spotify"])

        # Adding songs found into the new playlist
        sp.playlist_add_items(playlist_id = playlist["id"], items = song_uris)
    except BaseException:
        bot.reply_to(message, "Please type date in this format YYYY-MM-DD: ")


bot.polling(none_stop = True, interval = 0)
