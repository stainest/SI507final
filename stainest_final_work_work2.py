from bs4 import BeautifulSoup
import requests
import json
import sqlite3

BASE_URL = 'https://www.transfermarkt.us'
SEARCH_PATH = '/schnellsuche/ergebnis/schnellsuche?query='
TEAM_PATH = '/saison_id/2020/plus/1'
PLAYER_PATH = '/saison/ges/plus/1#gesamt'
#headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 13729.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.130 Safari/537.36"}
#response = requests.get('https://www.transfermarkt.us', headers={'User-Agent': 'Custom'}, timeout=100)
#print(response.text)

def grab_search_request():
    '''Takes input to determine next step in the program.
    Exit to leave
    Remove to remove players from analytical pool
    Or a search function sent to transfermarkt.us where the html is grabbed

    Parameters:
    None

    Returns:
    Soup: A beautiful soup object of the scraped html page.
    Can also return 'exit' or 'remove' strings
    '''
    userinput = input('Input a search term to find players for analysis, type "remove" to remove players for analysis, type "analysis" to analyze selected players, or type "exit": ')
    if userinput.lower() == 'exit':
        return 'exit'
    elif userinput.lower() == 'remove':
        return 'remove'
    elif userinput.lower() == 'analysis':
        return 'analysis'
    else:
        userinputstrip = userinput.strip().replace(' ','+')
        searchurl = BASE_URL + SEARCH_PATH + userinputstrip
        print(searchurl)
        response = requests.get(searchurl, headers={'User-Agent': 'Custom'}, timeout=100)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

def get_players_from_div(playerdiv, printlistplayers):
    '''Takes an html <div> with football players and appends them to a list.

    Parameters:
    playerdiv: a soup object of a <div> element containing player data from transfermarkt
    printlistplayers: A list of lists of player information

    Returns:
    None
    '''
    playertbody = playerdiv.find('tbody')
    trlist = playertbody.find_all('tr', class_='even')
    tr2list = playertbody.find_all('tr', class_='odd')
    for tr in tr2list:
        trlist.append(tr)
    for i in range(len(trlist)):
        namelink = trlist[i].find('a', class_="spielprofil_tooltip")
        if namelink is not None:
            name = namelink.string
            site = namelink['href']
        else:
            name = "No Name"
            site = "No Site"
        teamlink = trlist[i].find('a', class_="vereinprofil_tooltip")
        if teamlink is not None:
            team = teamlink.string
        else:
            team = 'No Team'
        thislist = [i+1, name, team, site]
        printlistplayers.append(thislist)

def get_teams_from_div(teamdiv, printlistteams):
    '''Takes an html <div> with football teams and appends them to a list.

    Parameters:
    teamdiv: a soup object of a <div> element containing team data from transfermarkt
    printlistplayers: A list of lists of team information

    Returns:
    None
    '''
    teamtbody = teamdiv.find('tbody')
    trteamlist = teamtbody.find_all('tr', class_='even')
    tr2teamlist = teamtbody.find_all('tr', class_='odd')
    for tr in tr2teamlist:
        trteamlist.append(tr)
    for i in range(len(trteamlist)):
        teamtable = trteamlist[i].find('table')
        teamanchor = teamtable.find('a')
        team = teamanchor.string
        site = teamanchor['href']
        thisteamlist = [i+1, team, site]
        printlistteams.append(thisteamlist)

def print_results(printlistplayers, printlistteams):
    '''Prints results from two lists of lists in a readable format,
    separated by players and teams

    Parameters:
    printlistplayers: A list of lists of player information
    printlistteams: A list of lists of team information

    Returns:
    None
    '''
    print("\nSEARCH RESULTS\n")
    if (printlistplayers == [] and printlistteams == []):
        print('----------------------------')
        print('NO SEARCH RESULTS')
        print('----------------------------')
    else:
        print('Players\n')
        if printlistplayers == []:
            print('No Players Found')
        else:
            for item in printlistplayers:
                print(f'{item[0]}. {item[1]}, {item[2]}')
        print('\nTeams\n')
        if printlistteams == []:
            print('No Teams Found')
        else:
            for item in printlistteams:
                print(f'{item[0]}. {item[1]}')

