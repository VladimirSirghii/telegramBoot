import telebot
import requests
import schedule

# Tokenul de acces al botului tău
TOKEN = '6187003407:AAFLjkODNqzyKq3v1BPmrDSvN1CwSKN2e-8'

# URL-ul serviciului API pentru prețurile criptomonedelor
API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# Criptomonedele pe care le vom urmări
cryptocurrencies = ['bitcoin']
vs_currencies = ['usd']

# Prețurile constante pentru comparație
constant_prices = {
    'bitcoin': 29200
}

# Investiția totală
total_investment = 1000

# Inițializarea botului
bot = telebot.TeleBot(TOKEN)

# Funcția pentru a obține prețurile actuale ale criptomonedelor


def get_crypto_prices():
    params = {
        'ids': ','.join(cryptocurrencies),
        'vs_currencies': ','.join(vs_currencies)
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        crypto_prices = {
            currency: data[currency][vs_currencies[0]] for currency in cryptocurrencies
        }
        return crypto_prices
    else:
        print('Eroare la obținerea prețurilor criptomonedelor.')

# Funcția pentru a calcula profitul total


def calculate_total_profit():
    crypto_prices = get_crypto_prices()
    if crypto_prices is not None:
        total_profit = 0
        for currency, current_price in crypto_prices.items():
            constant_price = constant_prices.get(currency)
            if constant_price is not None:
                investment = total_investment / len(cryptocurrencies)
                quantity = investment / constant_price
                current_value = quantity * current_price
                profit = current_value - investment
                total_profit += profit

        return total_profit

# Funcția pentru a inițializa planificarea de verificare a profitului


def schedule_profit_check():
    total_profit = calculate_total_profit()
    if total_profit is not None:
        if total_profit > 1:
            for _ in range(3):
                bot.send_message(chat_id=bot.get_updates(
                )[-1].message.chat.id, text='Profitul total este mai mare de 1 dolar!')

# Funcția pentru a afișa profitul curent


@bot.message_handler(commands=['profit'])
def show_current_profit(message):
    crypto_prices = get_crypto_prices()
    if crypto_prices is not None:
        profit_message = 'Profitul/Perderea curentă:\n'
        for currency, current_price in crypto_prices.items():
            constant_price = constant_prices.get(currency)
            if constant_price is not None:
                investment = total_investment / len(cryptocurrencies)
                quantity = investment / constant_price
                current_value = quantity * current_price
                profit = current_value - investment
                profit_percentage = (profit / investment) * 100
                profit_message += f'{currency.capitalize()}: {profit:.2f} USD ({profit_percentage:.2f}%)\n'

        bot.send_message(chat_id=message.chat.id, text=profit_message)

# Funcția pentru a afișa prețurile actuale ale criptomonedelor și modificările față de prețurile constante


@bot.message_handler(commands=['prices'])
def show_current_prices(message):
    crypto_prices = get_crypto_prices()
    if crypto_prices is not None:
        price_message = 'Prețurile curente ale criptomonedelor:\n'
        for currency, current_price in crypto_prices.items():
            constant_price = constant_prices.get(currency)
            if constant_price is not None:
                price_difference = current_price - constant_price
                price_percentage = (price_difference / constant_price) * 100
                price_message += f'{currency.capitalize()}: {current_price:.2f} USD ({price_percentage:.2f}%)\n'

        bot.send_message(chat_id=message.chat.id, text=price_message)

# Funcția pentru a inițializa planificarea


def start_scheduling():
    schedule_profit_check()
    schedule.every(5).minutes.do(schedule_profit_check)


# Pornirea planificării și a botului
start_scheduling()
bot.polling()
