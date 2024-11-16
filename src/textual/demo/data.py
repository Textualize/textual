import json

COUNTRIES = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Democratic Republic of the Congo",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "East Timor",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Ivory Coast",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Micronesia",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Korea",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Korea",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Vatican City",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Zambia",
    "Zimbabwe",
]
# Sort by length for auto-complete
COUNTRIES.sort(key=str.__len__)

# Thanks, Claude
MOVIES = """\
Date,Title,Genre,Director,Box Office (millions),Rating,Runtime (min)
1980-01-18,The Fog,Horror,John Carpenter,21,R,89
1980-02-15,Coal Miner's Daughter,Biography,Michael Apted,67,PG,124
1980-03-07,Little Miss Marker,Comedy,Walter Bernstein,12,PG,103
1980-04-11,The Long Riders,Western,Walter Hill,15,R,100
1980-05-21,The Empire Strikes Back,Sci-Fi,Irvin Kershner,538,PG,124
1980-06-13,The Blues Brothers,Comedy,John Landis,115,R,133
1980-07-02,Airplane!,Comedy,Jim Abrahams,83,PG,88
1980-08-01,Caddyshack,Comedy,Harold Ramis,39,R,98
1980-09-19,The Big Red One,War,Samuel Fuller,24,PG,113
1980-10-10,Private Benjamin,Comedy,Howard Zieff,69,R,109
1980-11-07,The Stunt Man,Action,Richard Rush,7,R,131
1980-12-19,Nine to Five,Comedy,Colin Higgins,103,PG,109
1981-01-23,Scanners,Horror,David Cronenberg,14,R,103
1981-02-20,The Final Conflict,Horror,Graham Baker,20,R,108
1981-03-20,Raiders of the Lost Ark,Action,Steven Spielberg,389,PG,115
1981-04-10,Excalibur,Fantasy,John Boorman,35,R,140
1981-05-22,Outland,Sci-Fi,Peter Hyams,17,R,109
1981-06-19,Superman II,Action,Richard Lester,108,PG,127
1981-07-17,Escape from New York,Sci-Fi,John Carpenter,25,R,99
1981-08-07,An American Werewolf in London,Horror,John Landis,30,R,97
1981-09-25,Continental Divide,Romance,Michael Apted,15,PG,103
1981-10-16,True Confessions,Drama,Ulu Grosbard,12,R,108
1981-11-20,Time Bandits,Fantasy,Terry Gilliam,42,PG,116
1981-12-04,Rollover,Drama,Alan J. Pakula,11,R,116
1982-01-15,The Beast Within,Horror,Philippe Mora,7,R,98
1982-02-12,Quest for Fire,Adventure,Jean-Jacques Annaud,20,R,100
1982-03-19,Porky's,Comedy,Bob Clark,105,R,94
1982-04-16,The Sword and the Sorcerer,Fantasy,Albert Pyun,39,R,99
1982-05-14,Conan the Barbarian,Fantasy,John Milius,68,R,129
1982-06-04,Star Trek II: The Wrath of Khan,Sci-Fi,Nicholas Meyer,97,PG,113
1982-06-11,E.T. the Extra-Terrestrial,Sci-Fi,Steven Spielberg,792,PG,115
1982-06-25,Blade Runner,Sci-Fi,Ridley Scott,33,R,117
1982-07-16,The World According to Garp,Comedy-Drama,George Roy Hill,29,R,136
1982-08-13,Fast Times at Ridgemont High,Comedy,Amy Heckerling,27,R,90
1982-09-17,The Challenge,Action,John Frankenheimer,9,R,108
1982-10-22,First Blood,Action,Ted Kotcheff,47,R,93
1982-11-12,The Man from Snowy River,Western,George Miller,20,PG,102
1982-12-08,48 Hrs.,Action,Walter Hill,79,R,96
1983-01-21,The Entity,Horror,Sidney J. Furie,13,R,125
1983-02-18,The Year of Living Dangerously,Drama,Peter Weir,10,PG,115
1983-03-25,The Outsiders,Drama,Francis Ford Coppola,25,PG,91
1983-04-22,Something Wicked This Way Comes,Horror,Jack Clayton,5,PG,95
1983-05-25,Return of the Jedi,Sci-Fi,Richard Marquand,475,PG,131
1983-06-17,Superman III,Action,Richard Lester,60,PG,125
1983-07-15,Class,Comedy,Lewis John Carlino,21,R,98
1983-08-19,Curse of the Pink Panther,Comedy,Blake Edwards,9,PG,109
1983-09-23,The Big Chill,Drama,Lawrence Kasdan,56,R,105
1983-10-07,The Right Stuff,Drama,Philip Kaufman,21,PG,193
1983-11-04,Deal of the Century,Comedy,William Friedkin,10,PG,99
1983-12-09,Scarface,Crime,Brian De Palma,65,R,170
1984-01-13,Terms of Endearment,Drama,James L. Brooks,108,PG,132
1984-02-17,Unfaithfully Yours,Comedy,Howard Zieff,12,PG,96
1984-03-16,Splash,Romance,Ron Howard,69,PG,111
1984-04-13,Friday the 13th: The Final Chapter,Horror,Joseph Zito,32,R,91
1984-05-04,Sixteen Candles,Comedy,John Hughes,23,PG,93
1984-06-08,Ghostbusters,Comedy,Ivan Reitman,295,PG,105
1984-07-06,The Last Starfighter,Sci-Fi,Nick Castle,28,PG,101
1984-08-10,Red Dawn,Action,John Milius,38,PG-13,114
1984-09-14,All of Me,Comedy,Carl Reiner,40,PG,93
1984-10-26,The Terminator,Sci-Fi,James Cameron,78,R,107
1984-11-16,Missing in Action,Action,Joseph Zito,22,R,101
1984-12-14,Dune,Sci-Fi,David Lynch,30,PG-13,137
1985-01-18,A Nightmare on Elm Street,Horror,Wes Craven,25,R,91
1985-02-15,The Breakfast Club,Drama,John Hughes,45,R,97
1985-03-29,Mask,Drama,Peter Bogdanovich,42,PG-13,120
1985-04-26,Code of Silence,Action,Andrew Davis,20,R,101
1985-05-22,Rambo: First Blood Part II,Action,George P. Cosmatos,150,R,96
1985-06-07,The Goonies,Adventure,Richard Donner,61,PG,114
1985-07-03,Back to the Future,Sci-Fi,Robert Zemeckis,381,PG,116
1985-08-16,Year of the Dragon,Crime,Michael Cimino,18,R,134
1985-09-20,Invasion U.S.A.,Action,Joseph Zito,17,R,107
1985-10-18,Silver Bullet,Horror,Daniel Attias,12,R,95
1985-11-22,Rocky IV,Drama,Sylvester Stallone,127,PG,91
1985-12-20,The Color Purple,Drama,Steven Spielberg,142,PG-13,154
1986-01-17,Iron Eagle,Action,Sidney J. Furie,24,PG-13,117
1986-02-21,Crossroads,Drama,Walter Hill,5,R,99
1986-03-21,Highlander,Fantasy,Russell Mulcahy,12,R,116
1986-04-18,Legend,Fantasy,Ridley Scott,15,PG,89
1986-05-16,Top Gun,Action,Tony Scott,357,PG,110
1986-06-27,Running Scared,Action,Peter Hyams,38,R,107
1986-07-18,Aliens,Sci-Fi,James Cameron,131,R,137
1986-08-08,Stand By Me,Drama,Rob Reiner,52,R,89
1986-09-19,Blue Velvet,Mystery,David Lynch,8,R,120
1986-10-24,The Name of the Rose,Mystery,Jean-Jacques Annaud,7,R,130
1986-11-21,An American Tail,Animation,Don Bluth,47,G,80
1986-12-19,Star Trek IV: The Voyage Home,Sci-Fi,Leonard Nimoy,109,PG,119
1987-01-23,Critical Condition,Comedy,Michael Apted,19,R,98
1987-02-20,Death Before Dishonor,Action,Terry Leonard,3,R,91
1987-03-13,Lethal Weapon,Action,Richard Donner,65,R,110
1987-04-10,Project X,Drama,Jonathan Kaplan,28,PG,108
1987-05-22,Beverly Hills Cop II,Action,Tony Scott,276,R,100
1987-06-19,Predator,Sci-Fi,John McTiernan,98,R,107
1987-07-17,RoboCop,Action,Paul Verhoeven,53,R,102
1987-08-14,No Way Out,Thriller,Roger Donaldson,35,R,114
1987-09-18,Fatal Beauty,Action,Tom Holland,12,R,104
1987-10-23,Fatal Attraction,Thriller,Adrian Lyne,320,R,119
1987-11-13,Running Man,Sci-Fi,Paul Michael Glaser,38,R,101
1987-12-18,Wall Street,Drama,Oliver Stone,43,R,126
1988-01-15,Return of the Living Dead Part II,Horror,Ken Wiederhorn,9,R,89
1988-02-12,Action Jackson,Action,Craig R. Baxley,20,R,96
1988-03-18,D.O.A.,Thriller,Rocky Morton,12,R,96
1988-04-29,Colors,Crime,Dennis Hopper,46,R,120
1988-05-20,Willow,Fantasy,Ron Howard,57,PG,126
1988-06-21,Big,Comedy,Penny Marshall,151,PG,104
1988-07-15,Die Hard,Action,John McTiernan,140,R,132
1988-08-05,Young Guns,Western,Christopher Cain,45,R,107
1988-09-16,Moon Over Parador,Comedy,Paul Mazursky,11,PG-13,103
1988-10-21,Halloween 4,Horror,Dwight H. Little,17,R,88
1988-11-11,Child's Play,Horror,Tom Holland,33,R,87
1988-12-21,Rain Man,Drama,Barry Levinson,172,R,133
1989-01-13,Deep Star Six,Sci-Fi,Sean S. Cunningham,8,R,99
1989-02-17,Bill & Ted's Excellent Adventure,Comedy,Stephen Herek,40,PG,90
1989-03-24,Leviathan,Sci-Fi,George P. Cosmatos,15,R,98
1989-04-14,Major League,Comedy,David S. Ward,49,R,107
1989-05-24,Indiana Jones and the Last Crusade,Action,Steven Spielberg,474,PG-13,127
1989-06-23,Batman,Action,Tim Burton,411,PG-13,126
1989-07-07,Lethal Weapon 2,Action,Richard Donner,227,R,114
1989-08-11,A Nightmare on Elm Street 5,Horror,Stephen Hopkins,22,R,89
1989-09-22,Black Rain,Action,Ridley Scott,46,R,125
1989-10-20,Look Who's Talking,Comedy,Amy Heckerling,140,PG-13,93
1989-11-17,All Dogs Go to Heaven,Animation,Don Bluth,27,G,84
1989-12-20,Tango & Cash,Action,Andrei Konchalovsky,63,R,104
"""

