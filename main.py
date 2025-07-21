import streamlit as st
import requests
import json
from bs4 import BeautifulSoup as bs
from time import sleep
from random import choice

def scrape_quotes():
    """Scrape quotes from quotes.toscrape.com"""
    all_quotes = []
    base_url = "http://quotes.toscrape.com"
    url = "/page/1"
    
    try:
        while url:
            res = requests.get(f"{base_url}{url}")
            res.raise_for_status()
            
            soup = bs(res.text, "html.parser")
            quotes = soup.find_all(class_='quote')
            
            for quote in quotes:
                href = quote.find('a')['href']
                try:
                    res1 = requests.get(f"{base_url}{href}")
                    res1.raise_for_status()
                    soup1 = bs(res1.text, 'html.parser')
                    
                    all_quotes.append({
                        'text': quote.find(class_='text').get_text(),
                        'author': quote.find(class_='author').get_text(),
                        'birth_date': soup1.find(class_='author-born-date').get_text(),
                        'birth_place': soup1.find(class_='author-born-location').get_text()
                    })
                except requests.exceptions.RequestException:
                    continue
            
            next_ = soup.find(class_='next')
            url = next_.find('a')['href'] if next_ else None
            sleep(2)
            
    except requests.exceptions.RequestException:
        pass
    
    return all_quotes

# Load quotes from file or show loading message
@st.cache_data
def load_quotes():
    try:
        with open('quotes.json', 'r') as file:
            quotes = json.load(file)
            if quotes:  # If file exists and has content
                return quotes
    except FileNotFoundError:
        pass
    
    # If no quotes file or empty, scrape them
    st.info("🔄 Loading quotes for the first time... This may take a moment.")
    quotes = scrape_quotes()
    
    if quotes:
        with open('quotes.json', 'w') as file:
            json.dump(quotes, file, indent=4)
        st.success(f"✅ Loaded {len(quotes)} quotes!")
        st.rerun()
    
    return quotes

# Load quotes
all_quotes = load_quotes()

# Game logic
if not all_quotes:
    st.error("❌ No quotes available. Please check your internet connection and try again.")
    st.stop()

# Initialize session state
if 'quote' not in st.session_state:
    st.session_state.quote = choice(all_quotes)
    st.session_state.remaining_guesses = 3
    st.session_state.show_message = False
    st.session_state.message_type = ""
    st.session_state.message_content = ""

st.title("Guess the Quote Game 🎭")
st.write(f"Here is a quote: **{st.session_state.quote['text']}**")

# Show any pending messages
if st.session_state.show_message:
    if st.session_state.message_type == "success":
        st.success(st.session_state.message_content)
        if st.button("Next Quote"):
            st.session_state.quote = choice(all_quotes)
            st.session_state.remaining_guesses = 3
            st.session_state.show_message = False
            st.rerun()
    elif st.session_state.message_type == "error":
        st.error(st.session_state.message_content)
        if st.button("Try Another Quote"):
            st.session_state.quote = choice(all_quotes)
            st.session_state.remaining_guesses = 3
            st.session_state.show_message = False
            st.rerun()
    elif st.session_state.message_type == "warning":
        st.warning(st.session_state.message_content)

# Only show input if not showing success/error message
if not st.session_state.show_message or st.session_state.message_type == "warning":
    guess = st.text_input(
        f"Who said this quote? Guesses remaining: {st.session_state.remaining_guesses}: ",
        key='guess_input'
    )

    if guess:
        if guess.lower() == st.session_state.quote['author'].lower():
            st.session_state.show_message = True
            st.session_state.message_type = "success"
            st.session_state.message_content = '🎉 You got it right!'
            st.rerun()
        else:
            st.session_state.remaining_guesses -= 1

            if st.session_state.remaining_guesses == 2:
                st.session_state.show_message = True
                st.session_state.message_type = "warning"
                st.session_state.message_content = f"Here is a hint: The author was born on {st.session_state.quote['birth_date']} in {st.session_state.quote['birth_place']}."
            elif st.session_state.remaining_guesses == 1:
                last_name_initial = st.session_state.quote['author'].split(' ')[-1][0]
                st.session_state.show_message = True
                st.session_state.message_type = "warning"
                st.session_state.message_content = f"Here is a hint: The author's last name starts with '{last_name_initial}'."
            elif st.session_state.remaining_guesses == 0:
                st.session_state.show_message = True
                st.session_state.message_type = "error"
                st.session_state.message_content = f"❌ Sorry, you ran out of guesses. The answer was {st.session_state.quote['author']}."
            
            st.rerun()
