import riotwatcher
from quickchart import QuickChart
import datetime

API_KEY = "RGAPI-2c01f0ab-4e14-45cd-b32e-bec731d68939"
REGION = "EUW1"

lol_watcher = riotwatcher.LolWatcher(API_KEY)


class Team:
    def __init__(self, *members):
        self.members = list(members)

    def add(self, member):
        self.members.append(member)

    def get_average_elo(self):
        """ Returns the average elo of the team """
        total = 0
        for member in self.members:
            total += member.elo.get_raw_elo()
        print(f"total : {total}")
        return Elo(raw_elo=total // len(self.members))

    def __repr__(self):
        s = ""
        for member in self.members:
            s += f"{member.summoner_name} : {member.elo}\n"
        return s


def get_index_solo_duo(liste):
    for i, e in enumerate(liste):
        if e["queueType"] == "RANKED_SOLO_5x5":
            return i


class Player:
    def __init__(self, summoner_name):
        self.summoner_name = summoner_name
        self.summoner_id = self.get_summoner_id()
        self.elo = self.get_elo()

    def get_elo(self):
        """ Returns solo duo rank of the player """
        info = lol_watcher.league.by_summoner(REGION, self.summoner_id)
        i = get_index_solo_duo(info)
        info = info[i]
        rank = info["tier"]
        lp = info["leaguePoints"]
        division = info["rank"]
        return Elo(rank=rank, lp=lp, division=division)

    def get_summoner_id(self):
        """ Returns the summoner id of the player """
        try:
            return lol_watcher.summoner.by_name(REGION, self.summoner_name)["id"]
        except Exception as e:
            print(e)
            return None


ranks = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
divisions = ["IV", "III", "II", "I"]


class Elo:
    def __init__(self, *, rank=None, lp=None, division=None, raw_elo=None):
        self.rank = rank
        self.division = division
        self.lp = lp
        self.raw_elo = raw_elo
        if not self.rank and raw_elo:
            self.compute_rank()
        self.raw_elo = self.get_raw_elo()

    def compute_rank(self):
        """ Computes the rank from the raw elo """
        rank_index, rest = divmod(self.raw_elo, 400)
        division_index, lp = divmod(rest, 100)
        self.rank = ranks[rank_index]
        if self.rank == "MASTER" or self.rank == "GRANDMASTER" or self.rank == "CHALLENGER":
            self.division = ""
        else:
            self.division = divisions[division_index]
        self.lp = lp

    def get_raw_elo(self):
        """ Returns the elo as a number """
        index = ranks.index(self.rank)
        raw_elo = 0
        if index <= 5:
            raw_elo += index * 400 + self.lp
            raw_elo += divisions.index(self.division) * 100
        else:  # MASTER,GRANDMASTER or CHALLENGER
            raw_elo += ranks.index("MASTER") * 400 + self.lp

        return raw_elo

    def __repr__(self):
        return f"{self.rank} {self.division} {self.lp} LP -> raw elo : {self.raw_elo}"


def get_team_from_file(file):
    """ Returns a team from a file """
    with open(file, "r") as f:
        lines = f.readlines()
        team = Team()
        for line in lines:
            team.add(Player(line.strip()))
        return team


def get_current_date_uk():
    """ Returns the current date in the UK format """
    return datetime.datetime.now().strftime("%m/%d/%Y")


def write_elo_to_file(elo_file, team):
    """ Writes the elo of the team to a file or modifies the last line if the date is the same"""
    flag = False
    with open(elo_file, "r") as f:
        lines = f.readlines()
        if lines:
            last_line = lines[-1]
            if last_line.split(":")[0] == get_current_date_uk():
                flag = True

    if not flag:
        with open("elo.txt", "a") as f:
            f.write(f"{get_current_date_uk()}:{team.get_average_elo().raw_elo}\n")
    else:
        # modify the last line
        with open("elo.txt", "w") as f:
            for line in lines[:-1]:
                f.write(line)
            f.write(f"{get_current_date_uk()}:{team.get_average_elo().raw_elo}\n")


def get_dates_and_elos_from_file(file):
    with open(file, "r") as f:
        lines = f.readlines()
        x = []
        y = []
        for line in lines:
            date, elo = line.split(":")
            x.append(date)
            y.append(int(elo))
        return x, y


def dl_graph_and_add_point(team_file, elo_file):
    qc = QuickChart()
    team = get_team_from_file(team_file)
    write_elo_to_file(elo_file, team)

    x, y = get_dates_and_elos_from_file(elo_file)
    dates = ",".join([f'"{i}"' for i in x])
    elos = ",".join([str(i) for i in y])

    print(dates)
    print(elos)

    qc.config = qc.config = """{
  "type": "line",
  "data": {
    "datasets": [
      {
        "label": "League of Legends ELO",
        "data": [
          """ + elos + """
        ],
        "borderColor": "rgba(54, 162, 235, 1)",
        "backgroundColor": "rgba(54, 162, 235, 0.2)",
        "fill": true,
        "spanGaps": false,
        "lineTension": 0.4,
        "pointRadius": 0,
        "pointHoverRadius": 3,
        "pointStyle": "circle",
        "borderDash": [
          0,
          0
        ],
        "barPercentage": 0.9,
        "categoryPercentage": 0.8,
        "type": "line",
        "borderWidth": 3,
        "hidden": false
      }
    ],
    "labels": [
        """ + dates + """
    ]
  },
  "options": {
    "title": {
      "display": false,
      "position": "top",
      "fontSize": 12,
      "fontFamily": "sans-serif",
      "fontColor": "#666666",
      "fontStyle": "bold",
      "padding": 10,
      "lineHeight": 1.2,
      "text": "Chart title"
    },
    "layout": {
      "padding": {},
      "left": 0,
      "right": 0,
      "top": 0,
      "bottom": 0
    },
    "legend": {
      "display": false,
      "position": "top",
      "align": "center",
      "fullWidth": true,
      "reverse": false,
      "labels": {
        "fontSize": 12,
        "fontFamily": "sans-serif",
        "fontColor": "#666666",
        "fontStyle": "normal",
        "padding": 10
      }
    },
    "scales": {
      "xAxes": [
        {
          "id": "X1",
          "type": "time",
          "time": {
            "unit": "day",
            "stepSize": 15,
            "displayFormats": {
              "millisecond": "h:mm:ss.SSS a",
              "second": "h:mm:ss a",
              "minute": "h:mm a",
              "hour": "hA",
              "day": "MMM D",
              "week": "ll",
              "month": "MMM YYYY",
              "quarter": "[Q]Q - YYYY",
              "year": "YYYY"
            }
          },
          "scaleLabel": {
            "display": false,
            "labelString": "Date",
            "lineHeight": 1.2,
            "fontColor": "white",
            "fontFamily": "sans-serif",
            "fontSize": 12,
            "fontStyle": "normal",
            "padding": 4
          },
          "display": true,
          "position": "bottom",
          "stacked": false,
          "offset": false,
          "distribution": "linear",
          "gridLines": {
            "display": false,
            "color": "rgba(0, 0, 0, 0.1)",
            "borderDash": [
              0,
              0
            ],
            "lineWidth": 1,
            "drawBorder": true,
            "drawOnChartArea": true,
            "drawTicks": true,
            "tickMarkLength": 10,
            "zeroLineWidth": 1,
            "zeroLineColor": "rgba(0, 0, 0, 0.25)",
            "zeroLineBorderDash": [
              0,
              0
            ]
          },
          "angleLines": {
            "display": true,
            "color": "rgba(0, 0, 0, 0.1)",
            "borderDash": [
              0,
              0
            ],
            "lineWidth": 1
          },
          "pointLabels": {
            "display": false,
            "fontColor": "#666",
            "fontSize": 10,
            "fontStyle": "normal"
          },
          "ticks": {
            "display": true,
            "fontSize": 12,
            "fontFamily": "sans-serif",
            "fontColor": "white",
            "fontStyle": "normal",
            "padding": 0,
            "stepSize": null,
            "minRotation": 0,
            "maxRotation": 50,
            "mirror": false,
            "reverse": false
          }
        }
      ],
      "yAxes": [
        {
          "id": "Y1",
          "type": "linear",
          "position": "left",
          "ticks": {
            "beginAtZero": true,
            "min": 1600,
            "max": 3000,
            "display": true,
            "fontSize": 12,
            "fontFamily": "sans-serif",
            "fontColor": "white",
            "fontStyle": "normal",
            "padding": 0,
            "stepSize": null,
            "minRotation": 0,
            "maxRotation": 50,
            "mirror": false,
            "reverse": false
          },
          "scaleLabel": {
            "display": false,
            "labelString": "ELO",
            "lineHeight": 1.2,
            "fontColor": "#666666",
            "fontFamily": "sans-serif",
            "fontSize": 12,
            "fontStyle": "normal",
            "padding": 4
          },
          "display": true,
          "stacked": false,
          "offset": false,
          "time": {
            "unit": false,
            "stepSize": 1,
            "displayFormats": {
              "millisecond": "h:mm:ss.SSS a",
              "second": "h:mm:ss a",
              "minute": "h:mm a",
              "hour": "hA",
              "day": "MMM D",
              "week": "ll",
              "month": "MMM YYYY",
              "quarter": "[Q]Q - YYYY",
              "year": "YYYY"
            }
          },
          "distribution": "linear",
          "gridLines": {
            "display": false,
            "color": "rgba(0, 0, 0, 0.1)",
            "borderDash": [
              0,
              0
            ],
            "lineWidth": 1,
            "drawBorder": true,
            "drawOnChartArea": true,
            "drawTicks": true,
            "tickMarkLength": 10,
            "zeroLineWidth": 1,
            "zeroLineColor": "rgba(0, 0, 0, 0.25)",
            "zeroLineBorderDash": [
              0,
              0
            ]
          },
          "angleLines": {
            "display": true,
            "color": "rgba(0, 0, 0, 0.1)",
            "borderDash": [
              0,
              0
            ],
            "lineWidth": 1
          },
          "pointLabels": {
            "display": true,
            "fontColor": "#666",
            "fontSize": 10,
            "fontStyle": "normal"
          }
        }
      ]
    },
    "plugins": {
    
      "datalabels": {
        "display": false,
        "align": "center",
        "anchor": "center",
        "backgroundColor": "#eee",
        "borderColor": "#ddd",
        "borderRadius": 6,
        "borderWidth": 1,
        "padding": 4,
        "color": "#666666",
        "font": {
          "family": "sans-serif",
          "size": 10,
          "style": "normal"
        }
      },
      
      "datalabelsZAxis": {
        "enabled": false
      },
      "googleSheets": {},
      "airtable": {},
      "tickFormat": ""
    },
    "cutoutPercentage": 50,
    "rotation": -1.5707963267948966,
    "circumference": 6.283185307179586,
    "startAngle": -1.5707963267948966
  }
}"""

    qc.background_color = "transparent"
    qc.to_file('mychart.png')


def add_player_to_team(player):
    with open("players.txt", "a", encoding="utf-8") as f:
        f.write(f"{player}\n")


def get_players_from_file():
    with open("players.txt", "r") as f:
        lines = f.readlines()
        return [Player(line.strip()) for line in lines]


if __name__ == "__main__":
    pseudos = ["TimeMeansNothing",
               "Sucré Calienté",
               "Le ZzZ",
               "La tour de Pisse",
               "Perdu en forêt"]
    team = Team()
    for pseudo in pseudos:
        team.add(Player(pseudo))
    dl_graph_and_add_point("team.txt", "elo.txt")
