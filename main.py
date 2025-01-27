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

quote = choice(all_quotes)
remaining_guesses = 3
print(f'Here is a quote: {quote['text']}')

while remaining_guesses > 0:
    guess = input(f'Who said this quote? Guesses remaining: {remaining_guesses} : ')

    if guess.lower() == quote['author'].lower():
        print('You got it right')
        break
    remaining_guesses -= 1

    if remaining_guesses == 2:
        print(f'Here is a hint: The author was born on {quote['birth_date']} {quote['birth_place']}')

    elif remaining_guesses == 1:
        r1 = quote['author'].split(' ')[1][0:]
        print(f'Here is a hint: The author last name is {r1}')

if remaining_guesses == 0 :
    print(f'Sorry you ran out of guesses. The answer was {quote['author']}')