def pick_player_or_team(printlistplayers, printlistteams):
    '''Takes user input to glean from list of players and teams the ones
    that the user wants to be included in visual analysis. It does this
    by asking the player if they want to add a player (and then prompts
    for the player), add a team (then prompting for the team), if they
    are done (returns a list of two lists, one of the desired players
    and one of the desired teams), or if they want to exit (ignores
    everything they've done so far)

    Parameters:
    printlistplayers: A list of lists of player information
    printlistteams: A list of lists of team information

    Returns:
    returnlist: a list of lists, one of players to add to analysis and one of teams to add (might not return anything)
    '''
    playeraddlist = []
    teamaddlist = []
    while True:
        print('\nIf you would like to add a player to the analysis, type "player"')
        print('If you would like to add all players of a team, type "team"')
        print('If you have chosen all that you want from this search, type "done"')
        userinput = input('Or type "exit", which will not add any of these search terms: ')
        if userinput.lower() == 'exit':
            return [[],[]]
        elif userinput.lower() == 'done':
            returnlist = [playeraddlist, teamaddlist]
            return returnlist
        elif userinput.lower() == 'player':
            if printlistplayers == []:
                print('No Players to Add')
            else:
                print('\n')
                for item in printlistplayers:
                    print(f'{item[0]}. {item[1]}, {item[2]}')
                playeradd = input('Type the number next to the player you would like to add: ')
                if not playeradd.isnumeric():
                    print('Please type the number of the player, not the name')
                else:
                    try:
                        x = int(playeradd) - 1
                        xo = 0
                        for i in range(len(playeraddlist)):
                            if playeraddlist[i][0] == x + 1:
                                xo += 2
                                print('Player Already Selected')
                            else:
                                pass
                        if xo >= 1:
                            pass
                        else:
                            playeraddlist.append(printlistplayers[x])
                    except:
                        print('Error: Number out of range')
        elif userinput.lower() == 'team':
            if printlistteams == []:
                print('No Teams to Add')
            else:
                print('\n')
                for item in printlistteams:
                    print(f'{item[0]}. {item[1]}')
                teamadd = input('Please type the number next to the team whose players you would like to add: ')
                if not teamadd.isnumeric():
                    print('Please type the number of the team, not the name')
                else:
                    try:
                        x = int(teamadd) - 1
                        xo = 0
                        for i in range(len(teamaddlist)):
                            if teamaddlist[i][0] == x + 1:
                                xo += 2
                                print('Team Already Selected')
                            else:
                                pass
                        if xo >= 1:
                            pass
                        else:
                            teamaddlist.append(printlistteams[x])
                    except:
                        print('Error: Number out of range')
        else:
            print('Error: Unrecognized Input. Please type "player", "team", "done", or "exit"')

def prepare_players_for_analysis(addlistslist, playeranalysis):
    if playeranalysis == []:
        for player in addlistslist[0]:
            playeranalysis.append(player)
    else:
        for player in addlistslist[0]:
            nogo = 0
            for item in playeranalysis:
                if player[3] == item[3]:
                    nogo += 2
                else:
                    pass
            if nogo >= 1:
                pass
            else:
                playeranalysis.append(player)

def prepare_teams_for_analysis(addlistslist, teamanalysis):
    if teamanalysis == []:
        for team in addlistslist[1]:
            teamanalysis.append(team)
    else:
        for team in addlistslist[1]:
            nogo = 0
            for item in teamanalysis:
                if team[2] == item[2]:
                    nogo += 2
                else:
                    pass
            if nogo >= 1:
                pass
            else:
                teamanalysis.append(team)

def remove_players_for_analysis(playeranalysis, teamanalysis):
    while True:
        if playeranalysis == []:
            print("There are no players to remove!!")
            break
        else:
            print('\nPLAYERS\n')
            for i in range(len(playeranalysis)):
                print(f'{i+1}. {playeranalysis[i][1]}, {playeranalysis[i][2]}')
            print('\nTEAMs\n')
            if teamanalysis == []:
                print('No Teams to Remove')
            else:
                for i in range(len(teamanalysis)):
                    print(f'{i+1}. {teamanalysis[i][1]}')
                print("----------------------------")
                print("CAUTION: IF YOU DO NOT REMOVE A TEAM FROM ANALYSIS, ALL ITS PLAYERS WILL STILL BE INCLUDED!")
                print("----------------------------")
            userinput = input('Would you like to remove a player or a team? Type "player", "team", or "exit": ')
            if userinput.lower() == 'exit':
                break
            elif userinput.lower() == 'player':
                for i in range(len(playeranalysis)):
                    print(f'{i+1}. {playeranalysis[i][1]}, {playeranalysis[i][2]}')
                playerinput = input('Please input the number next to the player you wish to remove, or "exit": ')
                if playerinput.lower() == 'exit':
                    break
                elif not playerinput.isnumeric():
                    print('Error: Not Integer. Please input the number next to the desired player')
                else:
                    try:
                        x = int(playerinput)
                        playeranalysis.pop(x-1)
                    except:
                        print('Error: Number out of range. Select a number next to a visible player')
            elif userinput.lower() == 'team':
                for i in range(len(teamanalysis)):
                    print(f'{i+1}. {teamanalysis[i][1]}')
                playerinput = input('Please input the number next to the team you wish to remove, or "exit": ')
                if playerinput.lower() == 'exit':
                    break
                elif not playerinput.isnumeric():
                    print('Error: Not Integer. Please input the number next to the desired player')
                else:
                    try:
                        x = int(playerinput)
                        teamtoremove = teamanalysis[x-1][1]
                        print(teamtoremove)
                        teamanalysis.pop(x-1)
                        playeranalysis = [x for x in playeranalysis if not x[2].lower() == teamtoremove.lower()]
                    except:
                        print('Error: Number out of range. Select a number next to a visible team')
            else:
                print('Error: Unrecognized Input. Please type "player", "team", or "exit"')

