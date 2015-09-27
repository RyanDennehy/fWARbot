import praw, re, os, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bot_config import *

"""
fwar.py
Author: Ryan Dennehy <rmd5947 @ rit.edu>

A reddit bot for posting fWAR scores from FanGraphs on demand
"""

def process(match):
    """Return a list of players (strings) from an re MatchObject"""
    return match.group(0)[6:].split("; ")

def initialize_bot():
    """Log into Reddit as the bot"""
    user_agent = ("fWARbot 0.1")
    r = praw.Reddit(user_agent=user_agent)

    r.login(r_username, r_password, disable_warning=True)

    return r

def search_new(player, base_url):
    """
    Search for a player on fangraphs.com

    player   - the name of a player
    base_url - the base url, i.e. fangraphs.com

    Returns a BeautifulSoup object of the desired page
    """
    driver = webdriver.Firefox()                #Opens up browser window
    driver.get(base_url)                        #Go to base_url page
    box = driver.find_element_by_id("psbox")    #Find the search box
    box.send_keys(player)                       #Enter the player's name
    box.send_keys(Keys.ENTER)                   #Hit enter
    new_page = BeautifulSoup(requests.get(driver.current_url).text, "lxml")
    driver.close()
    return new_page

def findWAR(player, base_url):
    """
    Finds a player's WAR on the FanGraphs page

    player   - the name of the player
    base_url - the base url, i.e. fangraphs.com

    Returns the player's WAR
    """
    soup = search_new(player, base_url) 
    for row in soup.select('#SeasonStats1_dgSeason11_ctl00 tr'):
        cols = [elem.get_text(strip=True) for elem in row.find_all('td')]
        if not cols: 
            continue
        if cols[0] == '2015' and cols[1] in TEAMS:
            print(cols[-1])
            return cols[-1]

def create_output(players, base_url):
    """
    Create properly formatted string for output

    players  - list of names of players
    base_url - the base url, i.e. fangraphs.com
    """
    WARs = [findWAR(player, base_url) for player in players]
    string = "fWAR for player(s): {}\n\n".format(", ".join(players))
    string += "Player | fWAR\n---|---\n"
    for player, WAR in zip(players, WARs):
        string += "{0} | {1}\n".format(player, WAR)
    string += "\n"
    return string


def main():
    """
    Initialize the bot, check for any comments that match the pattern,
    lookup WARs, and respond

    Not yet implemented - making sure it doesn't respond to the same
    comment more than once
    """
    r = initialize_bot()
    fangraphs = "http://www.fangraphs.com/"

    #If we don't already have a file of posts replied to
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else: #If we do
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read().split("\n")
            posts_replied_to = filter(None, posts_replied_to)

    #sub = r.get_subreddit("baseball")
    sub = r.get_subreddit("fWARbot")
    for submission in sub.get_hot(limit=25):
        for comment in submission.comments:
            m = re.search("fWAR! .+", comment.body)
            if m:
                comment.reply(create_output(process(m), fangraphs))

if __name__ == "__main__":
    main()
