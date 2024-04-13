# LCC
Repository for the LCC, League Community Cup, data processing scripts. 

## Prerequisites
### Riot API
To use the fetch, you will need to create a Riot account and generate a riot API key.  Learn more by visiting https://developer.riotgames.com/docs/portal.  

Create a ```.env``` file and add
```
RIOT_API_KEY='your-key-here'
```

### Dependency Installation

1. Activate your virtual environment
2. Run ```pip install -r requirements.txt```

## Adding Match Data

The script will pull match IDs from the ```tournaments``` directory.  To create a new tournament, simply add a ```.txt``` file to that directory and list the match IDs (one per line).  Example match IDs can be found below

```
4945781121
4941568096
```

If a tournament is not entered on the first input field, it will default to LCC_Season_2

## Results
Once the program is run, an ```xlsx``` file containing the match and individual player stats will be available in the ```results``` directory labeled ```Stats_Report_{TODAYS DATE}```.  A JSON file will also be created for each match input for additional programmatic work.  I left some example files from 2024-04-12 in the ```results``` directory