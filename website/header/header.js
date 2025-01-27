window.addEventListener("load", function() {
    let header = document.createElement("header");
    header.innerHTML = `
    <a href="../accueil/index.html"><img src="../img/jo_logo_white.png" alt="Logo des JO"></a>
    <nav><ul>
            <li><a href="../participants/index.html">Participants</a></li>
            <li><a href="../resultat/index.html">Résultats</a></li>
            <li><a href="../calendrier/index.html">Calendrier des épreuves</a></li>
            <li><a href="../lieu/index.html">Se rendre aux sites</a></li>
    </ul></nav>`
    document.body.insertBefore(header, document.body.firstChild)
});