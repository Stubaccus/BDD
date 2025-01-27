import time
import asyncio
import datetime
import sqlite3

from itertools import islice
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin

from scrapper_script.async_fetch import fetch_all_and_process, fetchone

PARSER = "lxml"
BASE_URL = "https://www.olympedia.org"
RESULT_URL_2020 = "https://www.olympedia.org/editions/61/result"
RESULT_URL_2024 = "https://www.olympedia.org/editions/62/result"

def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

nb_lost_athletes = 0
def is_result_href(href: str) -> bool:
    return href and href.startswith("/results/")

def is_athlete_href(href: str) -> bool:
    return href and href.startswith("/athletes/")

def is_sport_href(href: str) -> bool:
    return href and href.startswith("/sports/")

def is_country_href(href: str) -> bool:
    return href and href.startswith("/countries/")

def get_athlete_data(webcontent: bytes, url) -> dict | None:
    def filter(brut_data: dict) -> dict | None:
        # We only want to recover athlete
        if "Competed in Olympic Games" not in brut_data["Roles"]:
            return None
        data = {}
        name, surname = brut_data["Used name"].split('•')
        if "Name order" in brut_data:
            name, surname = surname, name
        data["Name"] = name
        data["Surname"] = surname
        data["Birthdate"] = datetime.datetime.strptime(" ".join(brut_data["Born"].split()[:3]), '%d %B %Y').date()
        data["NOC"] = brut_data["NOC"]
        data["Gender"] = "Homme" if brut_data["Sex"] == "Male" else "Femme"
        data["URL"] = url
        return data
    if webcontent is None:
        global nb_lost_athletes
        nb_lost_athletes += 1
        return None

    data = {}
    soup = BeautifulSoup(webcontent, PARSER, parse_only=SoupStrainer(class_="biodata"))

    biodata_table = soup.find('table', class_='biodata')
    if biodata_table:
        rows = biodata_table.find_all('tr')
        for row in rows:
            th_elements = row.find_all('th')
            td_elements = row.find_all('td')
            if len(th_elements) == len(td_elements):
                for th, td in zip(th_elements, td_elements):
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    data[key] = value

    noc_link =  biodata_table.find("a", href=is_country_href)
    data["NOC"] = noc_link["href"].split("/")[-1]
    return filter(data)

async def async_get_athlete_data(coro, url) -> dict | None:
    webcontent = await coro
    return get_athlete_data(webcontent, url)

async def get_category_data(url: str, category_name: str, sport: str) -> dict:
    webcontent = await fetchone(url)
    i = category_name.rfind(',')
    name, gender = category_name[:i].strip(), category_name[i+1:].strip()
    is_collective = is_category_collective(name, gender)
    # Open is the same as Mixed, we change it after calling is collective
    # because Open categories are individual while Mixed are collective
    if gender == "Open": 
        gender = "Mixed"

    data = {
        "Is_Collective": is_collective,
        "Gender": "Homme" if gender == "Men" else ("Femme" if gender == "Women" else "Mixte")
    }

    soup = BeautifulSoup(webcontent, PARSER, parse_only=SoupStrainer("table", class_="table table-striped"))
    athletes_link = soup.find_all('a', href=is_athlete_href)
    urls = set(urljoin(BASE_URL, link['href']) for link in athletes_link)
    data["Athletes_URLS"] = urls
    data["Sport"] = sport
    data["Name"] = name
    return data

def is_category_collective(name, gender):
    ind_words = ["Indiviual", "Single"]
    collect_words = ["Team", "Relay", "Double", "Quadruple", "Eights"]
    if any(w in name for w in ind_words):
        return False
    if any(w in name for w in collect_words) or gender == "Mixed":
        return True
    return False