def get_team_players(team, teamsite):
    teamsite2 = teamsite.replace('startseite', 'kader')
    searchsite = BASE_URL + teamsite2 + TEAM_PATH
    response = requests.get(searchsite, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'html.parser')
    playerdivbox = soup.find('div', id='yw1')
    playerstr = playerdivbox.find_all('tr', class_="odd")
    playerstr2 = playerdivbox.find_all('tr', class_="even")
    for item in playerstr2:
        playerstr.append(item)
    returnlist = []
    for player in playerstr:
        playeranchor = player.find('a', class_="spielprofil_tooltip")
        if playeranchor is not None:
            name = playeranchor.string
            site = playeranchor['href']
            thisplayerlist = [0, name, team, site]
            returnlist.append(thisplayerlist)
        else:
            pass
    return returnlist

def get_player_stats(player):
    '''Takes a player list representation and uses the player path to go to
    Transfermarkt to get player data. Turns that data into a dictionary

    Parameters:
    player: a list representing a player, the fourth item in which is the player path

    Returns:
    returndict: a returned dictionary containing player data from Transfermarkt
    '''
    playerpath = player[3].replace('profil', 'leistungsdaten')
    playersite = BASE_URL + playerpath + PLAYER_PATH
    response = requests.get(playersite, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'html.parser')
    #Player Info
    infodiv = soup.find('div', class_='dataContent')
    infosections = infodiv.find_all('div', class_='dataDaten')
    #Player age
    agep = infosections[0].find_all('p')
    ageindicator = 0
    for p in agep:
        pspans = p.find_all('span')
        if pspans[0].string == 'Date of birth/Age:':
            agetext = pspans[1].string.strip()
            age = int(agetext[-3:-1])
            ageindicator += 2
        else:
            pass
    if ageindicator >= 1:
        pass
    else:
        age = None
    #Player Height
    heightposp = infosections[1].find_all('p')
    heightindicator = 0
    for p in heightposp:
        pspans = p.find_all('span')
        if pspans[0].string == "Height:":
            heighttext = pspans[1].string.strip()
            heightt = heighttext[:4].strip()
            height = float(heightt.replace(',',''))
            heightindicator += 2
        else:
            pass
    if heightindicator >= 1:
        pass
    else:
        height = None
    #Player Position
    posindicator = 0
    for p in heightposp:
        pspans = p.find_all('span')
        if pspans[0].string == 'Position:':
            position = pspans[1].string.strip()
            posindicator += 2
        else:
            pass
    if posindicator >= 1:
        pass
    else:
        position = None
    #Player Monetary Value
    value = soup.find('div', class_='dataMarktwert')
    if value is not None:
        valueanchor = value.find('a')
        spans = valueanchor.find_all('span')
        if valueanchor is not None:
            valuetext = valueanchor.text[:10]
            worklist = []
            for character in valuetext:
                if character.isnumeric():
                    worklist.append(character)
                else:
                    worklist.append('')
            valuestring = (worklist[0] + worklist[1] + worklist[2] + worklist[3] + worklist[4] +
            worklist[5] + worklist[6] + worklist[7] +worklist[8] + worklist[9])
            valueint = int(valuestring)
            if spans[1].string == 'm':
                playervalue = valueint * 10000
            elif spans[1].string == 'Th.':
                playervalue = valueint * 1000
            else:
                playervalue = 0
        else:
            playervalue = 0
    else:
        playervalue = 0
    #Stats
    if position != 'Goalkeeper':
        footdiv = soup.find('tfoot')
        zentrierts = footdiv.find_all('td', class_='zentriert')
        zentriertslist = []
        for centered in zentrierts:
            zentriertslist.append(centered.string)
        for i in range(len(zentriertslist)):
            if zentriertslist[i] == '-':
                zentriertslist[i] = '0'
            else:
                pass
            zentriertslist[i] = int(zentriertslist[i])
        rechts = footdiv.find_all('td', class_='rechts')
        try:
            if rechts[1].string == '-':
                minpergoal = 0
            else:
                minpergoal = int(rechts[1].string.replace("'", "").replace(".", ""))
        except:
            minpergoal = 0
        try:
            if rechts[2].string == '-':
                totalminutes = 0
            else:
                totalminutes = int(rechts[2].string.replace("'", "").replace(".", ""))
        except:
            totalminutes = 0
        zentriertslist.append(0)
        zentriertslist.append(0)
    else:
        footdiv = soup.find('tfoot')
        zentrierts = footdiv.find_all('td', class_='zentriert')
        zentriertstobelist = []
        for centered in zentrierts:
            zentriertstobelist.append(centered.string)
        rechts = footdiv.find_all('td', class_='rechts')
        if rechts[1].string == '-':
            totalminutes = 0
        else:
            totalminutes = int(rechts[1].string.replace("'", "").replace(".", ""))
        minpergoal = 0
        zentriertslist = []
        zentriertslist.append(zentriertstobelist[0])#appearances
        zentriertslist.append(zentriertstobelist[1])#goals
        zentriertslist.append(0)#assists
        zentriertslist.append(zentriertstobelist[2])#own goals
        zentriertslist.append(zentriertstobelist[3])#subs on
        zentriertslist.append(zentriertstobelist[4])#subs off
        zentriertslist.append(zentriertstobelist[5])#yellows
        zentriertslist.append(zentriertstobelist[6])#second yellows
        zentriertslist.append(zentriertstobelist[7])#reds
        zentriertslist.append(0)#penaltygoals
        zentriertslist.append(zentriertstobelist[8])#goals conceded
        zentriertslist.append(zentriertstobelist[9])#clean sheets
        for i in range(len(zentriertslist)):
            if zentriertslist[i] == '-':
                zentriertslist[i] = '0'
            else:
                pass
            zentriertslist[i] = int(zentriertslist[i])
    returndict = {}
    returndict['name'] = player[1]
    returndict['team'] = player[2]
    returndict['site'] = player[3]
    returndict['position'] = position
    returndict['age'] = age
    returndict['height (cm)'] = height
    returndict['value ($)'] = playervalue
    returndict['appearances'] = zentriertslist[0]
    returndict['goals'] = zentriertslist[1]
    returndict['assists'] = zentriertslist[2]
    returndict['own goals'] = zentriertslist[3]
    returndict['substitutions on'] = zentriertslist[4]
    returndict['substitutions off'] = zentriertslist[5]
    returndict['yellow cards'] = zentriertslist[6]
    returndict['second yellows'] = zentriertslist[7]
    returndict['red cards'] = zentriertslist[8]
    returndict['penalty goals'] = zentriertslist[9]
    returndict['goals conceded'] = zentriertslist[10]
    returndict['clean sheets'] = zentriertslist[11]
    returndict['total minutes'] = totalminutes
    returndict['minutes per goal'] = minpergoal
    return returndict

