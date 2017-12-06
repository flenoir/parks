# -*- encoding :utf8 -*-
import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen

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
		with urlopen(url) as f:
			tree = ET.parse(f)
			root = tree.getroot()
		for x in root:
			single_park[str(x.tag)] = str(x.text)

		parking_datas.append(single_park)


with open("curated_parking_list.json","w") as outfile:
	json.dump(parking_datas[2:], outfile) # on enleve les 2 premieres valeurs

# creation d'un class parking pour créer tous mes parkings
class Parking:
	
	def __init__(self, **url):
		for attr_name, attr_value in url.items():
			setattr(self, attr_name, attr_value) # equivaut à my_object.attribute = value

def main():
	all_parks = []
	for parks in json.load(open("curated_parking_list.json")): # on ouvre le json propre des parkings
		parks['Name'] = Parking(**parks) # on instancie chaque parking avec son nom
		Date = parks['Name'].DateTime
		print("Today at {}, {} is {} and has {} places left on a total of {} places.".format(Date[11:-3],parks['Name'].Name,parks['Name'].Status, parks['Name'].Free, parks["Name"].Total))
		all_parks.append(parks['Name'])
	return all_parks

for i in main():
	print(i.Name)
