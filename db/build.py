import sqlite3 as sql
import asyncio

from scrapper_script.result import main as result_main
from scrapper_script.athlete_data import main as athlete_main
from scrapper_script.record_script import main as record_main #do not use yet, script not done

async def main():
    con = sql.connect("./jo2024.sqlite")
    for script_name in ("groupe_NPC", "static", "sport_categories"): # Orders matter
        with open(f"./db/sql_script/{script_name}.sql", encoding="UTF-8") as sql_script:
            print(f"Executed {script_name}.sql")
            con.executescript(sql_script.read())
            con.commit()
    con.close()
    await athlete_main()
    await result_main()

if __name__ == "__main__":
    asyncio.run(main())