
function main() {
    // Récupération des événements depuis la base de données
    let eventsData = getEvents();

    // Création du tableau HTML
    let table = createEventsTable(eventsData[0]);

    // Ajout du tableau au contenu de la page
    document.body.appendChild(table);
}

// Fonction pour créer un tableau HTML à partir des données d'événements
function createEventsTable(eventsData) {
    // Création de l'élément de tableau
    let table = document.createElement("table");
    
    // Ajout de la classe à l'élément de tableau
    table.classList.add("table-container");

    // Création de l'en-tête du tableau avec les noms des colonnes renommées
    let headerRow = table.insertRow();
    let columnNames = ['Discipline', 'Début', 'Fin', 'Lieu']; // Nouveaux noms de colonnes
    for (let columnName of columnNames) {
        let headerCell = document.createElement("th");
        headerCell.textContent = columnName;
        headerRow.appendChild(headerCell);
    }

    // Remplissage des données dans le tableau
    for (let rowData of eventsData.values) {
        let row = table.insertRow();
        for (let value of rowData) {
            let cell = row.insertCell();
            cell.textContent = value;
        }
    }

    return table;
}




window.addEventListener("load", () => {
    setTimeout(main, 400);
});