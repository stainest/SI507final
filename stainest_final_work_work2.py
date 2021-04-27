from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import plotly.graph_objects as go

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
    userinput = input('\nInput a search term to find players for analysis, type "remove" to remove players for analysis, type "analysis" to analyze selected players, or type "exit": ')
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
    '''takes a list of lists of players and teams to add, and adds the players list
    to the list of players to be included in analysis

    Paramters:
    addlistslist: a list of two lists, one of players to be added to analysis and one of teams to be added
    playeranalysis: the list of players to be added to analysis

    Returns:
    N/A
    '''
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
    '''takes a list of lists of players and teams to add, and adds the teams list
    to the list of teams to be included in analysis

    Paramters:
    addlistslist: a list of two lists, one of players to be added to analysis and one of teams to be added
    teamanalysis: the list of teams to be added to analysis

    Returns:
    N/A
    '''
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
    '''Requests user input regarding the removal of players and teams
    to be removed from the analysis lists

    Parameters:
    playeranalysis: the list of players to be added to analysis
    teamanalysis: the list of teams to be added to analysis

    Returns:
    N/A
    '''
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
    '''Takes a team name and the website path associated with it to get the player
    lists that include player name, website path, and team, returned in a list
    of all of those players

    Parameters:
    team: The name of the team
    teamsite: the website path connected to that team

    Returns:
    returnlist: a list of the players from the requested team, their team,
    and their website path on Transfermarkt
    '''
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

def bar_graph_players(playerdicts, desiredstat):
    '''Takes a list of player dictionaries and a desired statistic that lines up with
    one of the dictionary keys and creates a bar graph of the players from the dictionary
    around that key

    Parameters:
    playerdicts: a list of player dictionaries
    desiredstat: the desired dictionary key

    Returns:
    N/A
    '''
    names = []
    data = []
    data2 = []
    for player in playerdicts:
        names.append(player['name'])
    if desiredstat.lower() == 'goals':
        for player in playerdicts:
            fieldgoals = player['goals'] - player['penalty goals']
            data.append(player['penalty goals'])
            data2.append(fieldgoals)
        fig = go.Figure(go.Bar(x=names, y=data, name='penalty goals'))
        fig.add_trace(go.Bar(x=names, y=data2, name='goals from open play'))
        fig.update_layout(barmode='stack')
        fig.show()
    elif desiredstat.lower() == 'chances':
        for player in playerdicts:
            data.append(player['goals'])
            data2.append(player['assists'])
        fig = go.Figure(go.Bar(x=names, y=data, name='goals'))
        fig.add_trace(go.Bar(x=names, y=data2, name='assists'))
        fig.update_layout(barmode='stack')
        fig.show()
    else:
        for player in playerdicts:
            data.append(player[desiredstat])
        bar_data = go.Bar(x=names, y=data)
        basic_layout = go.Layout(title=desiredstat)
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()

def scatter_graph(playerdicts, desiredstat1, desiredstat2):
    '''Takes a list of player dictionaries and two desired statistics that line up with
    dictionary keys and creates a scatter plot of the players from the dictionary
    around that key

    Parameters:
    playerdicts: a list of player dictionaries
    desiredstat1: one desired dictionary key
    desiredstat2: the second desired dictionary key

    Returns:
    N/A
    '''
    names = []
    data = []
    data2 = []
    for player in playerdicts:
        names.append(player['name'])
        data.append(player[desiredstat1])
        data2.append(player[desiredstat2])
    scatter_data = go.Scatter(
        x=data,
        y=data2,
        text=names,
        marker={'symbol':'diamond', 'size':20, 'color':'green'},
        mode='markers+text',
        textposition='top center')
    basic_layout = go.Layout(title=f'{desiredstat1} by {desiredstat2}')
    fig = go.Figure(data=scatter_data, layout=basic_layout)
    fig.show()

