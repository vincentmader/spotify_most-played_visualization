#!/usr/bin/env python3

import json
import os
from enum import Enum
from pathlib import Path
from tqdm import tqdm


PATH_TO_DATA    = Path("..", "tmp", "raw_data", "most-recent-export")
PATH_TO_EXPORTS = Path(PATH_TO_DATA, "Spotify Extended Streaming History")


def read_listening_history_from_json() -> list[dict]:
    listening_history = []

    export_files = sorted(os.listdir(PATH_TO_EXPORTS))
    for export_file in tqdm(export_files):
        if not export_file.startswith("Streaming_History_Audio"):
            continue
        # if "2024" not in export_file:
        #     continue

        path_to_export_file = Path(PATH_TO_EXPORTS, export_file)
        with open(path_to_export_file) as fp:
            data = json.load(fp)

        for entry in data:
            listening_history.append(entry)

    return listening_history


class QueryVariant(Enum):
    TITLE  = "master_metadata_track_name"
    ALBUM  = "master_metadata_album_album_name"
    ARTIST = "master_metadata_album_artist_name"


def get_total_playtime_from_query_variant(
    listening_history: list[dict],
    query_variant: QueryVariant
) -> dict[str, float]:
    total_playtime: dict[str, float] = {}

    for entry in tqdm(listening_history):
        query = entry[query_variant.value]
        playtime = entry["ms_played"]
        if query in total_playtime:
            total_playtime[query] += playtime
        else:
            total_playtime[query] = playtime

    most_played = sorted(total_playtime, key=total_playtime.get, reverse=True)
    return { q: total_playtime[q] for q in most_played }


def print_total_playtime_from_query_variant(
    total_playtime: dict[str, float],
    query_variant: QueryVariant
):
    for index, (query, playtime) in enumerate(total_playtime.items()):
        playtime_in_h = playtime / 1000 / 60 / 60

        tmp_h = int(playtime_in_h) // 1
        tmp_m = int(playtime_in_h % 1 * 60)
        tmp_h = f" {tmp_h}" if playtime_in_h < 100   else tmp_h
        tmp_h = f" {tmp_h}" if playtime_in_h < 10    else tmp_h
        tmp_m = f"0{tmp_m}" if tmp_m         < 10    else tmp_m

        index     = index + 1
        index_str =  f"{index}"
        index_str = f" {index_str}" if index         < 10000 else index_str
        index_str = f" {index_str}" if index         < 1000  else index_str
        index_str = f" {index_str}" if index         < 100   else index_str
        index_str = f" {index_str}" if index         < 10    else index_str

        playtime_str  = f"{tmp_h}h {tmp_m}m"
        line = f"{index_str}.\t\t{playtime_str}\t{query}"
        print(line)


if __name__ == "__main__":
    listening_history = read_listening_history_from_json()

    query_variant = QueryVariant.ARTIST  # ARTIST, ALBUM, or TITLE
    total_playtime = get_total_playtime_from_query_variant(listening_history, query_variant)

    print_total_playtime_from_query_variant(total_playtime, query_variant)
