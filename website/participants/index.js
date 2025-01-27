function main() {
    let sexSelect = document.getElementById("sexSelect");
    let nationaliteSelect = document.getElementById("nationaliteSelect");
    let paralympicSelect = document.getElementById("paralympicSelect");
    let opt;

    for(let vals of [[null, "H/F"], ["Homme", "Homme"], ["Femme", "Femme"]]) {
        opt = document.createElement('option');
        opt.value = vals[0];
        opt.text = vals[1];
        sexSelect.appendChild(opt);
    }
    
    for(let vals of [[null, "Tous"], [false, "Non"], [true, "Oui"]]) {
        opt = document.createElement('option');
        opt.value = vals[0];
        opt.text = vals[1];
        paralympicSelect.appendChild(opt);
    }

    opt = document.createElement('option');
    opt.value = null;
    opt.text = "Tous"
    nationaliteSelect.appendChild(opt);
    for(let pays of getData({tablename:"Pays", fields:"acronyme, nom", order_by:"nom"})[0].values) {
        opt = document.createElement('option');
        opt.value = pays[0];
        opt.text = pays[1];
        nationaliteSelect.appendChild(opt);
    }
}

function changeTable() {
    let sexSelect = document.getElementById("sexSelect");
    let nationaliteSelect = document.getElementById("nationaliteSelect");
    let paralympicSelect = document.getElementById("paralympicSelect");
    let data = getParticipants({sexe:sexSelect.value, is_paralympic:paralympicSelect.value, country:nationaliteSelect.value});
    let table = createTable(data, null, true, true, true, true);
    let resultTable = document.getElementById("liaison_bd");
    resultTable.innerHTML= `<tr>
    <th style="width: 20%;">Nom</th>
    <th style="width: 22%;">Prénom</th>
    <th style="width: 7%">Age</th>
    <th style="width: 8%;">Sexe</th>
    <th style="width: 15%;">Nationalité</th>
    <th style="width: 15%;">Paralympique?</th>
    </tr>` + table.innerHTML;
}

window.addEventListener("load", () => {
    setTimeout(main, 400);
    buttonR = document.getElementById("bouttonR");
    buttonR.addEventListener('click', changeTable) ;
    
    let athleteform = document.getElementById("athleteForm");

    athleteform.addEventListener('submit',function(e){
        e.preventDefault();
    });
});