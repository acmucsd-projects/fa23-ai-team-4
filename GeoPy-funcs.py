import geopy
from geopy.geocoders import Nominatim

geopy.geocoders.options.default_user_agent = "Nominatim"
def coordinates (location_string):

    geolocator = Nominatim(user_agent="Nominatim")
    location = geolocator.geocode(location_string)
    print(location.address)
    print((location.latitude, location.longitude))
    print(location.raw)

coordinates("University of California, San Diego")

transcript = YouTubeTranscriptApi.get_transcript("IV1dbqcg9bI")
transcript_text = ""

for line in transcript:
    transcript_text += (line["text"].replace("\n"," "))

print(transcript_text)