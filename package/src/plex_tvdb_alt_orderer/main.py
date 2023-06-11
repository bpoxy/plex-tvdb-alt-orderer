from __future__ import annotations
import click
import inquirer
import re
import validators
from plexapi.myplex import MyPlexAccount, PlexServer
from plexapi.library import ShowSection
from plexapi.video import Episode, Show
from progress.bar import Bar
from termcolor import colored
from tvdb_v4_official import TVDB

UPDATE_ENTIRE_SERIES = -1

@click.command()
@click.option("--plex-library", "plex_section_name", type=str, envvar="ALT_ORDERER_PLEX_LIBRARY",
              help="Your Plex TV show library name. Omit to use the ALT_ORDERER_PLEX_LIBRARY environment variable, choose from a list interactively or if your Plex server has a sole TV show library.")
@click.option("--plex-password", type=str, envvar="ALT_ORDERER_PLEX_PASSWORD",
              help="Your Plex password. Omit to use the ALT_ORDERER_PLEX_PASSWORD environment variable or enter interactively.")
@click.option("--plex-server", "plex_server_identifier", type=str, envvar="ALT_ORDERER_PLEX_SERVER",
              help="Your Plex server name (user/password authentication) or URL (token authentication). Omit to use the ALT_ORDERER_PLEX_SERVER environment variable or enter interactively.")
@click.option("--plex-show", "plex_show_name", type=str, envvar="ALT_ORDERER_PLEX_SHOW",
              help="The name of the show in Plex. Omit to use the ALT_ORDERER_PLEX_SHOW environment variable or enter interactively.")
@click.option("--plex-token", type=str, envvar="ALT_ORDERER_PLEX_TOKEN",
              help="Your Plex token. Omit to use the ALT_ORDERER_PLEX_TOKEN environment variable or enter interactively.")
@click.option("--plex-user", type=str, envvar="ALT_ORDERER_PLEX_USER",
              help="Your Plex username. Omit to use the ALT_ORDERER_PLEX_USER environment variable or enter interactively.")
@click.option("--season", type=int, envvar="ALT_ORDERER_SEASON",
              help=f"The season to update ({UPDATE_ENTIRE_SERIES} to update the entire series). Omit to use the ALT_ORDERER_SEASON environment variable or enter interactively.")
@click.option("--tvdb-order", "tvdb_order_name", type=str, envvar="ALT_ORDERER_TVDB_ORDER",
              help="The TVDB order name (as specified for API-connected systems). Omit to use the ALT_ORDERER_TVDB_ORDER environment variable or choose from a list interactively.")
@click.option("--tvdb-pin", type=str, envvar="ALT_ORDERER_TVDB_PIN",
              help="Your TVDB subscriber PIN. Omit to use the ALT_ORDERER_TVDB_PIN environment variable or enter interactively.")

def main(plex_section_name: str, plex_password: str, plex_server_identifier: str, plex_show_name: str, plex_token: str, plex_user: str, season: int, tvdb_order_name: str, tvdb_pin: str):
    plex_server = get_plex_server(plex_password, plex_server_identifier, plex_token, plex_user)
    plex_section = get_plex_section(plex_server, plex_section_name)
    plex_show = get_plex_show(plex_section, plex_show_name)
    plex_episodes = plex_show.episodes()
    
    tvdb_pin = text_prompt_if_unspecified(tvdb_pin, "your TVDB subscriber PIN")
    tvdb = TVDB(apikey="5f119e31-f9c5-4f0c-b1c3-064b3225e7d9", pin=tvdb_pin)
    tvdb_id = next(match.group("id") for match in [re.match(r"tvdb://(?P<id>\d+)", guid.id) for guid in plex_show.guids] if match)
    tvdb_season_type = get_tvdb_season_type(tvdb, tvdb_id, tvdb_order_name)
    tvdb_episodes = tvdb.get_series_episodes(tvdb_id, season_type=tvdb_season_type, lang="eng")["episodes"]
    
    update_plex(season, plex_episodes, tvdb_episodes)

