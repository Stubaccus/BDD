import asyncio
import sqlite3 as sql
from bs4 import BeautifulSoup

from scrapper_script.async_fetch import fetch_all_and_process, fetchone

BASE_URL = "https://www.lequipe.fr"
PARSER = "lxml"

MEDAILLES = ["Or", "Argent", "Bronze", None]

import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

async def process_result(coro, url: str, resultats: list[dict]):
    print("Traitement: " + url)
    soup = BeautifulSoup(await coro, PARSER)
    first_list_element = soup.find('section', class_='UniversalResults__list')
    sport_category, sexe, sport = format_category_name(soup.find("option", {"selected": True}).text, url)
    if not first_list_element:
        return
    
    h2 = first_list_element.find('h2')
    date = None
    if h2:
        h2_text = h2.get_text(strip=True)
        if "Finale - " in h2_text:
            date = h2_text.split("Finale - ")[1]
        else:
            h3 = first_list_element.find('h3')
            if h3:
                h3_text = h3.get_text(strip=True)
                if "Finale - " in h3_text:
                    date = h3_text.split("Finale - ")[1]

    tr_elements = first_list_element.find_all('tr')[1:]
    for index, tr in enumerate(tr_elements):
        td_elements = tr.find_all('td')
        if len(td_elements) >= 4:
            auteur = td_elements[2].get_text(strip=True)
            value: str = td_elements[3].get_text(strip=True)
            record_olympique = "Record olympique" in value or "Record du monde" in value

            if "Record" in value:
                value = value.split("Record")[0]
            if "pts" in value:
                value = value.split("pts")[0] + "pts"

            # Ajout de la médaille en fonction de l'index du tr
            place =  MEDAILLES[index] if index < 3 else index+1

            resultats.append({
                "id": len(resultats),
                "date": date,
                "auteur": auteur,
                "value": value,
                "is_record": record_olympique,
                "place": place,
                "category": sport_category,
                "sexe": sexe,
                "sport": sport
            })

def format_category_name(sport_category: str, url: str):
    sport_category = sport_category.strip().split(" ")
    name, sexe = " ".join(sport_category[:-1]).capitalize(), sport_category[-1].capitalize()
    if sexe[-1] == "s":
        sexe = sexe[:-1]
    sport = url.split("/")[3].replace("-", " ")
    if sport == "Bmx":
        sport = "BMX racing" if name == "Course" else "BMX freestyle"
    elif sport == "Canoe kayak":
        sport = "Canoë-kayak slalom" if name.startswith("Slalom") else "Canoë-kayak sprint"
    elif sport == "Equitation":
        if name.startswith("Concours"):
            sport = "Concours Complet équestres"
        elif name.startswith("Saut"):
            sport =  "Saut équestres"
        else:
            sport = "Dressage équestres"
    return name, sexe, sport

async def process_sport(coro, url: str, resultats: list[dict]):
    soup = BeautifulSoup(await coro, PARSER)
    result_links = [BASE_URL + link["href"] for link in soup.find_all('a', class_='Link CalendarWidget__link')]

    await fetch_all_and_process(result_links, process_result, True, resultats=resultats)
        
def appartient_data(resultats: list[dict], con: sql.Connection) -> list[tuple]:
    data = []
    for resultat in resultats:
        resultat_id = resultat["id"]
        athlete: str = resultat["auteur"]
        if ',' in athlete: # don't deal with collective for now
            continue
        sportif_row = con.execute(
            "SELECT (id) FROM Sportif WHERE remove_accents(prenom || ' ' || nom) = remove_accents(?) " + 
            "OR remove_accents(nom || ' ' || prenom) = remove_accents(?)", (athlete, athlete)).fetchone()
        if sportif_row:
            try:
                sport_id = con.execute("SELECT (id) FROM Sport WHERE nom = ?", (resultat["sport"],)).fetchone()[0]
            except Exception as e:
                print(e)
                print(resultat["sport"])
                continue

            try:
                category_id = con.execute(
                    "SELECT (id) FROM SportCategorie WHERE nom = ? AND sexe = ? AND  id_Sport = ?"
                    , (resultat["category"], resultat["sexe"], sport_id)
                ).fetchone()[0]
            except Exception as e:
                print(e)
                print(sport_id, resultat["sport"], resultat["category"], resultat["sexe"])
                continue
            data.append((resultat_id, sportif_row[0], category_id))
        else:
            pass
            #print(f"ATHLETE: {athlete} NOT FOUND IN DB")
    return data

async def parcourir_liste_resultats(url: str, con: sql.Connection):
    print("Récupération de la page principale...")

    html_content = await fetchone(url)
    soup = BeautifulSoup(html_content, PARSER)
    divs = soup.find_all('div', class_='UniversalResults__header')
    sports_urls = [BASE_URL + div.find("a")["href"] for div in divs]
    resultats = []
    await fetch_all_and_process(sports_urls, process_sport, True, resultats=resultats)

    print("Insertion des données dans la base de données...")
    # Insérer les données dans la base de données jo2024.sqlite
    results_data = [[d["id"], d["date"], d["value"], d["is_record"], d["place"]] for d in resultats]
    con.executemany('INSERT INTO Resultat (id, date, valeur, is_record, type_Medaille) VALUES (?, ?, ?, ?, ?)', results_data)
   
    d = appartient_data(resultats, con)
    #print(con.execute("SELECT remove_accents(prenom || ' ' || nom) FROM Sportif").fetchall()[:10])
    con.executemany('INSERT INTO Appartient VALUES (?, ?, ?)', d)

    con.commit()
    print("Données insérées avec succès.")

async def main():
    con = sql.connect("./jo2024.sqlite")
    con.create_function("remove_accents", 1, remove_accents)
    con.commit()

    url = "https://www.lequipe.fr/jeux-olympiques-ete/annee-2020/page-resultats-par-sport"
    await parcourir_liste_resultats(url, con)
    con.close()
    print("Les données ont été insérées avec succès dans la table 'Resultat' de la base de données 'jo2024.sqlite'.")

if __name__ == "__main__":
    asyncio.run(main())