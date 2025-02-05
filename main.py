import streamlit as st
import requests
import json
from bs4 import BeautifulSoup as bs
from csv import writer
from time import sleep
from random import choice

try:
    with open('quotes.json', 'r') as file:
        all_quotes = json.load(file)
except FileNotFoundError:
    all_quotes = []
if not all_quotes:
    base_url = "http://quotes.toscrape.com"
    url = "/page/1"

# this part of code do the scraping and save in a file
# for effeciency,

    while url:
        res = requests.get(f"{base_url}{url}")
        soup = bs(res.text, "html.parser")

        quotes = soup.find_all(class_='quote')
        
        for quote in quotes:
            href = quote.find('a')['href']
            res1 = requests.get(f"{base_url}{href}")
            soup1 = bs(res1.text, 'html.parser')

            all_quotes.append({
                'text':quote.find(class_='text').get_text(),
                'author':quote.find(class_='author').get_text(),
                'birth_date' : soup1.find(class_='author-born-date').get_text(),
                'birth_place' : soup1.find(class_='author-born-location').get_text()
            })
        next_ = soup.find(class_='next')
        url = next_.find('a')['href'] if next_ else None
        sleep(2)

    with open('quotes.json', 'w') as file:
        json.dump(all_quotes, file, indent=4)

# this part of code do the game

if 'quote' not in st.session_state:
    st.session_state.quote = choice(all_quotes)
    st.session_state.remaining_guesses = 3
if 'user_guess' not in st.session_state:
    st.session_state.user_guess = ''

title = "Guess the Quote Game 🎭"
st.title(title)
st.write(f"Here is a quote: **{st.session_state.quote['text']}**")

guess = st.text_input(f'Who said this quote? Guesses remaining: {st.session_state.remaining_guesses} : ', value=st.session_state.user_guess, key='guess_input')

if guess:
        if guess.lower() == st.session_state.quote['author'].lower():
            st.success('🎉 You got it right')
            st.session_state.quote = choice(all_quotes)
            st.session_state.remaining_guesses = 3
            st.session_state.user_guess = ''
            st.rerun()
        else:
            st.session_state.remaining_guesses -= 1
            # st.session_state.user_guess = ''

            if st.session_state.remaining_guesses == 2:
                st.warning(f'Here is a hint: The author was born on {st.session_state.quote['birth_date']} {st.session_state.quote['birth_place']}')

            elif st.session_state.remaining_guesses == 1:
                r1 = st.session_state.quote['author'].split(' ')[1][0:]
                st.warning(f'Here is a hint: The author last name is {r1}')
            elif st.session_state.remaining_guesses == 0 :
                st.error(f'❌ Sorry you ran out of guesses. The answer was {st.session_state.quote['author']}')
                st.session_state.quote = choice(all_quotes)
                st.session_state.remaining_guesses = 3

            st.session_state.user_guess = ''
            st.rerun()