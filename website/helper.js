function getData(options) {
    const {
        tablename,
        fields = "*",
        where = null,
        order_by = null,
        is_acsending = true
    } = options;

    db = window.DB;
    querry = `SELECT ${fields} FROM ${tablename}`;
    if (where) {
        querry += ` WHERE ${where}`;
    }
    if (order_by) {
        querry += ` ORDER BY ${order_by} ${is_acsending ? "ASC" : "DESC"}`
    }
    console.log(querry);
    return db.exec(querry);
}

function getSports() {
    return getData({tablename: "Sport", order_by: "nom"});
}

function getEvents() {
    db = window.DB;
    querry = `SELECT Evenement.nom AS nom_evenement, Evenement.date_debut, Evenement.date_fin, Lieu.nom AS nom_lieu
                FROM Evenement
                JOIN Lieu ON Evenement.id_Lieu = Lieu.id;
         `
    return db.exec(querry);
}

function getLieux(options){
    const {
        ville_id = null,  
    } = options;

    filter = null;
    if (ville_id){
        filter = `id_Ville = ${ville_id}`
    }

    return getData({tablename: "Lieu INNER JOIN Ville on id_Ville = Ville.id", fields: "Lieu.nom, capacite, is_extern, Ville.nom", order_by: "Lieu.nom", where: filter});
}

function getCategories(options) {
    const {
        sport = null,
        sport_id = null,
        sexe = null,
        individual = null
    } = options;

    filter = [];
    if (sport_id) {
        filter.push(`id_Sport = ${sport_id}`);
    }
    if (sport && !sport_id) {
        id = getData({tablename: "Sport", where: `nom = '${sport}'`})[0].values[0][0];
        filter.push(`id_Sport = ${id}`);
    }
    if (sexe) {
        filter.push(`sexe = '${sexe}'`);
    }
    if (individual) {
        filter.push(`is_individual = ${individual ? 1 : 0}`);
    }
    if (filter.length) {
        filter = filter.join(' AND ');
    }
    else {
        filter = null;
    }
    return getData({tablename: "SportCategorie", order_by: "nom", where: filter});
}

function createTable(data, fieldnames = null, null_to_empty = true, date_to_age = false, boolToYesOrNo = false, no_header = false) {
    console.log(data);
    data = data[0];
    if (data == undefined) {
        let table = document.createElement("table");
        table.innerHTML = "<p id='no_data'>NO DATA</p>"
        return table
    }
    let table = document.createElement("table");
    if (!fieldnames) {
        fieldnames = data.columns;
    }

    if(!no_header) {
        header = document.createElement("tr");
        for (let fieldname of fieldnames) {
            header.innerHTML += `<th>${fieldname}</th>`;
        }
        table.appendChild(header);
    }

    for (let row of data.values) {
        tr = document.createElement("tr");
        for (let field of row) {
            if(boolToYesOrNo) {
                if(field == "0") {
                    field = "Non";
                } else if(field == "1"){
                    field = "Oui";
                }
            }
            if(date_to_age && field && field instanceof String && field.match(/\d{4}-[0-1]\d-[0-3]\d/)) {
                let d1 = new Date(field);
                let d2 = new Date();
                field = Math.round((d2 - d1) / (1000*60*60*24*365.25));
            }
            if (null_to_empty && field == null) {
                field = "";
            }
            tr.innerHTML += `<td>${field}</td>`;
        }
        table.appendChild(tr);
    }
    return table;
}

function getParticipants(options) {
    const {
            id_sport = null,
            id_category = null,
            sexe = null,
            country = null,
            is_paralympic = null,
        order_by = null
    } = options;

    let sport_category_join = "SELECT Sport.id AS id_sport, SportCategorie.id AS id_category FROM Sport INNER JOIN SportCategorie ON Sport.id = SportCategorie.id_Sport";
    let sport_filter = [];
    if (id_sport) {
        sport_filter.push(`Sport.id = ${id_sport}`);
    }
    if (id_category) {
        sport_filter.push(`SportCategorie.id = ${id_category}`);
    }
    if (sport_filter.length) {
        sport_category_join += ` WHERE ${sport_filter.join(" AND ")}`;
    }
    ", nom AS nom_Sportif, prenom, date_naissance, sexe, is_paralympic,"
    "id_Sportif, nom_Sportif, prenom, date_naissance, sexe, is_paralympic, "
    let pratique_join = `SELECT id_Sportif AS id_Sportif_Pratique FROM (${sport_category_join}) INNER JOIN Pratique ON id_SportCategorie = id_category`;
    let pratique_nationalite_join = `SELECT id_Sportif, acronyme_Pays FROM (${pratique_join}) INNER JOIN Nationalite ON id_Sportif_Pratique = id_Sportif`;
    
    country_select = "Pays";
    if (country && country !== "null") {
        country_select = `(SELECT nom, acronyme FROM Pays WHERE acronyme = '${country}')`;
    }
    let country_join = `SELECT id_Sportif, nom AS nom_Pays FROM (${pratique_nationalite_join}) INNER JOIN ${country_select} ON acronyme_Pays = acronyme`;
    

    let querry = `SELECT DISTINCT nom, prenom, date_naissance, sexe, nom_Pays, is_paralympic FROM (${country_join}) INNER JOIN Sportif ON id_Sportif = id`;
    let sportif_filter = [];
    if (sexe === "Homme" || sexe === "Femme") {
        sportif_filter.push(`Sportif.sexe = '${sexe}'`);
    }
    if (is_paralympic === true || is_paralympic === false) {
        sportif_filter.push(`Sportif.is_paralympic = ${is_paralympic}`);
    }
    if (sportif_filter.length) {
        querry += ` WHERE ${sportif_filter.join(" AND ")}`;
    }
    if (order_by) {
        querry += ` ORDER BY ${order_by}`;
    }
    return window.DB.exec(querry);
}