async def data_from_result_url(url: str) -> dict:
    """
        Data format:
            SportName: {
                SportCategoryName {
                    URL,
                    Collectif: bool
                    Athletes: {
                        Name,
                        Firstname,
                        Birthdate,
                        Gender,
                        NOC,
                        Nationality,
                    }
                }
            }
    """

    st = time.time()
    data = {}
    print("Recovering Result Page...")
    webcontent = await fetchone(url)
    soup = BeautifulSoup(webcontent, PARSER, parse_only=SoupStrainer("table", class_="table"))
    print("Recovering Categories URLS...")
    tasks = []
    tds = soup.find_all("td")
    last_sport = ""
    for td in tds:
        link = td.find("a")
        if td.find("h2"):
            last_sport = link.text
            data[last_sport] = {}
        else:
            tasks.append(get_category_data(urljoin(BASE_URL, link["href"]), link.text, last_sport))

    n = len(tasks)
    nb_task_done = 0
    async def counter(coro):
        result = await coro
        nonlocal nb_task_done
        nb_task_done += 1
        t = time.time() - st
        print(f"Sport Category Data: {nb_task_done: }/{n} ({nb_task_done/n:.0%})")
        print(f"Time since start: {int(t)//60} min {int(t)%60}")

        remaining_sec = int(t/nb_task_done * (n-nb_task_done))
        hour = remaining_sec // 3600
        min = (remaining_sec - hour * 3600) // 60
        sec = remaining_sec - hour * 3600 - min * 60
        print(f"Estimated Remaining Time: {hour}h {min}min {sec}sec")
        print()

        return result

    categories_data = []
    for task_group in batched((counter(task) for task in tasks), 50):
        categories_data.extend(await asyncio.gather(*task_group))
                               
    athletes_urls = set()
    for c in categories_data:
        data[c["Sport"]][c["Name"] + " " + c["Gender"]] = c
        athletes_urls = athletes_urls.union(c["Athletes_URLS"])

    n = len(athletes_urls)
    nb_process_athletes = 0
    athlete_st = time.time()
    async def counter_athletes(coro):
        r = await coro
        nonlocal nb_process_athletes
        nb_process_athletes += len(r)

        t = time.time() - athlete_st
        print(f"Athletes Data: {nb_process_athletes: }/{n} ({nb_process_athletes/n:.0%})")
        print(f"Time since start: {int(t)//60} min {int(t)%60}")

        remaining_sec = int(t/nb_process_athletes * (n-nb_process_athletes))
        hour = remaining_sec // 3600
        min = (remaining_sec - hour * 3600) // 60
        sec = remaining_sec - hour * 3600 - min * 60
        print(f"Estimated Remaining Time: {hour}h {min}min {sec}sec")
        print()
        return r
    athletes_data = []
    for urls_group in batched(athletes_urls, 200):
        athletes_data.extend(await counter_athletes(fetch_all_and_process(urls_group, async_get_athlete_data, True,  progress_str="Athletes Data:")))
    athletes_data = [athlete_data for athlete_data in athletes_data if athlete_data]

    print(f"Couldn't get {nb_lost_athletes} Athletes, because of server")
    for sport_data in data.values():
        for category_data in sport_data.values():
            category_data["Athletes"] = [athlete_data for athlete_data in athletes_data if athlete_data["URL"] in category_data["Athletes_URLS"]]

    t = time.time() - st
    print(f"Took {t}sec ({int(t)//60}min {int(t)%60})")
    return data, athletes_data

def insert_data_in_db(con: sqlite3.Connection, data: dict[str, dict[str, dict]], athletes_data: list[dict]) -> None:
    athletes_tuples = []
    for athlete_data in athletes_data:
        if athlete_data:
            t = (athlete_data["Surname"], athlete_data["Name"], athlete_data["Birthdate"], athlete_data["Gender"], False, True)
            athletes_tuples.append(t)

    con.executemany("INSERT INTO Sportif(nom, prenom, date_naissance, sexe, is_paralympic, is_participating) VALUES(?, ?, ?, ?, ?, ?)", athletes_tuples)

    athlete_id_nocs = {}
    for sport, sport_data in data.items():
        try:
            sport_id = con.execute("SELECT (id) FROM Sport WHERE nom_anglais = ?", (sport,)).fetchone()[0]
        except Exception as e:
            print(sport)
            print(e)
            continue

        for category, c_data in sport_data.items():
            athletes_id_in_category = set()
            try:
                temp = con.execute("SELECT (id) FROM SportCategorie WHERE nom_anglais = ? AND sexe = ? AND  id_Sport = ?", (c_data["Name"], c_data["Gender"], sport_id)).fetchone()
            except Exception as e:
                print(f"ERROR: Sport: {c_data['Name']}: sexe: {c_data['Gender']}, sport: {c_data['Sport']}, id_Sport: {sport_id}")
                print(e)
                continue
            if not temp:
                print(f"ERROR: Category: {c_data['Name']}: sexe: {c_data['Gender']}, sport: {c_data['Sport']}, id_Sport: {sport_id}")
                continue
            category_id  = temp[0]
            for athlete_data in c_data["Athletes"]:
                if athlete_data:
                    noc = athlete_data["NOC"]
                    try:
                        athlete_id = con.execute("SELECT (id) FROM Sportif WHERE nom = ? AND prenom = ?", (athlete_data["Surname"], athlete_data["Name"])).fetchone()[0]
                    except Exception as e:
                        print(e)
                        continue
                    athlete_id_nocs[athlete_id] = (athlete_id, noc, True)
                    athletes_id_in_category.add(athlete_id)
            con.executemany("INSERT OR IGNORE INTO Pratique VALUES(?, ?)", ((id, category_id) for id in athletes_id_in_category))
            
    con.executemany("INSERT OR IGNORE INTO Nationalite VALUES(?, ?, ?)", athlete_id_nocs.values())
    con.commit()

async def main():
    try:
        data, athletes_data = await data_from_result_url(RESULT_URL_2020)
        con = sqlite3.connect("./jo2024.sqlite")
        insert_data_in_db(con, data, athletes_data)
        con.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())