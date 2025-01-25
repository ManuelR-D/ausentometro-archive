from datetime import datetime
import sqlite3
import json
import os
import sys

# Define the schema
def create_schema(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Representative (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            position TEXT NOT NULL,
            img_url TEXT,
            info_url TEXT,
            UNIQUE(id, name)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Party (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            UNIQUE(id, name)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Subject (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            UNIQUE(id, name)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Province (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            UNIQUE(id, name)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Vote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            representative_id INTEGER NOT NULL,
            party_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            province_id INTEGER NOT NULL,
            vote TEXT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (representative_id) REFERENCES Representative(id),
            FOREIGN KEY (party_id) REFERENCES Party(id),
            FOREIGN KEY (subject_id) REFERENCES Subject(id),
            FOREIGN KEY (province_id) REFERENCES Province(id)
        )
    ''')

    for i in range(2005, 2026):
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS SummarizedVote{i} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                representative_id INTEGER NOT NULL,
                representative_name TEXT NOT NULL,
                representative_position TEXT NOT NULL,
                representative_info_url TEXT NOT NULL,
                representative_img_url TEXT NOT NULL,
                party_name TEXT NOT NULL,
                province_name TEXT NOT NULL,
                last_vote_date DATE,
                afirmativo_count INTEGER NOT NULL,
                negativo_count INTEGER NOT NULL,
                ausente_count INTEGER NOT NULL,
                abstencion_count INTEGER NOT NULL,
                total_votes INTEGER NOT NULL,
                ausente_days_count INTEGER NOT NULL,
                FOREIGN KEY (representative_id) REFERENCES Representative(id)
            )
        ''')
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SummarizedVoteByProvince (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            province_id INTEGER NOT NULL,
            province_name TEXT NOT NULL,
            last_vote_date DATE NOT NULL,
            position TEXT NOT NULL,
            afirmativo_count INTEGER NOT NULL,
            negativo_count INTEGER NOT NULL,
            ausente_count INTEGER NOT NULL,
            abstencion_count INTEGER NOT NULL,
            total_votes INTEGER NOT NULL,
            FOREIGN KEY (province_id) REFERENCES Province(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SummarizedVoteByParty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER NOT NULL,
            party_name TEXT NOT NULL,
            position TEXT NOT NULL,
            last_vote_date DATE NOT NULL,
            afirmativo_count INTEGER NOT NULL,
            negativo_count INTEGER NOT NULL,
            ausente_count INTEGER NOT NULL,
            abstencion_count INTEGER NOT NULL,
            total_votes INTEGER NOT NULL,
            FOREIGN KEY (party_id) REFERENCES Party(id)
        )
    ''')

# Insert data into the database
def insert_data(cursor, data, position):
    for representative in data:
        # Get or insert into Representative table
        cursor.execute('''
            SELECT id FROM Representative WHERE name = ?
        ''', (representative['name'],))
        result = cursor.fetchone()
        if result:
            representative_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Representative (name, position, img_url, info_url)
                VALUES (?, ?, ?, ?)
            ''', (representative['name'], position, representative['img_url'], representative['info_url']))
            representative_id = cursor.lastrowid

        # Get or insert into Party table
        cursor.execute('''
            SELECT id FROM Party WHERE name = ?
        ''', (representative['party'],))
        result = cursor.fetchone()
        if result:
            party_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Party (name)
                VALUES (?)
            ''', (representative['party'],))
            party_id = cursor.lastrowid

        # Get or insert into Subject table
        cursor.execute('''
            SELECT id FROM Subject WHERE name = ?
        ''', (representative['subject'],))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Subject (name)
                VALUES (?)
            ''', (representative['subject'],))
            subject_id = cursor.lastrowid

        if representative['province'] == "Capital Federal":
            representative['province'] = "C.A.B.A."
        # Get or insert into Province table
        cursor.execute('''
            SELECT id FROM Province WHERE name = ?
        ''', (representative['province'],))
        result = cursor.fetchone()
        if result:
            province_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Province (name)
                VALUES (?)
            ''', (representative['province'],))
            province_id = cursor.lastrowid

        # Convert date to YYYY-MM-DD format
        try: 
            date = datetime.strptime(representative['date'][:10], '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            print(f"Error parsing date for {representative['name']}: {representative['date']}")
            # default to minimum date
            date = datetime.min.date().isoformat()

        # Insert into Vote table
        cursor.execute('''
            INSERT INTO Vote (representative_id, party_id, subject_id, province_id, vote, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (representative_id, party_id, subject_id, province_id, representative['vote'], date))

def summarize_data(cursor):
    summarized_votes_list = []
    for i in range(2005, 2026):
        print("summarizing year ", i)
        cursor.execute(f'''
            SELECT 
                Representative.id, 
                Representative.name, 
                Representative.position, 
                Representative.info_url, 
                Representative.img_url, 
                (SELECT Party.name 
                FROM Vote 
                JOIN Party ON Party.id = Vote.party_id 
                WHERE Vote.representative_id = Representative.id 
                ORDER BY Vote.date DESC 
                LIMIT 1) AS party_name, 
                (SELECT Province.name
                FROM Vote 
                JOIN Province ON Province.id = Vote.province_id 
                WHERE Vote.representative_id = Representative.id 
                ORDER BY Vote.date DESC 
                LIMIT 1) AS province_name, 
                (SELECT Vote.date
                FROM Vote 
                WHERE Vote.representative_id = Representative.id 
                ORDER BY Vote.date DESC 
                LIMIT 1) AS last_vote_date, 
                SUM(CASE WHEN Vote.vote = 'AFIRMATIVO' THEN 1 ELSE 0 END) AS afirmativo_count,
                SUM(CASE WHEN Vote.vote = 'NEGATIVO' THEN 1 ELSE 0 END) AS negativo_count,
                SUM(CASE WHEN Vote.vote = 'AUSENTE' THEN 1 ELSE 0 END) AS ausente_count,
                SUM(CASE WHEN Vote.vote = 'ABSTENCION' THEN 1 ELSE 0 END) AS abstencion_count,
                COUNT(*) AS total_votes,
                COUNT(DISTINCT CASE WHEN Vote.vote = 'AUSENTE' THEN Vote.date ELSE NULL END) AS ausente_days_count
            FROM Vote
            JOIN Representative ON Representative.id = Vote.representative_id
            WHERE Vote.date BETWEEN '{i}-01-01' AND '{i}-12-31'  
            GROUP BY Representative.id
        ''')
        summarized_votes = cursor.fetchall()
        print("inserting summarized votes for year ", i)
        cursor.executemany(f'''
        INSERT INTO SummarizedVote{i} (representative_id, representative_name, representative_position, representative_info_url, representative_img_url, party_name, province_name, last_vote_date, afirmativo_count, negativo_count, ausente_count, abstencion_count, total_votes, ausente_days_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', summarized_votes)

    print("summarizing votes by party")
    cursor.execute('''
        SELECT 
            Party.id,
            Party.name,
            (SELECT Vote.date
             FROM Vote 
             WHERE Vote.party_id = Party.id 
             ORDER BY Vote.date DESC 
            LIMIT 1) AS last_vote_date, 
            Representative.position as position,
            SUM(CASE WHEN Vote.vote = 'AFIRMATIVO' THEN 1 ELSE 0 END) AS afirmativo_count,
            SUM(CASE WHEN Vote.vote = 'NEGATIVO' THEN 1 ELSE 0 END) AS negativo_count,
            SUM(CASE WHEN Vote.vote = 'AUSENTE' THEN 1 ELSE 0 END) AS ausente_count,
            SUM(CASE WHEN Vote.vote = 'ABSTENCION' THEN 1 ELSE 0 END) AS abstencion_count,
            COUNT(*) AS total_votes
        FROM Vote
        JOIN Party ON Party.id = Vote.party_id
        JOIN Representative ON Representative.id = Vote.representative_id
        GROUP BY Party.id
                   ''')
    summarized_votes = cursor.fetchall()
    
    print("inserting summarized votes by party")
    cursor.executemany('''
        INSERT INTO SummarizedVoteByParty (party_id, party_name, last_vote_date, position, afirmativo_count, negativo_count, ausente_count, abstencion_count, total_votes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', summarized_votes)


    print("summarizing votes by province")
    cursor.execute('''
        SELECT 
            Province.id,
            Province.name,
            (SELECT Vote.date
             FROM Vote 
             WHERE Vote.province_id = Province.id 
             ORDER BY Vote.date DESC 
            LIMIT 1) AS last_vote_date, 
            Representative.position as position,
            SUM(CASE WHEN Vote.vote = 'AFIRMATIVO' THEN 1 ELSE 0 END) AS afirmativo_count,
            SUM(CASE WHEN Vote.vote = 'NEGATIVO' THEN 1 ELSE 0 END) AS negativo_count,
            SUM(CASE WHEN Vote.vote = 'AUSENTE' THEN 1 ELSE 0 END) AS ausente_count,
            SUM(CASE WHEN Vote.vote = 'ABSTENCION' THEN 1 ELSE 0 END) AS abstencion_count,
            COUNT(*) AS total_votes
        FROM Vote
        JOIN Province ON Province.id = Vote.province_id
        JOIN Representative ON Representative.id = Vote.representative_id
        GROUP BY Province.id
                     ''')
    summarized_votes = cursor.fetchall()
    
    print("inserting summarized votes by province")
    cursor.executemany('''
        INSERT INTO SummarizedVoteByProvince (province_id, province_name, last_vote_date, position, afirmativo_count, negativo_count, ausente_count, abstencion_count, total_votes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', summarized_votes)

def main():
    create_representatives_db()
    create_caba_representatives_db()

def create_caba_representatives_db():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_file_name = f'./caba_representatives{timestamp}.db'

    print(db_file_name)
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    create_schema(cursor)

    print("Adding legislator data to database...")
    add_caba_legislators(cursor)
    print(f"Summarizing data...")
    summarize_data(cursor=cursor)

    conn.commit()
    conn.close()

def add_caba_legislators(cursor):
    folder_path = './caba'
    representatives = []
    enrichment_data = {}
    with open("diputados_caba.json", 'r', encoding='utf-8') as json_file:
        enrichment_data = json.load(json_file)
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                votacion_expediente = data['votacion_expediente']
                votes = data['votes']
                    
                for vote in votes:
                    if (vote['voto'] == 'NO VOTÓ'):
                        vote['voto'] = 'AUSENTE'
                    
                    id_legislador = vote['id_legislador']
                    img_url = [x['img_url'] for x in enrichment_data if x['id_legislador'] == id_legislador][0]
                    url_legislador = [x['url_legislador'] for x in enrichment_data if x['id_legislador'] == id_legislador][0]
                    representative = {
                        'name': f"{vote['nombre']} {vote['apellido']}",
                        'party': vote['bloque'],
                        'subject': votacion_expediente['asunto'],
                        'province': 'C.A.B.A.',
                        'vote': vote['voto'],
                        'date': votacion_expediente['fch_sesion'].split(' ')[0],
                        'img_url': img_url,
                        'info_url': url_legislador
                    }
                    if (representative['party'] is None):
                        representative['party'] = "Sin Bloque"
                    
                    if (representative['subject'] is None):
                        representative['subject'] = "NO SE ESPECIFICA"

                    representatives.append(representative)
    # Insert data
    insert_data(cursor, representatives, "Legislador CABA")

def create_representatives_db():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_file_name = f'./representatives{timestamp}.db'

    print(db_file_name)
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    create_schema(cursor)

    print("Adding senator data to database...")
    add_senadores(cursor)
    print("Adding deputies data to database...")
    add_diputados(cursor)
    print(f"Summarizing data...")
    summarize_data(cursor=cursor)

    conn.commit()
    conn.close()

def add_senadores(cursor):
    with open('senators_20250120_004148.json', 'r', encoding='latin-1') as json_file:
        data = json.load(json_file)

    data = enrich_data(data)
    # Insert data
    insert_data(cursor, data, "Senador")

def add_diputados(cursor):
    with open('diputados_20250120_162406.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Enrich data with image URLs
    data = enrich_data(data)
    # Insert data
    insert_data(cursor, data, "Diputado")

def enrich_data(data):
    with open('results2.json', 'r', encoding='latin-1') as json_file:
        results = json.load(json_file)
        for representative in data:
            representative['img_url'] = results.get(representative['name'], "")
    
    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sqliteIngestor.py <database_type>")
        sys.exit(1)

    database_type = sys.argv[1]

    if database_type == "nacion":
        create_representatives_db()
    elif database_type == "caba":
        create_caba_representatives_db()
    elif database_type == "all":
        main()
    else:
        print("Invalid database type. Use 'representatives' or 'caba_representatives'.")
        sys.exit(1)