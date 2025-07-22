rules = [
    {
        "category": "Food",
        "subcategory": "Groceries",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "Lidl",
                    "tesco",
                    "sainsbury",
                    "aldi",
                    "sainsbury's",
                    "waitrose",
                    "m&s",
                    "Co-Op",
                ],
            }
        ],
    },
    {
        "category": "Food",
        "subcategory": "Eating Out",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    # Chain Restaurants
                    "wasabi",
                    "itsu",
                    "Nando’s",
                    "Bleecker Burger",
                    "Chipotle",
                    "Honest Burger",
                    "TORTILLA",
                    "franco manca",
                    "wagamama",
                    "Greggs",
                    "Flat Iron",
                ],
            }
        ],
    },
    {
        "category": "Food",
        "subcategory": "Takeaway/FastFood",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    # Fast Food
                    "kfc",
                    "mcdonalds",
                    "mcdonald’s",
                    "popeyes",
                    "shake shack",
                    "Burger King",
                    "LEON",
                    "subway",
                    "domino's",
                    "DOMINO S PIZZA",
                    "pizza hut",
                    "five guys",
                    # Deliveres
                    "deliveroo",
                    "just eat",
                    "uber eats",
                ],
            }
        ],
    },
    {
        "category": "Shopping",
        "subcategory": "Clothes",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "ZARA",
                    "H&M",
                    "UNIQLO",
                    "PRIMARK",
                    "JD Sports",
                    "ASOS",
                    "Nike",
                    "Adidas",
                    "TK Maxx",
                    "Next",
                    "Hollister",
                ],
            }
        ],
    },
    {
        "category": "Shopping",
        "subcategory": "Electronics",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "Argos",
                    "Currys",
                    "Apple Store",
                ],
            }
        ],
    },
    {
        "category": "Shopping",
        "subcategory": "Home",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "IKEA",
                    "Boots",
                    "John Lewis",
                ],
            }
        ],
    },
    {
        "category": "Shopping",
        "subcategory": "Other",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "Amazon",
                    "Etsy",
                    "Ebay",
                ],
            }
        ],
    },
    {
        "category": "Entertainment",
        "subcategory": "Cinema",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "cinema",
                    "Vue",
                    "odeon",
                ],
            }
        ],
    },
    {
        "category": "Transport",
        "subcategory": "Public Transport",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "trainline",
                    "Transport for London",
                    "tfl",
                    "tube",
                    "First West of England",
                    "London Overground",
                ],
            },
        ],
    },
    {
        "category": "Transport",
        "subcategory": "Taxis",
        "conditions": [
            {"column": "Name", "contains": ["uber", "taxi"]},
        ],
    },
    {
        "category": "Transport",
        "subcategory": "Taxis",
        "conditions": [
            {"column": "Notes and #tags", "contains": ["uber", "taxi"]},
        ],
    },
    {
        "category": "Transport",
        "subcategory": "E-Scooters & Bikes",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "forest",
                    "Lime",
                    "Voi UK",
                ],
            },
        ],
    },
    {
        "category": "Transport",
        "subcategory": "Petrol",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "shell",
                    "petrol",
                ],
            },
        ],
    },
    {
        "category": "Transport",
        "subcategory": "Parking",
        "conditions": [
            {"column": "Name", "contains": ["parking", "MiPermit", "RingGo"]},
        ],
    },
    # Bills & Utilities
    {
        "category": "Bills",
        "subcategory": "Utilities",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "British Gas",
                    "Thames Water",
                    "EDF",
                    "Octopus Energy",
                    "E.ON",
                    "Scottish Power",
                    "OVO Energy",
                    "Utilita",
                ],
            }
        ],
    },
    {
        "category": "Bills",
        "subcategory": "Internet & Mobile",
        "conditions": [
            {
                "column": "Name",
                "contains": [
                    "EE",
                    "Vodafone",
                    "Three",
                    "O2",
                    "giffgaff",
                    "Sky",
                    "BT",
                    "Virgin Media",
                    "TalkTalk",
                ],
            }
        ],
    },
]