MOVIES_JSON = """{
  "decades": {
    "1980s": {
      "genres": {
        "action": {
          "franchises": {
            "terminator": {
              "name": "The Terminator",
              "movies": [
                {
                  "title": "The Terminator",
                  "year": 1984,
                  "director": "James Cameron",
                  "stars": ["Arnold Schwarzenegger", "Linda Hamilton", "Michael Biehn"],
                  "boxOffice": 78371200,
                  "quotes": ["I'll be back", "Come with me if you want to live"]
                }
              ]
            },
            "rambo": {
              "name": "Rambo",
              "movies": [
                {
                  "title": "First Blood",
                  "year": 1982,
                  "director": "Ted Kotcheff",
                  "stars": ["Sylvester Stallone", "Richard Crenna", "Brian Dennehy"],
                  "boxOffice": 47212904
                },
                {
                  "title": "Rambo: First Blood Part II",
                  "year": 1985,
                  "director": "George P. Cosmatos",
                  "stars": ["Sylvester Stallone", "Richard Crenna", "Charles Napier"],
                  "boxOffice": 150415432
                }
              ]
            }
          },
          "standalone_classics": {
            "die_hard": {
              "title": "Die Hard",
              "year": 1988,
              "director": "John McTiernan",
              "stars": ["Bruce Willis", "Alan Rickman", "Reginald VelJohnson"],
              "boxOffice": 140700000,
              "location": "Nakatomi Plaza",
              "quotes": ["Yippee-ki-yay, motherf***er"]
            },
            "predator": {
              "title": "Predator",
              "year": 1987,
              "director": "John McTiernan",
              "stars": ["Arnold Schwarzenegger", "Carl Weathers", "Jesse Ventura"],
              "boxOffice": 98267558,
              "location": "Val Verde jungle",
              "quotes": ["Get to the chopper!"]
            }
          },
          "common_themes": [
            "Cold War politics",
            "One man army",
            "Revenge plots",
            "Military operations",
            "Law enforcement"
          ],
          "typical_elements": {
            "weapons": ["M60 machine gun", "Desert Eagle", "Explosive arrows"],
            "vehicles": ["Military helicopters", "Muscle cars", "Tanks"],
            "locations": ["Urban jungle", "Actual jungle", "Industrial facilities"]
          }
        }
      }
    }
  },
  "metadata": {
    "total_movies": 4,
    "date_compiled": "2024",
    "box_office_total": 467654094,
    "most_frequent_actor": "Arnold Schwarzenegger",
    "most_frequent_director": "John McTiernan"
  }
}"""

