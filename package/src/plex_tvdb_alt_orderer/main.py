import click
import inquirer
import re
from plexapi.myplex import MyPlexAccount, MyPlexResource
from plexapi.library import ShowSection
from plexapi.video import Episode, Show
from progress.bar import Bar
from tvdb_v4_official import TVDB

@click.command()
@click.option("--plex-library", "plex_section_name", type=str, help="Your Plex TV show library name. Omit to choose from a list interactively or if your Plex server has a single TV show library.")
@click.option("--plex-password", type=str, help="Your Plex password. Omit to enter interactively.")
@click.option("--plex-server", type=str, help="Your Plex server name. Omit to enter interactively.")
@click.option("--plex-show", "plex_show_name", type=str, help="The name of the show in Plex. Omit to enter interactively.")
@click.option("--plex-user", type=str, help="Your Plex username. Omit to enter interactively.")
@click.option("--tvdb-order", "tvdb_order_name", type=str, help="The TVDB order name (as specified for API-connected systems). Omit to choose from a list interactively.")
@click.option("--tvdb-pin", type=str, help="Your TVDB subscriber PIN. Omit to enter interactively.")

def main(plex_section_name: str, plex_password: str, plex_server: str, plex_show_name: str, plex_user: str, tvdb_order_name: str, tvdb_pin: str):
    questions = []

    if not tvdb_pin:
        questions.append(inquirer.Text("tvdb_pin", message="Enter your TVDB subscriber PIN"))
    if not plex_user:
        questions.append(inquirer.Text("plex_user", message="Enter your Plex username"))
    if not plex_password:
        questions.append(inquirer.Text("plex_password", message="Enter your Plex password"))
    if not plex_server:
        questions.append(inquirer.Text("plex_server", message="Enter your Plex server name"))

    answers = inquirer.prompt(questions)

    plex_account = MyPlexAccount(plex_user or answers["plex_user"], plex_password or answers["plex_password"])
    plex = plex_account.resource(plex_server or answers["plex_server"]).connect()

    plex_section = get_plex_section(plex, plex_section_name)
    plex_show = get_plex_show(plex_section, plex_show_name)
    plex_episodes = plex_show.episodes()
    tvdb_id = next(match.group("id") for match in [re.match(r"tvdb://(?P<id>\d+)", guid.id) for guid in plex_show.guids] if match)

    tvdb = TVDB(apikey="5f119e31-f9c5-4f0c-b1c3-064b3225e7d9", pin=tvdb_pin or answers["tvdb_pin"])
    tvdb_season_type = get_tvdb_season_type(tvdb, tvdb_id, tvdb_order_name)
    tvdb_episodes = tvdb.get_series_episodes(tvdb_id, season_type=tvdb_season_type, lang="eng")["episodes"]
    
    update_plex(plex_episodes, tvdb_episodes)

def get_plex_section(plex: MyPlexResource, section_name: str) -> ShowSection:
    sections = list(filter(lambda s: s.TYPE == "show", plex.library.sections()))

    if section_name:
        section = next(filter(lambda s: s.title == section_name, sections), None)
        
        if not section:
            raise ValueError(f"Your Plex server doesn't contain a TV show library named '{section_name}'.")

        return section

    if len(sections) == 0:
        raise ValueError(f"Your Plex server doesn't contain a TV show library.")
    elif len(sections) == 1:
        section = sections[0]
    else:
        sections_dict = {s.title: s for s in sections}
        section_title = inquirer.prompt([inquirer.List("section_title", message="Select the library to update", choices=sections_dict.keys())])["section_title"]
        section = sections_dict[section_title]

    return section

def get_plex_show(section: ShowSection, show_name: str) -> Show:
    show_name = show_name or inquirer.prompt([inquirer.Text("show_name", message="Enter the name of the show")])["show_name"]
    shows = section.search(title=show_name)

    if len(shows) == 0:
        raise ValueError(f"Your TV show library doesn't contain a show with name '{show_name}'.")
    elif len(shows) == 1:
        show = shows[0]
    else:
        shows_dict = {s.title: s for s in shows}
        show_title = inquirer.prompt([inquirer.List("show_title", message="Select the show to update", choices=shows_dict.keys())])["show_title"]
        show = shows_dict[show_title]

    return show

def get_tvdb_season_type(tvdb: TVDB, tvdb_id: int, order_name: str) -> str:
    season_types = tvdb.get_season_types(tvdb_id)
    season_types_dict = {s["name"]: s["type"] for s in season_types}

    if order_name and order_name not in season_types_dict:
        raise ValueError(f"TVDB doesn't define an order with name '{order_name}'.")

    season_type_name = order_name or inquirer.prompt([inquirer.List("season_type_name", message="Select the order to apply", choices=season_types_dict.keys())])["season_type_name"]
    return season_types_dict[season_type_name]

def update_plex(plex_episodes: list[Episode], tvdb_episodes: list[dict]):
    tvdb_episode_dict = {}

    for e in tvdb_episodes:
        episode_number = e["number"]
        season_number = e["seasonNumber"]

        if season_number not in tvdb_episode_dict:
            tvdb_episode_dict[season_number] = {}

        tvdb_episode_dict[season_number][episode_number] = e

    for e in plex_episodes:
        if e.parentIndex not in tvdb_episode_dict or e.index not in tvdb_episode_dict[e.parentIndex]:
            raise KeyError(f"S{e.parentIndex:02}E{e.index:02} doesn't exist in the selected TVDB order.")

    progress = Bar("Updating Plex", max=len(plex_episodes))

    for e in plex_episodes:
        tvdb_episode = tvdb_episode_dict[e.parentIndex][e.index]

        e.editOriginallyAvailable(tvdb_episode["aired"])
        e.editSummary(tvdb_episode["overview"])
        e.editTitle(tvdb_episode["name"])

        if tvdb_episode["image"]:
            e.uploadPoster("https://thetvdb.com" + tvdb_episode["image"])

        progress.next()

    progress.finish()

if __name__ == "__main__":
    main()