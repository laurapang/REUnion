# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 18:37:04 2015

@author: akash
"""

import facebook
import urllib
import json
import requests 

APIKEY = "ae21f0f2-29f4-43c6-8fc5-cdfc55010c01"
URL = "https://api.havenondemand.com/1/api/sync/{}/v1"
ENTITY_TYPES = [
            "address_au",
            "address_ca",
            "address_de",
            "address_es",
            "address_fr",
            "address_gb",
            "address_it",
            "address_us",
            "address_zh",
            "pii",
            "pii_ext",
            "number_phone_au",
            "number_phone_ca",
            "number_phone_gb",
            "number_phone_us",
            "number_phone_de",
            "number_phone_fr",
            "number_phone_it",
            "number_phone_es",
            "number_phone_zh",
            "ip_address",
            "number_cc",
            "nationalinsurance_gb",
            "socialsecurity_us",
            "socialinsurance_ca",
            "licenseplate_us",
            "licenseplate_gb",
            "licenseplate_fr",
            "licenseplate_de",
            "licenseplate_ca",
            "driverslicense_us",
            "driverslicense_gb",
            "driverslicense_fr",
            "driverslicense_de",
            "driverslicense_ca",
            "bankaccount_ca",
            "bankaccount_fr",
            "bankaccount_gb",
            "bankaccount_de",
            "bankaccount_ie",
            "bankaccount_us"
        ]

def post_requests(function, data={}, files={}):
   data["apikey"] = APIKEY
   callurl = URL.format(function)
   r = requests.post(callurl, data=data, files=files)
   return r.json()
               
results = post_requests('analyzesentiment', data = {'text': 'i think too much...'})
print results['aggregate']['sentiment']
print results['aggregate']['score']
print

entities = post_requests('extractentities', data = {'text': 'SSN: 123 45 7189, Phone #: (646) 623-0283, Pet: cutie', 'entity_type': ENTITY_TYPES })
for entity in entities['entities']:
    print entity
    print