MOVIES_TREE = json.loads(MOVIES_JSON)

DUNE_BIOS = [
    {
        "name": "Paul Atreides",
        "description": "Heir to House Atreides who becomes the Fremen messiah Muad'Dib. Born with extraordinary mental abilities due to Bene Gesserit breeding program.",
    },
    {
        "name": "Lady Jessica",
        "description": "Bene Gesserit concubine to Duke Leto and mother of Paul. Defied her order by bearing a son instead of a daughter, disrupting centuries of careful breeding.",
    },
    {
        "name": "Baron Vladimir Harkonnen",
        "description": "Cruel and corpulent leader of House Harkonnen, sworn enemy of House Atreides. Known for his cunning and brutality in pursuing power.",
    },
    {
        "name": "Leto Atreides",
        "description": "Noble Duke and father of Paul, known for his honor and just rule. Accepts governorship of Arrakis despite knowing it's likely a trap.",
    },
    {
        "name": "Stilgar",
        "description": "Leader of the Fremen Sietch Tabr, becomes a loyal supporter of Paul. Skilled warrior who helps train Paul in Fremen ways.",
    },
    {
        "name": "Chani",
        "description": "Fremen warrior and daughter of planetologist Liet-Kynes. Becomes Paul's concubine and true love after appearing in his prescient visions.",
    },
    {
        "name": "Thufir Hawat",
        "description": "Mentat and Master of Assassins for House Atreides. Serves three generations of Atreides with his superhuman computational skills.",
    },
    {
        "name": "Duncan Idaho",
        "description": "Swordmaster of the Ginaz, loyal to House Atreides. Known for his exceptional fighting skills and sacrifice to save Paul and Jessica.",
    },
    {
        "name": "Gurney Halleck",
        "description": "Warrior-troubadour of House Atreides, skilled with sword and baliset. Serves as Paul's weapons teacher and loyal friend.",
    },
    {
        "name": "Dr. Yueh",
        "description": "Suk doctor conditioned against taking human life, but betrays House Atreides after the Harkonnens torture his wife. Imperial Conditioning broken.",
    },
]
