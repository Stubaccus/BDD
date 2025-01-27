function main() {
  let villeSelect = document.getElementById("villeSelect");
  let opt;

  opt = document.createElement('option');
  opt.value = null;
  opt.text = "Tous"
  villeSelect.appendChild(opt);
  for(let ville of getData({tablename: "Ville", fields: "id, nom"})[0].values) {
      opt = document.createElement('option');
      opt.value = ville[0];
      opt.text = ville[1];
      villeSelect.appendChild(opt);
  }
}

function changeTable() {
  let villeSelect = document.getElementById("villeSelect");
  let data = getLieux({sexe:villeSelect.value});
  let table = createTable(data, ["Lieu", "Capacité", "Extérieur", "Ville", "Transport"], true, true, true, false);
  let resultTable = document.getElementById("lieuTableBody");
  resultTable.innerHTML= table.innerHTML;
}

window.addEventListener("load", () => {
  setTimeout(main, 400);
  buttonR = document.getElementById("bouttonR");
  buttonR.addEventListener('click', changeTable) ;
  
  let form = document.getElementById("lieuForm");

  form.addEventListener('submit',function(e){
      e.preventDefault();
  });
});
