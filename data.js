// VA Schools Data - JavaScript Module
// This file contains the comprehensive VA overseas schools data
// It serves as a fallback for local development when fetch() might not work due to CORS

const VA_SCHOOLS_DATA = {
  "data_overview": {
    "total_records": 51,
    "countries_represented": 10,
    "data_source": "VA Comparison Tool or Sample Data"
  },
  "overseas_analysis": {
    "total_schools": 51,
    "countries": {
      "United Kingdom": 8,
      "Germany": 5,
      "France": 5,
      "Japan": 5,
      "Australia": 5,
      "Canada": 5,
      "Spain": 5,
      "Italy": 5,
      "Switzerland": 4,
      "Netherlands": 4
    },
    "cities": {
      "London": 4,
      "Tokyo": 3,
      "Barcelona": 2,
      "Geneva": 2,
      "Toronto": 2,
      "Paris": 2,
      "Rome": 2,
      "Madrid": 2,
      "Montreal": 2,
      "Munich": 1,
      "Berlin": 1,
      "Hamburg": 1,
      "Frankfurt": 1,
      "Cologne": 1,
      "Marseille": 1,
      "Lyon": 1,
      "Nice": 1,
      "Osaka": 1,
      "Kyoto": 1,
      "Sydney": 1,
      "Melbourne": 1,
      "Brisbane": 1,
      "Perth": 1,
      "Adelaide": 1,
      "Vancouver": 1,
      "Calgary": 1,
      "Ottawa": 1,
      "Seville": 1,
      "Bilbao": 1,
      "Granada": 1,
      "Naples": 1,
      "Milan": 1,
      "Valencia": 1,
      "Florence": 1,
      "Venice": 1,
      "Zurich": 1,
      "Basel": 1,
      "Amsterdam": 1,
      "Rotterdam": 1,
      "The Hague": 1,
      "Maastricht": 1
    },
    "school_types": {
      "Private": 33,
      "Public": 18
    },
    "schools_list": [
      {
        "INSTITUTION": "University College London",
        "CITY": "London",
        "COUNTRY": "United Kingdom",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "University of Edinburgh",
        "CITY": "Edinburgh",
        "COUNTRY": "United Kingdom",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Imperial College London",
        "CITY": "London",
        "COUNTRY": "United Kingdom",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "King's College London",
        "CITY": "London",
        "COUNTRY": "United Kingdom",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "University of Manchester",
        "CITY": "Manchester",
        "COUNTRY": "United Kingdom",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "London School of Economics",
        "CITY": "London",
        "COUNTRY": "United Kingdom",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "University of Cambridge",
        "CITY": "Cambridge",
        "COUNTRY": "United Kingdom",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Oxford",
        "CITY": "Oxford",
        "COUNTRY": "United Kingdom",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Technical University of Munich",
        "CITY": "Munich",
        "COUNTRY": "Germany",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Humboldt University of Berlin",
        "CITY": "Berlin",
        "COUNTRY": "Germany",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Hamburg",
        "CITY": "Hamburg",
        "COUNTRY": "Germany",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Goethe University Frankfurt",
        "CITY": "Frankfurt",
        "COUNTRY": "Germany",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Cologne",
        "CITY": "Cologne",
        "COUNTRY": "Germany",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Sorbonne University",
        "CITY": "Paris",
        "COUNTRY": "France",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "École Normale Supérieure",
        "CITY": "Paris",
        "COUNTRY": "France",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Aix-Marseille University",
        "CITY": "Marseille",
        "COUNTRY": "France",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Lyon",
        "CITY": "Lyon",
        "COUNTRY": "France",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Nice Sophia Antipolis",
        "CITY": "Nice",
        "COUNTRY": "France",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Tokyo",
        "CITY": "Tokyo",
        "COUNTRY": "Japan",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Waseda University",
        "CITY": "Tokyo",
        "COUNTRY": "Japan",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "Keio University",
        "CITY": "Tokyo",
        "COUNTRY": "Japan",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "Osaka University",
        "CITY": "Osaka",
        "COUNTRY": "Japan",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Kyoto University",
        "CITY": "Kyoto",
        "COUNTRY": "Japan",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Sydney",
        "CITY": "Sydney",
        "COUNTRY": "Australia",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Melbourne",
        "CITY": "Melbourne",
        "COUNTRY": "Australia",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Queensland",
        "CITY": "Brisbane",
        "COUNTRY": "Australia",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Western Australia",
        "CITY": "Perth",
        "COUNTRY": "Australia",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Adelaide",
        "CITY": "Adelaide",
        "COUNTRY": "Australia",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Toronto",
        "CITY": "Toronto",
        "COUNTRY": "Canada",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "McGill University",
        "CITY": "Montreal",
        "COUNTRY": "Canada",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "University of British Columbia",
        "CITY": "Vancouver",
        "COUNTRY": "Canada",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Calgary",
        "CITY": "Calgary",
        "COUNTRY": "Canada",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Carleton University",
        "CITY": "Ottawa",
        "COUNTRY": "Canada",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Barcelona",
        "CITY": "Barcelona",
        "COUNTRY": "Spain",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Pompeu Fabra University",
        "CITY": "Barcelona",
        "COUNTRY": "Spain",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Complutense University of Madrid",
        "CITY": "Madrid",
        "COUNTRY": "Spain",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Autonomous University of Madrid",
        "CITY": "Madrid",
        "COUNTRY": "Spain",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Seville",
        "CITY": "Seville",
        "COUNTRY": "Spain",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Sapienza University of Rome",
        "CITY": "Rome",
        "COUNTRY": "Italy",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Rome Tor Vergata",
        "CITY": "Rome",
        "COUNTRY": "Italy",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Naples Federico II",
        "CITY": "Naples",
        "COUNTRY": "Italy",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Bocconi University",
        "CITY": "Milan",
        "COUNTRY": "Italy",
        "TYPE": "Private"
      },
      {
        "INSTITUTION": "University of Florence",
        "CITY": "Florence",
        "COUNTRY": "Italy",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "ETH Zurich",
        "CITY": "Zurich",
        "COUNTRY": "Switzerland",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Zurich",
        "CITY": "Zurich",
        "COUNTRY": "Switzerland",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Geneva",
        "CITY": "Geneva",
        "COUNTRY": "Switzerland",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Basel",
        "CITY": "Basel",
        "COUNTRY": "Switzerland",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "University of Amsterdam",
        "CITY": "Amsterdam",
        "COUNTRY": "Netherlands",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Erasmus University Rotterdam",
        "CITY": "Rotterdam",
        "COUNTRY": "Netherlands",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Leiden University",
        "CITY": "The Hague",
        "COUNTRY": "Netherlands",
        "TYPE": "Public"
      },
      {
        "INSTITUTION": "Maastricht University",
        "CITY": "Maastricht",
        "COUNTRY": "Netherlands",
        "TYPE": "Public"
      }
    ]
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VA_SCHOOLS_DATA;
}
