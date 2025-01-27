window.addEventListener("load", function() {
    setTimeout(main, 400);
    buttonR = document.getElementById("bouttonR");
    buttonR.addEventListener('click', changeTable) ;
    
    let sportform = document.getElementById("sportForm");

    sportform.addEventListener('submit',function(e){
        e.preventDefault();
    });
});

function main(){
    let sportSelect = document.getElementById("sportSelect");
    for (let sportData of getSports()[0].values) {
        let opt = document.createElement('option');
        opt.value = sportData[0];
        opt.text = sportData[1];
        sportSelect.appendChild(opt);
        sportSelect.insertBefore(opt, null);
    }
    onSportSelect(sportSelect.value);

    sportSelect.addEventListener( "change", (event) => {
        onSportSelect(event.target.value);
    });

}

function onSportSelect(sport_id){
    let categorySelect = document.getElementById("categorySelect")
    for (let  i = categorySelect.options.length-1; i>=0 ;i--) {
        categorySelect.remove(i);
    }
    
    for (let sportCategorieData of getCategories({sport_id: sport_id})[0].values) {
        let opt = document.createElement('option');
        opt.value = sportCategorieData[0];
        opt.text = `${sportCategorieData[1]}, ${sportCategorieData[3]}`;
        categorySelect.appendChild(opt);
        categorySelect.insertBefore(opt, null);
    }
}

function changeTable() {
    let category_id = document.getElementById("categorySelect").value;
    let appartient_querry = `SELECT id_Sportif, id_Resultat FROM Appartient WHERE id_SportCategorie = ${category_id}`;
    let result_querry = `SELECT type_Medaille, id_Sportif, date, valeur FROM Resultat INNER JOIN (${appartient_querry}) ON Resultat.id = id_Resultat`;
    let querry = `SELECT type_Medaille, nom, date, valeur, prenom FROM (${result_querry}) INNER JOIN Sportif ON Sportif.id = id_Sportif`;
    let data = window.DB.exec(querry);
    for (let row of data[0].values) {
        row[1] = row[4] + " " + row[1];
        row.pop();
    }
    let table = createTable(data, ["Medaille", "Athlete", "Date", "Resultat"]);
    let resultTable = document.getElementById("results");
    resultTable.innerHTML= table.innerHTML;
}