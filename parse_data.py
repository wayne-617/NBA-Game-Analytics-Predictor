import pandas as pd
import os
from bs4 import BeautifulSoup
from io import StringIO
from tqdm import tqdm

SCORES_DIR = "data/scores"

box_scores = os.listdir(SCORES_DIR) # list of files from scores

box_scores = [os.path.join(SCORES_DIR, f) for f in box_scores if f.endswith(".html")] # create full path to files that end with .html

def parse_html(box_score):
    with open(box_score) as f:
        html = f.read()

    soup = BeautifulSoup(html, features="html.parser")

    # get rid of unnecessary rows
    [s.decompose() for s in soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thread")]

    return soup

def read_line_score(soup):
    line_score = pd.read_html(StringIO(str(soup)), attrs={"id": "line_score"})[0]

    # rename columns
    cols = list(line_score.columns)
    cols[0] = "team" 
    cols[-1] = "total"
    line_score.columns = cols

    line_score = line_score[["team", "total"]] # get rid of quarter/ot scores

    return line_score

def read_stats(soup, team, stat):
    stats = pd.read_html(StringIO(str(soup)), attrs={"id" : f"box-{team}-game-{stat}"}, index_col = 0)[0]
    stats = stats.apply(pd.to_numeric, errors="coerce") # set all non-numeric values NaN
    return stats

# get season for the game
def get_season(soup):
    nav = soup.select("#bottom_nav_container")[0]
    hrefs = [a["href"] for a in nav.find_all("a")]
    season = os.path.basename(hrefs[1]).split("_")[0]
    return season


def main():
    games = []
    base_cols = None # def columns for df
    print(len(box_scores))

    for box_score in tqdm(box_scores, desc="Processing Games"):
        soup = parse_html(box_scores) # parse box score

        line_score = read_line_score(soup) # get line score of the game
        teams = list(line_score["team"]) # get teams in the game
        print(teams)

        summaries = []
        for team in teams:
            # get stats
            basic = read_stats(soup, team, "basic") # get basic stat table
            advanced = read_stats(soup, team, "advanced") # get advanced stat table

            # get totals
            totals = pd.concat([basic.iloc[-1], advanced.iloc[-1]]) # combine totals of basic stats and advanced stats into pd series
            totals.index = totals.index.str.lower()
            print(totals)

            # get maxes
            maxes = pd.concat([basic.iloc[:-1].max(), advanced.iloc[:-1].max()]) # get maxes of all columns into 
            maxes.index = maxes.index.str.lower() + "_max" # indicate index is max

            summary = pd.concat([totals, maxes]) # contains team's total stats and max for each stat
            
            if base_cols is None:
                base_cols = list(summary.index.drop_duplicates(keep="first")) # define values to look for in box scores and remove duplicates
                base_cols = [b for b in base_cols if "bpm" not in b] # remove plus-minus stat
                print(f"Base Cols: {base_cols}")
        
            summary = summary[base_cols] # parse summaries to just contain the base columns

            summaries.append(summary)
            
        summary = pd.concat(summaries, axis = 1).T # merge summaries and transpose so that each game is a row and columns are stats
        print(summary)

        game = pd.concat([summary, line_score], axis = 1) # add line score as columns
        game["home"] = [0 , 1] # add home column where first team is away team and second is home team

        # add opposing team stats
        game_opp = game.iloc[::-1].reset_index() # new df where rows are flipped
        game_opp.columns += "_opp" # update column names

        # create full game
        full_game = pd.concat([game, game_opp], axis = 1)

        # add additional columns
        full_game["season"] = get_season(soup) # add season as column
        full_game["date"] = os.path.basename(box_score)[:8]
        full_game["date"] = pd.to_datetime(full_game["date"], format="%Y$m$d") # add date
        full_game["won"] = full_game["total"] > full_game["total_opp"] # add whether or not they won

        games.append(full_game)

    games_df = pd.concat(games, ignore_index=True) # combine all games into one df

    games_df.to_csv("nba_games.csv") # write to csv


if __name__ == "__main__":
    main()