def team_bars(playerdicts, team):
    '''Takes a list of player dictionaries and a desired team and creates a bargraph
    of the players on the team. The values of the bar graph are determined by userinput
    across 5 possibilities: goals, discipline, goalie, value, and minutes. The first
    three are aggregate bar graphs, the latter two are normal bar graphs

    Parameters:
    playerdicts: a list of player dictionaries
    team: a string representation of a team name

    Returns:
    N/A
    '''
    analytype = input('What type of analysis? Type "goals", "discipline", "goalie", "value", or "minutes": ')
    if analytype.lower() == 'goals':
        fig = go.Figure()
        x = ['goals', 'assists', 'own goals']
        for player in playerdicts:
            if player['team'] == team:
                playerdata = []
                playerdata.append(player['goals'])
                playerdata.append(player['assists'])
                playerdata.append(player['own goals'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'discipline':
        fig = go.Figure()
        x = ['yellow cards', 'second yellows', 'red cards']
        for player in playerdicts:
            if player['team'] == team:
                playerdata = []
                playerdata.append(player['yellow cards'])
                playerdata.append(player['second yellows'])
                playerdata.append(player['red cards'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'goalie':
        fig = go.Figure()
        x = ['goals conceded', 'clean sheets']
        for player in playerdicts:
            if player['team'] == team:
                playerdata = []
                playerdata.append(player['goals conceded'])
                playerdata.append(player['clean sheets'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'value':
        names = []
        data = []
        for player in playerdicts:
            if player['team'] == team:
                data.append(player['value ($)'])
                names.append(player['name'])
            else:
                pass
        bar_data = go.Bar(x=names, y=data)
        basic_layout = go.Layout(title='Value ($)')
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()
    elif analytype.lower() == 'minutes':
        names = []
        data = []
        for player in playerdicts:
            if player['team'] == team:
                data.append(player['total minutes'])
                names.append(player['name'])
            else:
                pass
        bar_data = go.Bar(x=names, y=data)
        basic_layout = go.Layout(title=['Total Minutes Played'])
        fig = go.Figure(data=bar_data, layout=basic_layout)
        fig.show()
    else:
        print('Error: Unrecognized Input. Please type one of the accepted inputs.')

def team_2_bars(playerdicts, team1, team2):
    '''Takes a list of player dictionaries and two desired teams and creates a bargraph
    of the players on those teams. The values of the bar graph are determined by userinput
    across 5 possibilities: goals, discipline, goalie, value, and minutes. All graphs
    are aggregated bar graphs, i.e. they stack.

    Parameters:
    playerdicts: a list of player dictionaries
    team1: a string representation of a team name
    team2: a string representation of a second team name

    Returns:
    N/A
    '''
    analytype = input('What type of analysis? Type "goals", "discipline", "goalie", "value", or "minutes": ')
    if analytype.lower() == 'goals':
        fig = go.Figure()
        x = [f'{team1} goals', f'{team2} goals', f'{team1} assists', f'{team2} assists', f'{team1} own goals', f'{team2} own goals']
        for player in playerdicts:
            if player['team'] == team1:
                playerdata = []
                playerdata.append(player['goals'])
                playerdata.append(0)
                playerdata.append(player['assists'])
                playerdata.append(0)
                playerdata.append(player['own goals'])
                playerdata.append(0)
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            elif player['team'] == team2:
                playerdata = []
                playerdata.append(0)
                playerdata.append(player['goals'])
                playerdata.append(0)
                playerdata.append(player['assists'])
                playerdata.append(0)
                playerdata.append(player['own goals'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'discipline':
        fig = go.Figure()
        x = [f'{team1} yellow cards', f'{team2} yellow cards', f'{team1} second yellows', f'{team2} second yellows',
        f'{team1} red cards', f'{team2} red cards']
        for player in playerdicts:
            if player['team'] == team1:
                playerdata = []
                playerdata.append(player['yellow cards'])
                playerdata.append(0)
                playerdata.append(player['second yellows'])
                playerdata.append(0)
                playerdata.append(player['red cards'])
                playerdata.append(0)
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            elif player['team'] == team2:
                playerdata = []
                playerdata.append(0)
                playerdata.append(player['yellow cards'])
                playerdata.append(0)
                playerdata.append(player['second yellows'])
                playerdata.append(0)
                playerdata.append(player['red cards'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'goalie':
        fig = go.Figure()
        x = [f'{team1} goals conceded', f'{team2} goals conceded', f'{team1} clean sheets', f'{team2} clean sheets']
        for player in playerdicts:
            if player['team'] == team1:
                playerdata = []
                playerdata.append(player['goals conceded'])
                playerdata.append(0)
                playerdata.append(player['clean sheets'])
                playerdata.append(0)
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            elif player['team'] == team2:
                playerdata = []
                playerdata.append(0)
                playerdata.append(player['goals conceded'])
                playerdata.append(0)
                playerdata.append(player['clean sheets'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'value':
        fig = go.Figure()
        x = [f'{team1} value ($)', f'{team2} value ($)']
        for player in playerdicts:
            if player['team'] == team1:
                playerdata = []
                playerdata.append(player['value ($)'])
                playerdata.append(0)
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            elif player['team'] == team2:
                playerdata = []
                playerdata.append(0)
                playerdata.append(player['value ($)'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    elif analytype.lower() == 'minutes':
        fig = go.Figure()
        x = [f'{team1} total minutes', f'{team2} total minutes']
        for player in playerdicts:
            if player['team'] == team1:
                playerdata = []
                playerdata.append(player['total minutes'])
                playerdata.append(0)
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            elif player['team'] == team2:
                playerdata = []
                playerdata.append(0)
                playerdata.append(player['total minutes'])
                fig.add_trace(go.Bar(x=x, y=playerdata, name=player['name']))
            else:
                pass
        fig.update_layout(barmode='stack')
        fig.show()
    else:
        print("Error: Unrecognized Input.")

def radar_function(playerdicts):
    '''Takes a given list of player dictionaries and asks the user to select one of them,
    which it uses to create a radar plot. The rest of the dictionaries are used to create
    an "average" which is also on the radar plot, and to sent the range on the radar plot.

    Parameters:
    playerdicts: A list of player dictionaries

    Returns:
    None
    '''
    for i in range(len(playerdicts)):
        print(f'{i+1}. {playerdicts[i]["name"]}')
    analyplay = input('Which player would you like to analyze? Type their number: ')
    if not analyplay.isnumeric():
        print("Error: Please type the number next to the desired team")
    else:
        try:
            intplay = int(analyplay) - 1
            theplayer = playerdicts[intplay]
            if theplayer['position'].lower() == 'goalkeeper':
                categories = ['goals conceded', 'clean sheets', 'total minutes', 'age', 'yellow cards', 'value ($)']
            else:
                categories = ['goals', 'assists', 'total minutes', 'age', 'yellow cards', 'value ($)']
            carinput = input('Would you like "career" stats or "per 90" stats?: ')
            if carinput.lower() == 'per 90':
                categories[2] = 'substitutions on'
                categories[3] = 'appearances'
                categories[5] = 'red cards'
            else:
                pass
            x = []
            y = []
            z = []
            for item in categories:
                ynum = [0, {'total minutes': 0}]
                znum = 0
                for player in playerdicts:
                    if theplayer['position'].lower() == 'goalkeeper':
                        if (item == 'goals conceded' or item == 'clean sheets'):
                            if player['position'].lower() == 'goalkeeper':
                                if carinput.lower() == 'career':
                                    znum += player[item]
                                else:
                                    z90 = player['total minutes'] / 90
                                    znum += (player[item] / z90)
                            else:
                                pass
                        else:
                            if carinput.lower() == 'career':
                                znum += player[item]
                            else:
                                z90 = player['total minutes'] / 90
                                znum += (player[item] / z90)
                    else:
                        if carinput.lower() == 'career':
                            znum += player[item]
                        else:
                            z90 = player['total minutes'] / 90
                            znum += (player[item] / z90)
                    if carinput.lower() == 'career':
                        if player[item] >= ynum[0]:
                            ynum[0] = player[item]
                            ynum[1] = player
                        else:
                            pass
                    else:
                        y90 = player['total minutes'] / 90
                        ystat = player[item] / y90
                        if ystat >= ynum[0]:
                            ynum[0] = ystat
                            ynum[1] = player
                        else:
                            pass
                if carinput.lower() == 'career':
                    compnum = ynum[0] / 5
                    x.append(theplayer[item]/compnum)
                    y.append(ynum[0]/compnum)
                    z.append(znum/compnum)
                elif carinput.lower() == 'per 90':
                    x90 = theplayer['total minutes'] / 90
                    compnum = ynum[0] / 5
                    xmin = theplayer[item] / x90
                    x.append(xmin/compnum)
                    y.append(ynum[0]/compnum)
                    z.append(znum/compnum)
                else:
                    print('sucks 2 suck')
            for i in range(len(z)):
                z[i] = z[i]/len(playerdicts)
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=x,
                theta=categories,
                fill='toself',
                name=theplayer['name']
            ))
            '''fig.add_trace(go.Scatterpolar(
                r=y,
                theta=categories,
                fill='toself',
                name='PlayerMax'
                ))'''
            fig.add_trace(go.Scatterpolar(
                r=z,
                theta=categories,
                fill='toself',
                name='PlayerAvg'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )),
                showlegend=True
            )
            fig.show()
        except:
            print('Error: Number out of range')

def get_desired_stat():
    '''Requests user input to return one of the keys of the player dictionaries that
    can be used in analysis

    Parameters:
    N/A
    
    Returns:
    a string value from playerstattypes list associated with a player dicitonary key
    '''
    playerstattypes = ['value ($)', 'height (cm)', 'appearances', 'goals', 'assists', 'own goals',
                        'substitutions on', 'substitutions off', 'yellow cards', 'second yellows',
                        'red cards', 'penalty goals', 'goals conceded', 'clean sheets',
                        'total minutes', 'minutes per goal']
    for i in range(len(playerstattypes)):
        print(f'{i+1}. {playerstattypes[i]}')
    desiredstatinput = input('What statistic would you like to compare on? Please input the number: ')
    if not desiredstatinput.isnumeric():
        print('Error: Not a Number. Please type the number next to the desired statistic')
    else:
        try:
            desint = int(desiredstatinput) - 1
            return playerstattypes[desint]
        except:
            return None

def analysis_function(playerdicts):
    '''Uses user input to determine what kind of graph they would like to make, and then
    uses the given player dictionaries to call the correct graph creating function

    Parameters:
    playerdicts: a list of player dictionaries

    Returns:
    N/A
    '''
    while True:
        userinput = input('\nWould you like an analyze by player or a team? Type "player", "team", or "back": ')
        if userinput.lower() == 'back':
            break
        elif userinput.lower() == 'player':
            number = input('One player or all players? Please type "one" or "all": ')
            if number.lower() == 'one':
                radar_function(playerdicts)
            elif number.lower() == 'all':
                graphtype = input('Across "one" statistic or "two"?: ')
                if (graphtype == 'one' or graphtype == '1'):
                    desiredstat = get_desired_stat()
                    if desiredstat is not None:
                        bar_graph_players(playerdicts, desiredstat)
                    else:
                        print('Error: Number out of range')
                elif (graphtype == 'two' or graphtype == '2'):
                    print('FIRST STATISTIC')
                    desiredstat1 = get_desired_stat()
                    if desiredstat1 is not None:
                        print('SECOND STATISTIC')
                        desiredstat2 = get_desired_stat()
                        if desiredstat2 is not None:
                            scatter_graph(playerdicts, desiredstat1, desiredstat2)
                        else:
                            print('Error: number out of range')
                    else:
                        print('Error: number out of range')
                else:
                    print('Error: Type "one" or "two"')
        elif userinput.lower() == 'team':
            teamlist = []
            for player in playerdicts:
                if player['team'] not in teamlist:
                    teamlist.append(player['team'])
                else:
                    pass
            for i in range(len(teamlist)):
                print(f'{i+1}. {teamlist[i]}')
            teamnuminput = input('Would you like to analyze "one" or "two" teams?: ')
            if (teamnuminput == "one" or teamnuminput == "1"):
                teaminput = input('Which team would you like to analyze? Type their number: ')
                if not teaminput.isnumeric():
                    print('Error: Please type the number, not the team name')
                else:
                    teamint = int(teaminput) - 1
                    try:
                        team = teamlist[teamint]
                        team_bars(playerdicts, team)
                    except:
                        print('Error: Selected number out of range')
            elif (teamnuminput == "two" or teamnuminput == "2"):
                team1input = input('Which team would you like to analyze? Type their number: ')
                if not team1input.isnumeric():
                    print("Error: Please type the number, not the team name")
                else:
                    team2input = input('Which team would you like to analyze in addition to the first? Type their number: ')
                    if not team2input.isnumeric():
                        print('Error: Please type the number, not the team name')
                    else:
                        team1int = int(team1input) - 1
                        team2int = int(team2input) - 1
                        try:
                            team1 = teamlist[team1int]
                            team2 = teamlist[team2int]
                            team_2_bars(playerdicts, team1, team2)
                        except:
                            print('Error: Selected number out of range')
            else:
                print("Error: Unrecognized input")
        else:
            print('Error: Unrecognized Input. Please type "player", "team", or "exit"')

def input_search_term():
    '''Collects a user search and uses it to scrape information from Transfermarkt regarding
    players and teams that match the search. Prompts the user to select which of the returned
    search options they wish to add to the program for analysis, from the top ten players
    and teams. Adds those to the analysis
    Also prompts the user to move to another part of the program - to remove players and
    teams from analysis, to the analysis itself, or to exit the program
    
    Parameters:
    None
    
    Returns:
    N/A
    '''
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
                analysis_function(playerdicts)
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
                    if player not in playeranalysis:
                        playeranalysis.append(player)
                    else:
                        pass



input_search_term()
