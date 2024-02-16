import requests

url = "https://api.omnicasa.com/OmnicasaAPI.asmx/GetPropertyList"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {
    "CustomerName": "omnicasa_admin",
    "CustomerPassword": "test123",
    "LanguageID": "10",
    "PriceFrom": "1",
    "PriceTo": "1000000",
    "Goal": "1",
    "GeographicIDs": "2",
    "PostalCodes": "1",
    "TypeIDs": "1",
    "MinRoom": "1",
    "NrRooms": "2",
    "Recordfiles": "2",
    "CityNames": "",
    "PictureSizeMaxWidth": "10",
    "PictureSizeMaxHeight": "10",
    "Limit1": "0",
    "Limit2": "1",
    "SORTORDER": "-1",
}

response = requests.post(url, headers=headers, data=data)

# Print the response status code and content
print(f"Status Code: {response.status_code}")
print("Response Content:")
print(response.text)
