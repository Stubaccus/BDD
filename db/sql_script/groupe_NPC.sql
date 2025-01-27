DROP TABLE IF EXISTS Sport;
DROP TABLE IF EXISTS Pays;
DROP TABLE IF EXISTS Sportif;
DROP TABLE IF EXISTS SportCategorie;
DROP TABLE IF EXISTS Lieu;
DROP TABLE IF EXISTS Medaille;
DROP TABLE IF EXISTS Epreuve;
DROP TABLE IF EXISTS Transport;
DROP TABLE IF EXISTS Ville;
DROP TABLE IF EXISTS Resultat;
DROP TABLE IF EXISTS Pratique;
DROP TABLE IF EXISTS Nationalite;
DROP TABLE IF EXISTS TransportLieu;
DROP TABLE IF EXISTS Appartient;
DROP TABLE IF EXISTS Evenement;

CREATE TABLE Sport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT UNIQUE,
    nom_anglais TEXT,
    date_creation DATE,
    is_paralympic BOOLEAN
);

CREATE TABLE Pays (
    acronyme TEXT PRIMARY KEY UNIQUE,
    nom TEXT UNIQUE,
    drapeau TEXT
);

CREATE TABLE Sportif (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    date_naissance DATE,
    sexe TEXT,
    is_paralympic BOOLEAN,
    is_participating BOOLEAN
);

CREATE TABLE SportCategorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    nom_anglais TEXT,
    sexe TEXT,
    is_individual BOOLEAN,
    id_Sport INTEGER,
    FOREIGN KEY (id_Sport) REFERENCES Sport(id) ON DELETE CASCADE
);

CREATE TABLE Lieu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    adresse TEXT,
    capacite INTEGER,
    is_extern BOOLEAN,
    id_Ville INTEGER,
    FOREIGN KEY (id_Ville) REFERENCES Ville(id) ON DELETE CASCADE
);

CREATE TABLE Medaille (
    type TEXT PRIMARY KEY UNIQUE
);

CREATE TABLE Epreuve (
    nom TEXT PRIMARY KEY,
    date DATE,
    id_SportCategorie INTEGER,
    id_Lieu INTEGER,
    FOREIGN KEY (id_SportCategorie) REFERENCES SportCategorie(id) ON DELETE CASCADE,
    FOREIGN KEY (id_Lieu) REFERENCES Lieu(id) ON DELETE CASCADE
);

CREATE TABLE Transport (
    nom TEXT PRIMARY KEY
);

CREATE TABLE Ville (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    code_postal DATE,
    nom_Pays TEXT,
    FOREIGN KEY (nom_Pays) REFERENCES Pays(nom) ON DELETE CASCADE
);

CREATE TABLE Resultat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    unite TEXT,
    valeur TEXT,
    is_record BOOLEAN,
    type_Medaille TEXT,
    FOREIGN KEY (type_Medaille) REFERENCES Medaille(type) ON DELETE CASCADE
);

CREATE TABLE Pratique (
    id_Sportif INTEGER,
    id_SportCategorie INTEGER,
    PRIMARY KEY (id_Sportif, id_SportCategorie),
    FOREIGN KEY (id_Sportif) REFERENCES Sportif(id) ON DELETE CASCADE,
    FOREIGN KEY (id_SportCategorie) REFERENCES SportCategorie(id) ON DELETE CASCADE
);

CREATE TABLE Nationalite (
    id_Sportif INTEGER,
    acronyme_Pays TEXT,
    is_representing_Nationalite BOOLEAN,
    PRIMARY KEY (id_Sportif, acronyme_Pays),
    FOREIGN KEY (id_Sportif) REFERENCES Sportif(id) ON DELETE CASCADE,
    FOREIGN KEY (acronyme_Pays) REFERENCES Pays(acronyme) ON DELETE CASCADE
);

CREATE TABLE TransportLieu (
    nom_Transport TEXT,
    id_Lieu INTEGER,
    PRIMARY KEY (nom_Transport, id_Lieu),
    FOREIGN KEY (nom_Transport) REFERENCES Transport(nom_Transport) ON DELETE CASCADE,
    FOREIGN KEY (id_Lieu) REFERENCES Lieu(id) ON DELETE CASCADE
);

CREATE TABLE Appartient (
    id_Resultat INTEGER,
    id_Sportif INTEGER,
    id_SportCategorie INTEGER,
    PRIMARY KEY (id_Resultat, id_Sportif, id_SportCategorie),
    FOREIGN KEY (id_Resultat) REFERENCES Resultat(id) ON DELETE CASCADE,
    FOREIGN KEY (id_Sportif) REFERENCES Sportif(id) ON DELETE CASCADE,
    FOREIGN KEY (id_SportCategorie) REFERENCES SportCategorie(id) ON DELETE CASCADE
);

CREATE TABLE Evenement (
    nom TEXT PRIMARY KEY,
    date_debut DATE,
    date_fin DATE,
    id_Lieu INTEGER,
    FOREIGN KEY (id_Lieu) REFERENCES Lieu(id) ON DELETE CASCADE
);