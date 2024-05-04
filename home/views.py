from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from decimal import Decimal
from dotenv import load_dotenv
import requests
import json
import re
import os

load_dotenv()
API_KEY = os.environ.get("API_KEY")
AMMOUNT_NEEDED = 7500

def get_mercado_pago_data():
    url = "https://api.mercadopago.com/v1/payments/search"
    headers = { 
        "Authorization" : f"Bearer {API_KEY}"
    }
    params = {
        "sort": "date_created",
        "criteria": "desc",
        "range": "date_created",
        "begin_date": "NOW-120DAYS",
        "end_date": "NOW"
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # Process the response
        data = response.text
        return data
    else:
        # Handle the error
        print(f'Error: {response.status_code}')
        return None
    
def parse_json_response(response_content):
    # Convert JSON string to Python dictionary
    try:
        data = json.loads(response_content)
        return data
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
        return None
    
def calculate_total_donated(dictionary):
    total_donated = 0
    for transaction in dictionary["results"]:
        if transaction["status"] == "approved":
            total_donated += (Decimal(transaction["transaction_amount"]) - Decimal(transaction["transaction_amount_refunded"]))
    
    return total_donated

def calculate_progress(total_donated):
    progress = (total_donated*100)/AMMOUNT_NEEDED
    print(progress)
    return round(progress, 2)

def home(request):
    response = get_mercado_pago_data()
    print(response)
    dictionary = parse_json_response(response)
    total_donated = calculate_total_donated(dictionary)
    progress = calculate_progress(total_donated)
    template = loader.get_template('home.html')
    print(progress)
    context = {
        'progress': f"{progress}%"
    }
    return HttpResponse(template.render(context, request))