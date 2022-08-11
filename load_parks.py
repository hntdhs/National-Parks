import pdb
import urllib
import json
from os import environ
from app import app
from sqlalchemy import desc
from models import db, Park



def save_parks():
    
    API_KEY = environ.get("NPS_GOV_API_KEY")
    
    endpoint = f"https://developer.nps.gov/api/v1/parks?limit=500&start=0&API_KEY={API_KEY}"
    
    print(endpoint)
    req = urllib.request.Request(endpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    park_ids_in_db = [park.id for park in Park.query.all()]

    
    # Prepare and execute output
    for place in data["data"]:
        if place["designation"] == "National Park" and place["id"] not in park_ids_in_db:
            try:
                price = place["entrancePasses"][0]["cost"]
                description = place["entrancePasses"][0]["description"]
                title = place["entrancePasses"][0]["title"]
            except IndexError:
                price = None  
                description = None
                title = None

        else:
            continue

        activity_names = []
        for activity in place["activities"]:
            activity_names.append(activity['name'])

        park = Park(
            id=place["id"], 
            name=place["fullName"], 
            code=place["parkCode"], 
            description=place["description"], 
            ent_fees_cost=place["entranceFees"][0]["cost"], 
            ent_fees_description=place["entranceFees"][0]["description"], 
            ent_fees_title=place["entranceFees"][0]["title"], 
            ent_passes_cost=price, 
            ent_passes_description=description, 
            ent_passes_title=title, 
            activity=", ".join(activity_names),
            # activity=place["activities"][0]["name"], 
            state=place["states"], 
            phone=place["contacts"]["phoneNumbers"][0]["phoneNumber"], 
            directions_url=place["directionsUrl"], 
            hours=place["operatingHours"][0]["description"], 
            town=place["addresses"][0]["city"], 
            image_title=place["images"][0]["title"], 
            image_altText=place["images"][0]["altText"], 
            image_url=place["images"][0]["url"], 
            weather_info=place["weatherInfo"],)

        db.session.add(park)

    db.session.commit()


if __name__ == "__main__":
    db.app = app
    save_parks()

    # Why put this in a seperate script from app.py? Because we don't want to hit the NPS' API every time someone via our Flask app hits the parks endpoint. If 100 people do that, we'll be getting the same data each time, which is inefficient. Also API's have rate limits, and it'll start getting 429 codes, which means too many requests. A user would get a 500 internal server error. So if we load the data into the database in a separate script, it just hits the external API once, and our endpoint just queries the database to get that information.