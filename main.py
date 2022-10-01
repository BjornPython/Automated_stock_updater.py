import datetime
import requests
from email.message import EmailMessage
import ssl
import smtplib

"""Gets the date today and the date for the last 2 and 3 days."""
today = datetime.date.today()
last_2_days = today - datetime.timedelta(days=2)
last_3_days = today - datetime.timedelta(days=3)

search_for = "TESLA"  # latest subject of the news.
coin = "TSLA"  # Coin you are searching for.
news_API_key = ""  # Your Key
news_endpoint = "https://newsapi.org/v2/everything"  # Endpoint of newsapi

alphavantage_API_key = ""  # Your Key
alphavantage_endpoint = "https://www.alphavantage.co/query"  # Endpoint of alphavantage
alphavantage_parameters = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": coin,
    "interval": "60min",
    "apikey": alphavantage_API_key
}

"""Gets the data from the alphavantage with an api."""
alphavantage_response = requests.get(url=alphavantage_endpoint, params=alphavantage_parameters)
alphavantage_response.raise_for_status()
alphavantage_data = alphavantage_response.json()

close_f = float(alphavantage_data["Time Series (60min)"][f"{last_2_days} 16:00:00"]["4. close"])
close_i = float(alphavantage_data["Time Series (60min)"][f"{last_3_days} 16:00:00"]["4. close"])


change = round(((close_f - close_i) / close_i) * 100, 2)  # Calculates the percentage change of the closing values.

print(change)
if change >= 5 or change <= -5:  # Only continues if close value increased/decreased by 5%
    title_text = f"📈 increased by {change}% !" if change >= 5 else f"📉 decreased by {change}% !"
    title = f"{coin} STOCK {title_text}"
    body = f"{coin} STOCK VALUES\n{last_3_days}: {close_i}\n{last_2_days}: {close_f}\nValue decreased by {change}%" \
           f"\n\nNEWS:\n\n\n"

    news_parameters = {
        "q": search_for,
        "from": f"{today}",
        "sortBy": "publishedAt",
        "apiKey": news_API_key,
    }
    """Gets the news from the newsapi endpoint."""
    news_response = requests.get(url=news_endpoint, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]

    articles = 5 if len(news_data) > 5 else len(news_data)  # Limits the sent news to five.

    """Appends the articles to the body."""
    for article in range(articles):  
        body += f"{news_data[article]['title']}\n{news_data[article]['description']}\n" \
                f"link:{news_data[article]['url']}\n\n"
        
    """Email information"""
    my_email = ""  # Your email
    my_pass = ""  # Your email's password
    recipient = "" # The receiver
    em = EmailMessage()
    em["From"] = my_email
    em["Subject"] = title
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as connection:
        connection.login(my_email, my_pass)
        connection.sendmail(my_email,
                            recipient,
                            em.as_string()
                            )
