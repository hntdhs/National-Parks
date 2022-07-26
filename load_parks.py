import urllib
import json

from sqlalchemy import desc
from app import app
from models import db, Park


def save_parks():
    # endpoint = "https://developer.nps.gov/api/v1/parks?limit=90&API_KEY=HCUiwHQkl2bavKC6YK6zCXUQTrOnhs6K3f2BZD7Z"
    
    # limit = 100
    
    endpoint = "https://developer.nps.gov/api/v1/parks?limit=500&start=0&API_KEY={API_KEY}"
    # won't go past 50 because that's the limit the API sets
    req = urllib.request.Request(endpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    # import ipdb; ipdb.set_trace()
    park_ids_in_db = [park.id for park in Park.query.all()]

    park_array = []
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
                # import ipdb; ipdb.set_trace()
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
                # these are causing the issue 
                # error is - 'string indices must be integers'
                # activity=activityNames,
                activity=place["activities"][0]["name"], 
                state=place["states"], 
                phone=place["contacts"]["phoneNumbers"][0]["phoneNumber"], 
                directions_url=place["directionsUrl"], 
                hours=place["operatingHours"][0]["description"], 
                town=place["addresses"][0]["city"], 
                image_title=place["images"][0]["title"], 
                image_altText=place["images"][0]["altText"], 
                image_url=place["images"][0]["url"], 
                weather_info=place["weatherInfo"],)

            park_array.append(park)
            db.session.add(park)

    db.session.commit()


if __name__ == "__main__":
    db.app = app
    save_parks()