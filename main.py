import requests
import json
import datetime
import schedule
import time
import smtplib
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

def send_message(msg):
    carriers = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
    }

    to_number = '{}{}'.format(os.environ["PHONE"],carriers['verizon'])
    #The auth email and password I used are from setting up a google service that can send messages
    #https://support.google.com/accounts/answer/185833?visit_id=638136011549548814-2332719711&p=InvalidSecondFactor&rd=1
    #This link will get you the auth_password associated to the email you enabled it from
    auth = (os.environ["AUTH_EMAIL"], os.environ["AUTH_PASSWORD"])

	# Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP("smtp.gmail.com", 587 )
    server.starttls()
    server.login(auth[0], auth[1])

	# Send text message through SMS gateway of destination number
    print(msg)
    server.sendmail(auth[0], to_number, msg)

def check_prices():
    URL = "https://www.walgreens.com/store/c/doritos-dinamita-chile-limon-dinamita-chile-limon/ID=300420947-product"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content,'lxml')
    tag = soup.find("span",{"id": "sales-price-info"})

    walgreen_price = tag.text

    URL2 = "https://www.target.com/p/doritos-chili-limon-tortilla-chips-11-25oz/-/A-52535120"
    p2 = requests.get(URL2)

    test2 = (p2.text).split("formatted_current_price")[1]
    lower = test2.index(":")
    upper = test2.index(",")
    target_price = test2[lower+1+2:upper-2]

    with open('prices.json', 'r') as openfile:
        json_read = json.load(openfile)

    last_update = json_read[-1]["Prices"]

    if(last_update["Target"] != target_price or last_update["Walgreens"] != walgreen_price): 
       
        day = datetime.datetime.today()
        today_prices ={
            "Date:":str(day),
            "Prices":{
                "Target":target_price,
                "Walgreens":walgreen_price,
            }
        }
        json_read.append(today_prices)
        json_save = json.dumps(json_read, indent=4)
        with open("prices.json", "w") as outfile:
            outfile.write(json_save)        
        msg = 'Target - {}\nWalgreens - {}'.format(target_price,walgreen_price)
        send_message(msg)

# schedule.every().day.at("12:00").do(check_prices)

# while(True):
#     schedule.run_pending()
#     time.sleep(10)
check_prices()