if (!window.DB) {
    initSqlJs({
        locateFile: filename => `http://localhost:8000/sqljs-wasm/${filename}`
    }).then(sqlJs => {
        fetch('http://localhost:8000/jo2024.sqlite')
        .then(response => response.arrayBuffer())
        .then(buffer => {
            window.DB = new sqlJs.Database(new Uint8Array(buffer));
            console.log("Database loaded successfully.");
        })
        .catch(error => {
            console.error("Error loading database:", error);
        });
    })
}