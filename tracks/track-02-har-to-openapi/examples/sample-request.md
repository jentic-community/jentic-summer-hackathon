

---

# Daft.ie API Discovery Report & Documentation

**Version:** 1.0.0
**Source:** Reverse-engineered from public web traffic on `https://www.daft.ie`.

## 1. Introduction

This document provides a comprehensive reference for the unofficial public API of Daft.ie. The endpoints detailed below were discovered by analyzing network traffic during a typical user session. The primary purpose of this documentation is to enable developers and AI agents to programmatically access public property data for search, analysis, and discovery.

**Disclaimer:** This is not an official API. The endpoints, parameters, and response structures are subject to change without notice.

## 2. API Endpoints Reference

This section details the five key endpoints discovered, their functions, and data structures.

### 4.1 Search Property Listings

This is the primary endpoint for searching for property listings.

`GET /api/v2/ads/listings`

#### Description
Retrieves a paginated list of property ads based on a set of filter criteria. The response includes an array of listing summary objects and pagination details.

#### Example Request (cURL)
```bash
curl -X GET "https://www.daft.ie/api/v2/ads/listings?pageSize=20&mediaSizes=size720x480"
```

#### Example Response Snippet
The response is a large object. The most important keys are `listings` and `paging`.

```json
{
    "listings": [
        {
            "listing": {
                "id": 6261763,
                "title": "Claremount, Claremorris, Claremorris, Co. Mayo, F12ER22",
                "price": "€195,000",
                "numBedrooms": "2 Bed",
                "numBathrooms": "1 Bath",
                "propertyType": "Bungalow",
                "ber": {
                    "rating": "E2"
                },
                "seller": {
                    "sellerId": 5276,
                    "name": "Kevin Kirrane",
                    "branch": "APP Kirrane Auctioneering"
                },
                "media": {
                    "totalImages": 30,
                    "images": [
                        {
                            "size720x480": "https://media.daft.ie/..."
                        }
                    ]
                }
            }
        }
    ],
    "paging": {
        "totalPages": 770,
        "currentPage": 1,
        "totalResults": 15387,
        "pageSize": 20
    }
}
```

### 4.2 Get Specific Property Details

This endpoint retrieves all the detailed information for a single property listing.

`GET /_next/data/{buildId}/property.json`

#### Description
Used on the property details page to fetch the complete data set for a listing, including the full description, facilities, features, and media.

#### Parameters

| Name      | In   | Required | Type   | Description                                                                    |
| :-------- | :--- | :------- | :----- | :----------------------------------------------------------------------------- |
| `buildId` | Path | Yes      | String | A dynamic build ID from the Next.js framework. This value changes periodically. |
| `id`      | Query| Yes      | String | The unique numerical identifier of the property.                               |
| `address` | Query| No       | String | The URL-friendly address slug of the property.                                 |


#### Example Request (cURL)
```bash
curl -X GET "https://www.daft.ie/_next/data/r6FgZXTa2BqUvCvw0HNkI/property.json?id=6261763"
```

#### Example Response Snippet
The core data is nested within the `pageProps.listing` object.

```json
{
    "pageProps": {
        "listing": {
            "id": 6261763,
            "title": "Claremount, Claremorris, Claremorris, Co. Mayo, F12ER22",
            "price": "€195,000",
            "propertyType": "Bungalow",
            "description": "APP Kirrane Auctioneering proudly presents this beautifully finished two bedroom/ three bedroom detached bungalow...",
            "facilities": [
                { "key": "PARKING", "name": "Parking" },
                { "key": "OIL_FIRED_CENTRAL_HEATING", "name": "Oil Fired Central Heating" }
            ],
            "features": [
                "Eircode F12ER22",
                "Prime location with natural stone front wall and walking distance to Claremorris town centre"
            ]
        }
    }
}```

### 4.3 Get Available Search Filters

This endpoint provides the possible filter options for a given search category.

`GET /old/v3/filters/search/{searchType}`

#### Description
This is a crucial helper endpoint for building a user-facing search interface. It returns a structured JSON object defining all possible filter controls, such as price ranges, property types, and number of beds.

#### Parameters
| Name         | In   | Required | Type   | Description                                                                 |
| :----------- | :--- | :------- | :----- | :-------------------------------------------------------------------------- |
| `searchType` | Path | Yes      | String | The category of search, e.g., `residential-sold`, `residential-for-sale`. |

#### Example Request (cURL)
```bash
curl -X GET "https://www.daft.ie/old/v3/filters/search/residential-sold"```

#### Example Response Snippet
The response contains an array of filter objects. Each object describes a UI control (e.g., dropdown) and its possible values.

```json
{
    "name": "residential-sold",
    "showByDefault": [
        {
            "id": 2801,
            "name": "location",
            "displayName": "Location",
            "filterType": { "name": "LocationInputBox" }
        },
        {
            "id": 2802,
            "name": "salePrice",
            "displayName": "Asking Price",
            "filterType": { "name": "DropDownRange" },
            "values": [
                {
                    "from": [
                        { "displayName": "Min", "value": "" },
                        { "displayName": "€25k", "value": "25000" }
                        // ... and so on
                    ],
                    "to": [
                        { "displayName": "Max", "value": "" },
                        { "displayName": "€25k", "value": "25000" }
                        // ... and so on
                    ]
                }
            ]
        }
        // ... more filter objects for beds, baths, etc.
    ]
}
```

### 4.4 Get Autocomplete Suggestions

This endpoint provides search suggestions for use in a search bar.

`POST /old/v1/autocomplete`

#### Description
As a user types into a search bar, this endpoint can be called to provide relevant suggestions for locations, which helps guide the user and format the query correctly for other endpoints.

#### Request Body
The endpoint expects a JSON payload containing the user's partial search query.

```json
{
  "query": "dublin"
}
```

#### Example Request (cURL)
```bash
curl -X POST "https://www.daft.ie/old/v1/autocomplete" \
-H "Content-Type: application/json" \
-d '{"query": "dublin"}'```

#### Example Response
The response is an array of suggestion objects. Each object includes a display name and a breakdown of property counts in that area.

```json
[
    {
        "id": "1",
        "displayName": "Dublin (County)",
        "displayValue": "dublin",
        "propertyCount": {
            "residentialForSale": 3478,
            "residentialForRent": 847,
            "sharing": 839
        }
    }
]
```

### 4.5 Check User Session Status

An internal endpoint to check if the current session belongs to a logged-in user.

`POST /api/user`

#### Description
This endpoint is called on page loads to check the visitor's authentication state. It is not used for fetching public data but is a core part of the site's functionality. For unauthenticated requests (as an AI agent would make), it consistently returns an empty object.

#### Example Request (cURL)
```bash
curl -X POST "https://www.daft.ie/api/user"
```

#### Example Response (for a Guest)
```json
{}
```

---
## 6. Troubleshooting

*   **404 Errors on `/property.json`:** The `{buildId}` in the path is dynamic and expires. You must obtain a fresh `buildId` by first loading a property page on the main website and capturing the new value from the network traffic.
*   **Blocked Requests:** High-volume, rapid-fire requests may be blocked by anti-bot measures. Ensure your requests include a valid `User-Agent` header and are spaced out to mimic human behavior.