def dict_to_tuple(dict: dict):
    return [(key, value) for key, value in dict.items()]

def error_exit(text: str):
    print(colored(text, "red"))
    exit()

def get_plex_section(plex_server: PlexServer, section_name: str) -> ShowSection:
    sections = list(filter(lambda s: s.TYPE == "show", plex_server.library.sections()))
    sections_dict = {s.title: s for s in sections}

    if section_name:
        return sections_dict.get(section_name, None) or error_exit(f"Your Plex server doesn't contain a TV show library named '{section_name}'.")

    if len(sections) == 0:
        error_exit(f"Your Plex server doesn't contain a TV show library.")
    elif len(sections) == 1:
        return sections[0]
    else:
        return inquirer.prompt([inquirer.List("section", message="Select the library to update", choices=dict_to_tuple(sections_dict))])["section"]

def get_plex_server(plex_password: str, plex_server_identifier: str, plex_token: str, plex_user: str) -> PlexServer:
    plex_server_identifier = text_prompt_if_unspecified(plex_server_identifier, "your Plex server name (user/password authentication) or URL (token authentication)")

    if validators.url(plex_server_identifier):
        return PlexServer(plex_server_identifier, text_prompt_if_unspecified(plex_token, "your Plex token"))

    plex_user = text_prompt_if_unspecified(plex_user, "your Plex username")
    plex_password = plex_password or inquirer.prompt([inquirer.Password("password", message=f"Enter your Plex password")])["password"]
    plex_account = MyPlexAccount(plex_user, plex_password)
    return plex_account.resource(plex_server_identifier).connect()

def get_plex_show(section: ShowSection, show_name: str) -> Show:
    show_name = text_prompt_if_unspecified(show_name, "the name of the show")
    shows = section.search(title=show_name)

    if len(shows) == 0:
         error_exit(f"Your TV show library doesn't contain a show with name '{show_name}'.")
    elif len(shows) == 1:
        return shows[0]
    else:
        shows_dict = {s.title: s for s in shows}
        return inquirer.prompt([inquirer.List("show", message="Select the show to update", choices=dict_to_tuple(shows_dict))])["show"]

def get_tvdb_season_type(tvdb: TVDB, tvdb_id: int, order_name: str) -> str:
    season_types = tvdb.get_season_types(tvdb_id)
    season_types_dict = {s["name"]: s["type"] for s in season_types}

    if order_name:
        return season_types_dict.get(order_name, None) or error_exit(f"TVDB doesn't define an order with name '{order_name}'.")

    return inquirer.prompt([inquirer.List("season_type", message="Select the order to apply", choices=dict_to_tuple(season_types_dict))])["season_type"]

def text_prompt_if_unspecified(value: str, description: str):
    return value or inquirer.prompt([inquirer.Text("answer", message=f"Enter {description}")])["answer"]

def update_plex(season: int, plex_episodes: list[Episode], tvdb_episodes: list[dict]):
    plex_seasons_dict = {"Entire Series": UPDATE_ENTIRE_SERIES}
    plex_seasons_dict.update({f"Season {e.parentIndex}": e.parentIndex for e in plex_episodes})
    season = season or inquirer.prompt([inquirer.List("season", message="Select the season to update", choices=dict_to_tuple(plex_seasons_dict))])["season"]

    if season != UPDATE_ENTIRE_SERIES:
        plex_episodes = list(filter(lambda e: e.parentIndex == season, plex_episodes))
        tvdb_episodes = list(filter(lambda e: e["seasonNumber"] == season, tvdb_episodes))

    tvdb_episode_dict = {}

    for e in tvdb_episodes:
        episode_number = e["number"]
        season_number = e["seasonNumber"]

        if season_number not in tvdb_episode_dict:
            tvdb_episode_dict[season_number] = {}

        tvdb_episode_dict[season_number][episode_number] = e

    for e in plex_episodes:
        if e.parentIndex not in tvdb_episode_dict or e.index not in tvdb_episode_dict[e.parentIndex]:
            error_exit(f"S{e.parentIndex:02}E{e.index:02} doesn't exist in the selected TVDB order.")

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