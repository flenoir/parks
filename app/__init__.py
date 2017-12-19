'''
app/__init__.py
'''
# -*- encoding :utf8 -*-

from flask import Flask, render_template, jsonify
from flask_bower import Bower

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
Bower(app)

@app.route('/')

def extract_data():
    '''fonction principale'''

    import json
    import xml.etree.ElementTree as ET
    from urllib.request import urlopen
    import re

    # on enverra les xml dans un liste qu'on initialise
    parking_datas = []

    # import du fichier Json qui référence les données de tous les parkings
    with urlopen("https://data.montpellier3m.fr/api/3/action/package_show?id=90e17b94-989f-4d66-83f4-766d4587bec2&utm_source=Site%20internet&utm_campaign=Clic%20sur%20%3A%20https%3A//data.montpellier3m.fr/api/3/action/package_show/90e17b94-989f-4d66-83f4-766d4587bec2&utm_term=https%3A//data.montpellier3m.fr/api/3/action/package_show/90e17b94-989f-4d66-83f4-766d4587bec2") as file:
        data = json.load(file)
        resources = data["result"][0]["resources"]
        # récupération des adresses des xml des parkings et envoi dans la liste des parkings
        for item in resources:
            # parking_datas[item['name']] = item['url']
            single_park = {}
            url = item['url']
            with urlopen(url) as furl:
                tree = ET.parse(furl)
                root = tree.getroot()
            for xdata in root:
                single_park[str(xdata.tag)] = str(xdata.text)
            single_park['fullName'] = item['name']

            parking_datas.append(single_park)

    print(parking_datas)

    with open("curated_parking_list.json", "w") as outfile:
        # on enleve les 2 premieres valeurs
        json.dump(parking_datas[2:], outfile)

    # creation d'un class parking pour créer tous mes parkings
    class Parking:

        def __init__(self, **url):
            for attr_name, attr_value in url.items():
                # equivaut à my_object.attribute = value
                setattr(self, attr_name, attr_value)

    # def main():
    all_parks = []
    # on ouvre le json propre des parkings
    for parks in json.load(open("curated_parking_list.json")):
        # on instancie chaque parking avec son nom
        parks['Name'] = Parking(**parks)
        Date = parks['Name'].DateTime
        CleanedDate = re.search('(?<=T)([0-9][0-9][:][0-9][0-9])', Date)
        current_status = parks['Name'].Status

        if current_status == "Open":
            current_status = current_status.replace("Open", "ouvert")
        elif current_status == "Full":
            current_status = current_status.replace("Full", "saturé")
        else:
            current_status = current_status.replace("Closed", "fermé")
        all_parks.append({'name': parks['Name'].Name, "status": current_status, "date": CleanedDate.group(0),
                          'total': parks['Name'].Total.lstrip("0"), 'free': parks['Name'].Free.lstrip("0"), 'fullname': parks['fullName']})

    return render_template('index.html', all_parks=all_parks)


# Load the views
from app import views

# Load the config file
app.config.from_object('config')
