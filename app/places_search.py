import os

import httpx
from dotenv import load_dotenv

load_dotenv()

# Realistic mock businesses to return if no API key or if the API fails
MOCK_BUSINESSES = {
    "dentists in Miami, FL": [
        {
            "place_id": "mock_miami_dentist_1",
            "name": "Brickell Family Dentistry",
            "phone": "+1 305-555-0199",
            "address": "1200 Brickell Ave, Miami, FL 33131",
            "website_url": "https://www.brickellfamilydentistry.com",
            "rating": 4.8,
            "user_ratings_total": 312,
            "search_query": "dentists in Miami, FL",
        },
        {
            "place_id": "mock_miami_dentist_2",
            "name": "Downtown Miami Dental Arts",
            "phone": "+1 305-555-0244",
            "address": "100 SE 2nd St, Miami, FL 33131",
            "website_url": "http://downtownmiamidentalarts.example.com",
            "rating": 4.2,
            "user_ratings_total": 45,
            "search_query": "dentists in Miami, FL",
        },
        {
            "place_id": "mock_miami_dentist_3",
            "name": "Biscayne Bay Dental Group",
            "phone": "+1 305-555-0311",
            "address": "3000 Biscayne Blvd, Miami, FL 33137",
            "website_url": None,
            "rating": 3.9,
            "user_ratings_total": 12,
            "search_query": "dentists in Miami, FL",
        },
    ],
    "lawyers in Tampa, FL": [
        {
            "place_id": "mock_tampa_lawyer_1",
            "name": "Tampa Bay Injury Law Group",
            "phone": "+1 813-555-1022",
            "address": "400 N Tampa St, Tampa, FL 33602",
            "website_url": "https://www.tampabayinjurylawgroup.com",
            "rating": 4.9,
            "user_ratings_total": 650,
            "search_query": "lawyers in Tampa, FL",
        },
        {
            "place_id": "mock_tampa_lawyer_2",
            "name": "Sarasota & Tampa Defense Attorneys",
            "phone": "+1 813-555-1099",
            "address": "201 E Kennedy Blvd, Tampa, FL 33602",
            "website_url": "https://sarasotatampadefense.example.com",
            "rating": 4.5,
            "user_ratings_total": 85,
            "search_query": "lawyers in Tampa, FL",
        },
    ],
}


def search_places_google(query: str, api_key: str | None = None) -> list:
    """
    Searches for businesses using Google Places API (New).
    If no key is configured or the request fails, falls back to mock results.
    """
    if not api_key:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    if not api_key or api_key == "your_google_places_api_key_here":
        print(f"[Places API] No API Key. Falling back to mock data for: '{query}'")
        return MOCK_BUSINESSES.get(
            query,
            [
                # Fallback for dynamic query
                {
                    "place_id": f"mock_dynamic_{query.replace(' ', '_')}_1",
                    "name": f"Florida General Enterprise ({query})",
                    "phone": "+1 800-555-0100",
                    "address": "100 Main St, Orlando, FL 32801",
                    "website_url": "https://www.floridageneralenterprise.com",
                    "rating": 4.5,
                    "user_ratings_total": 120,
                    "search_query": query,
                }
            ],
        )

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount",
    }
    body = {"textQuery": query, "languageCode": "en"}

    try:
        response = httpx.post(url, headers=headers, json=body, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        places = data.get("places", [])
        results = []
        for place in places:
            display_name = place.get("displayName", {})
            name = display_name.get("text", "Unknown Business")

            results.append(
                {
                    "place_id": place.get("id"),
                    "name": name,
                    "phone": place.get("nationalPhoneNumber"),
                    "address": place.get("formattedAddress"),
                    "website_url": place.get("websiteUri"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("userRatingCount"),
                    "search_query": query,
                }
            )
        print(
            f"[Places API] Successfully fetched {len(results)} results from Google Places API for: '{query}'"
        )
        return results

    except Exception as e:
        print(f"[Places API] Error calling Places API: {e}. Falling back to mock data.")
        return MOCK_BUSINESSES.get(
            query,
            [
                {
                    "place_id": f"mock_dynamic_err_{query.replace(' ', '_')}_1",
                    "name": f"Florida General Enterprise ({query})",
                    "phone": "+1 800-555-0100",
                    "address": "100 Main St, Orlando, FL 32801",
                    "website_url": "https://www.floridageneralenterprise.com",
                    "rating": 4.5,
                    "user_ratings_total": 120,
                    "search_query": query,
                }
            ],
        )
