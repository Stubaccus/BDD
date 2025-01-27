import asyncio
from bs4 import BeautifulSoup

def process_wikipedia_page(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'lxml')

    body = soup.find('body')
    if body:
        div1 = body.find('div', class_='mw-page-container')
        if div1:
            div2 = div1.find('div', class_='mw-page-container-inner')
            if div2:
                div3 = div2.find('div', class_='mw-content-container')
                if div3:
                    main = div3.find('main', class_='mw-body')
                    if main:
                        div4 = main.find('div', id='bodyContent')
                        if div4:
                            div5 = div4.find('div', id='mw-content-text')
                            if div5:
                                div6 = div5.find('div', class_='mw-content-ltr mw-parser-output')
                                if div6:
                                    tables = div6.find_all('table', class_=lambda x: x and 'wikitable' in x.split())
                                    for table in tables:
                                        first_row = table.find('tr')
                                        if first_row and 'Discipline' in first_row.text:
                                            headers = [header.text.strip() for header in first_row.find_all('th')[:-1]]  # Récupérer les en-têtes, en excluant la dernière colonne
                                            for row in table.find_all('tr')[1:]:  # Parcourir les lignes suivantes, en ignorant la première
                                                columns = row.find_all('td')[:-1]  # Exclure la dernière colonne
                                                if len(columns) >= len(headers):  # Assurer que le nombre de colonnes correspond au nombre d'en-têtes
                                                    for header, column in zip(headers, columns):
                                                        if header == headers[0]:  # Vérifier si c'est la première colonne
                                                            value = column.text.strip()
                                                            # Retirer "Progression" à la fin de la valeur de la première colonne
                                                            value = value.rsplit("Progression", 1)[0].strip()
                                                            print(f"{header} : {value}")
                                                        else:
                                                            print(f"{header} : {column.text.strip()}")
                                                print()  # Ajouter une ligne vide entre chaque ligne du tableau

async def main():
    # Appeler la fonction pour chaque lien
    url1 = "https://fr.wikipedia.org/wiki/Records_olympiques_d%27athl%C3%A9tisme"
    url2 = "https://fr.wikipedia.org/wiki/Natation_aux_Jeux_olympiques"

    process_wikipedia_page(url1)
    print("\n\n")
    process_wikipedia_page(url2)


if __name__ == "__main__":
    asyncio.run(main())
