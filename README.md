 Migration CSV vers MongoDB

                                                I. Description du projet 

Ce projet permet de migrer un fichier CSV contenant des données médicales vers une base de données MongoDB, tout en assurant l’intégrité des données et en exportant les données migrées dans un nouveau CSV.
Le script automatise le flux complet : lecture du CSV → nettoyage → vérification → migration → intégrité → index → export.

                                              II. Description du script python pour import (import_csv_to_mongodb.py)

Fonctionnalités principales

1. Configuration et authentification: cette étape permet de définir l'URI de connexion à Mongodb, le port sur lequel mondodb écoute de puis le conteneur et permet aussi d'attribut des coordonnées de connexion (USER, PASSWORD) et un rôle (readwrite) au script python.

               CSV_FILE = "dhealthcare_dataset.csv"  # fichier CSV source

               DB_NAME = os.getenv("MONGO_DB", "Medical_db") # nom de la base de données

               COLLECTION_NAME = "Patients"             # nom de la collection

               MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource={DB_NAME}"

2. Nettoyage et normalisation des données

        - Suppression des doublons.

        - Normalisation des noms des patients et des docteurs (Name, Doctor) avec majuscule sur chaque mot. (dans le csv original les valeurs de Name et Doctor ont   parfois la syntaxe EMmaNueL KeITa)

        - Conversion des colonnes de dates (Date of Admission, Discharge Date) en type datetime. (dans le csv original, ses deux attributs sont de type string)

3. Vérification de l’intégrité avant migration: Affichage des colonnes disponibles; Détection des doublons et valeurs manquantes dans le DataFrame.

4. Migration vers MongoDB

           Connexion à MongoDB local; Création de la base et de la collection si nécessaire; Insertion des lignes du DataFrame dans MongoDB après suppression éventuelle de la collection existante.

5. Vérification de l’intégrité après migration: Nombre de documents; Détection des doublons ; Valeurs manquantes par champ, champs disponibles.


6. Création des index:  Index sur Name, Doctor et Date of Admission pour accélérer les recherches.

7. CRUD basique:  Fonctions pour créer, lire, mettre à jour et supprimer des documents dans MongoDB.

8. Export des données depuis MongoDB: Exporte la collection MongoDB dans un fichier CSV, créé automatiquement si inexistant.

9. Flux d’exécution (main): Lorsque le script est exécuté directement :Lecture et nettoyage du CSV; Vérification de l’intégrité avant migration; Migration vers MongoDB; Vérification de l’intégrité avant et  après migration; Création des index; Export des données dans export_patients.csv; Affichage d’un message indiquant la fin de la 
migration. On constate déjà l'automatisation des tests avec les fonctions créé et leurs appels dans le ---Int--- définit dans le script python.


                                                       III. Authentification et utilisateurs MongoDB

Pour sécuriser l'accès à la base MongoDB, une authentification est activée. Voici les détails :

Le projet utilise plusieurs utilisateurs MongoDB avec des rôles spécifiques :

1. adminuser1 et adminuser2 : utilisateurs administrateurs (rôle root), avec droits complets sur toutes les bases.

2. migrateUser : utilisateur utilisé par le script Python pour migrer les données, avec les droits lecture/écriture (readWrite) sur la base Medical_db.

3. readOnlyUser : utilisateur pour consultation seule en lecture sur la base.

Le fichier mongo-init.js contient les commandes de création de ces utilisateurs avec leurs rôles.

Le script Python utilise les variables d’environnement MONGO_USER, MONGO_PASSWORD, MONGO_DB pour se connecter à MongoDB avec l’utilisateur approprié.

Le script est configuré pour se connecter de manière sécurisée avec authentification via cet utilisateur, ce qui assure un contrôle d’accès fiable.

                 


                                                                       IV. Prérequis

1. Python 3.8 ou supérieur

2. MongoDB installé localement

3. Modules Python : pandas; pymongo 

                                                                  V. Fichiers du projet

1. import_csv_to_mongodb.py : script principal de migration.

2. dhealthcare_dataset.csv : fichier CSV contenant les données médicales.

3. Dockerfile  : création d'image pour script python.

4. Docker-compose: stack contenant l'image script python et l'image mongo.

4. requirements.txt : liste des modules Python nécessaires.

                                                                         VI. Utilisation 

                                                                                   VI.1. Conteneur et migration

1. Ouvre le terminal ou CMD dans le dossier  du projet.

2. Vérifie que les packages nécessaires sont installés : pip install pandas pymongo

3. Lancer la création du stack et la migration: docker-compose up --build

4. Surveiller la sortie console pour vérifier  la confirmation de l’insertion. la phrase de fin d'insertion devra s'afficher

                                                                                   VI.2 Se placer dans le conteneur et se connecter à la BD

1. Se placer dans le dossier du projet.

2. taper mongosh

3. pour se connecter à la bd avec authentification taper par exemple "docker exec -it mongodb mongo -u migrateUser -p MigratePass123! --authenticationDatabase Medical_db
                            

                                                                VII.  SCHEMAS DE LA BASE DE  DONNEES: DICTIONNAIRE DE DONNEES

Le jeux de données  "dhealthcare_dataset.csv" contient les champs suivants:


| Champ               | Type    | Description                                                                 |
|--------------------|---------|-----------------------------------------------------------------------------|
| Name               | String  | Nom des patients                                                           |
| Age                | Integer | Âge du patient                                                             |
| Gender             | String  | Genre du patient                                                          |
| Blood Type         | String  | Groupe sanguin du patient                                                 |
| Medical Condition  | String  | Condition médicale du patient (ex. Cancer, Diabète)                        |
| Date of Admission  | Date    | Date d’admission à l’hôpital                                              |
| Hospital           | String  | Hôpital où le patient a été admis                                         |
| Insurance Provider | String  | Nom de la compagnie assurant le patient                                   |
| Billing Amount     | Float   | Frais de santé payés par le patient                                       |
| Room Number        | Integer | Numéro de chambre dans laquelle le patient est hospitalisé                |
| Admission Type     | String  | Type d’admission du patient (ex. Urgence)                      |
| Discharge Date     | Date    | Date de sortie / fin d’hospitalisation                                     |
| Medication         | String  | Ordonnance prescrite par le docteur au patient                             |
| Test Results       | String  | Résultats des examens de santé du patient                                  |
| Doctor             | String  | Nom du docteur qui s’est occupé(e) du patient                              |


                                                                    VIII. Tests automatisés (supplementaire)

Vérifie : colonnes disponibles, doublons, format des noms, conversion des dates, migration complète vers MongoDB et création des index.

                                                  TAPER  python test_migration.py dans le CMD