def cache(playerdicts):
    '''Takes a list of dictionaries of players and caches the results by player

    Parameters:
    playerdicts: a list of player dictionaries

    Returns:
    None
    '''
    conn = sqlite3.connect("footballplayercache.sqlite")
    cur = conn.cursor()
    for pdict in playerdicts:
        cachelist = []
        for key, val in pdict.items():
            cachelist.append(val)
        insert_players = '''
            INSERT OR REPLACE INTO Players
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(insert_players, cachelist)
        conn.commit()
    conn.close()

def connect_to_cache():
    '''
    Connects to SQL database and creates players table

    Parameters:
    None

    Returns:
    None
    '''
    conn = sqlite3.connect("footballplayercache.sqlite")
    cur = conn.cursor()
    create_teams = '''
                CREATE TABLE IF NOT EXISTS "Players" (
                    "Name"  TEXT,
                    "Team"  TEXT,
                    "Site" TEXT PRIMARY KEY,
                    "Position"  TEXT,
                    "Age"  INTEGER,
                    "Height"  INTEGER,
                    "Value" INTEGER,
                    "Appearances"  INTEGER,
                    "Goals"  INTEGER,
                    "Assists"  INTEGER,
                    "Own Goals"  INTEGER,
                    "Subs On"  INTEGER,
                    "Subs Off"  INTEGER,
                    "Yellow Cards"  INTEGER,
                    "Second Yellows"  INTEGER,
                    "Red Cards"  INTEGER,
                    "Penalty Goals"  INTEGER,
                    "Goals Conceded" INTEGER,
                    "Clean Sheets" INTEGER,
                    "Total Minutes"  INTEGER,
                    "Minutes Per Goal"  INTEGER
                );
    '''
    cur.execute(create_teams)
    conn.commit()
    conn.close()

def take_from_cache(player):
    '''Takes a player, finds the associated website path, and uses that to get
    records from that player in the cache

    Parameters:
    player: a list representing a player, the fourth item in which is the player website path in Transfermarkt

    Returns:
    records: a list containing a tuple of the results returned from SQL
    '''
    conn = sqlite3.connect("footballplayercache.sqlite")
    cur = conn.cursor()
    check_in_cache = f'SELECT * FROM Players WHERE Site = "{player[3]}"'
    cur.execute(check_in_cache)
    records = cur.fetchall()
    return records

def turn_cache_into_dict(stats):
    '''Takes the list containing just the tuple that is returned from SQL
    and turns it into a dictionary

    Parameters:
    stats: A list containing a tuple of results from SQL request

    Returns:
    returndict: A dictionary made from SQL results
    '''
    returndict = {}
    returndict['name'] = stats[0][0]
    returndict['team'] = stats[0][1]
    returndict['site'] = stats[0][2]
    returndict['position'] = stats[0][3]
    returndict['age'] = stats[0][4]
    returndict['height (cm)'] = stats[0][5]
    returndict['value ($)'] = stats[0][6]
    returndict['appearances'] = stats[0][7]
    returndict['goals'] = stats[0][8]
    returndict['assists'] = stats[0][9]
    returndict['own goals'] = stats[0][10]
    returndict['substitutions on'] = stats[0][11]
    returndict['substitutions off'] = stats[0][12]
    returndict['yellow cards'] = stats[0][13]
    returndict['second yellows'] = stats[0][14]
    returndict['red cards'] = stats[0][15]
    returndict['penalty goals'] = stats[0][16]
    returndict['goals conceded'] = stats[0][17]
    returndict['clean sheets'] = stats[0][18]
    returndict['total minutes'] = stats[0][19]
    returndict['minutes per goal'] = stats[0][20]
    return returndict

def input_search_term():
    ''''''
    connect_to_cache()
    playeranalysis = []
    teamanalysis = []
    while True:
        soup = grab_search_request()
        if soup == 'exit':
            break
        elif soup == 'remove':
            remove_players_for_analysis(playeranalysis, teamanalysis)
        elif soup == 'analysis':
            if playeranalysis == []:
                print("Error: No Players to Analyze!")
            else:
                playerdicts = []
                for player in playeranalysis:
                    stats = take_from_cache(player)
                    if stats == []:
                        print('Collecting Data From Transfermarkt')
                        playerdict = get_player_stats(player)
                        playerdicts.append(playerdict)
                    else:
                        print('Collecting Data From Cache')
                        playerdict = turn_cache_into_dict(stats)
                        playerdicts.append(playerdict)
                cache(playerdicts)
        else:
            thedivs = soup.find_all('div', class_='row')
            newdivs = []
            printlistplayers = []
            printlistteams = []
            for div in thedivs:
                headdiv = div.find('div', class_='table-header')
                if headdiv is not None:
                    newdivs.append(div)
                else:
                    pass
            for div in newdivs:
                headdiv = div.find('div', class_='table-header')
                if headdiv is None:
                    pass
                elif 'players' in headdiv.string:
                    print('found a player div')
                    get_players_from_div(div, printlistplayers)
                elif 'lubs' in headdiv.string:
                    print('found a team div')
                    get_teams_from_div(div, printlistteams)
                else:
                    pass
            print_results(printlistplayers, printlistteams)
            addlistslist = pick_player_or_team(printlistplayers, printlistteams)
            prepare_players_for_analysis(addlistslist, playeranalysis)
            prepare_teams_for_analysis(addlistslist, teamanalysis)
            for team in teamanalysis:
                teamplayerslist = get_team_players(team[1], team[2])
                for player in teamplayerslist:
                    playeranalysis.append(player)




#gio = [0, 'Giovanni Lo Celso', 'Tottenham Hotspur', '/giovani-lo-celso/profil/spieler/348795']
#giodict = get_player_stats(gio)
#print(giodict)


input_search_term()
