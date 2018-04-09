from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import requests, json

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])

def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number. Strips and converts to lowercase
    body = request.values.get('Body', None).strip().lower()
    
    # Start our TwiML response
    resp = MessagingResponse()
    
    # Get text phone number
    from_number = request.values.get('From')
    
    # Shopify credentials
    key = '[SHOPIFY API KEY]'
    pw = '[SHOPIFY API PASSWORD]'
    headers = {'Content-Type': 'application/json',}
    
    # Get customer order
    def customer():
        try:
            url = 'https://%s:%s@[SHOP_NAME].myshopify.com/admin/customers/search.json?query=phone:"%s"&fields=id,email,first_name,last_name' % (key, pw, from_number)
            response = requests.get(url, headers=headers)
            customer = response.json()['customers'][0]
            return customer
        except:
            return resp.message("sorry, could not locate your profile. What is your email?")
    
    # Status order
    def option_status():
        try:
            cust = customer()
            url= 'https://%s:%s@[SHOP_NAME].myshopify.com/admin/customers/%s/orders.json?limit=1' % (key, pw, cust['id'])
            response = requests.get(url, headers=headers)
            customer_order = response.json()['orders'][0]
            message = ("Status selected: %s, order number %s was created at %s" % (cust['first_name'], cust['id'], customer_order['created_at']))
            resp.message(message)
        except:
            resp.message("sorry, unable to locate order.")
    
    # Pause order    
    def option_pause():
        try:
            cust = customer()
            url= 'https://%s:%s@[SHOP_NAME].myshopify.com/admin/customers/%s/orders.json?limit=1' % (key, pw, cust['id'])
            response = requests.get(url, headers=headers)
            customer_order = response.json()['orders'][0]
            message = ("Pause selected: %s, order number %s was created at %s will be paused" % (cust['first_name'], cust['id'], customer_order['created_at']))
            resp.message(message)
        except:
            resp.message("sorry, unable to locate order.")
    
    # Detects if email is in the message        
    def detect_email(message):
        is_email = ("@" in message)
        if is_email == True:
            print('this is an email')
            return option_email(message)
        else:
            print('this is not an email')
            cust = customer()
            return resp.message("Hello %s %s, what can we do for you?  To pause your order, reply 'PAUSE' or to status your order, reply 'STATUS'. If you are not %s please reply with, 'NOT ME'" % (cust['first_name'], cust['last_name'], cust['first_name']))
    
    # User responds with email    
    def option_email(message):
        try:
            url = 'https://%s:%s@[SHOP_NAME].myshopify.com/admin/customers/search.json?query=email:"%s"&fields=id,email,first_name,last_name' % (key, pw, message)
            response = requests.get(url, headers=headers)
            customer = response.json()['customers'][0]
            return customer
        except:
            return resp.message("Sorry, we are unable to locate your email")
        
    # Determine the right reply for this message
    if body == 'pause':
        option_pause()
    elif body == 'status':
        option_status()
    elif body == 'not me':
        resp.message("Sorry about that. What is your email address?")
    else:
        detect_email(body)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
