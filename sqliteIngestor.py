from datetime import datetime
import sqlite3
import json

# Define the schema
def create_schema(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Senator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
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
            senator_id INTEGER NOT NULL,
            party_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            province_id INTEGER NOT NULL,
            vote TEXT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (senator_id) REFERENCES Senator(id),
            FOREIGN KEY (party_id) REFERENCES Party(id),
            FOREIGN KEY (subject_id) REFERENCES Subject(id),
            FOREIGN KEY (province_id) REFERENCES Province(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SummarizedVote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            senator_id INTEGER NOT NULL,
            senator_name TEXT NOT NULL,
            senator_info_url TEXT NOT NULL,
            senator_img_url TEXT NOT NULL,
            party_name TEXT NOT NULL,
            province_name TEXT NOT NULL,
            last_vote_date DATE,
            afirmativo_count INTEGER NOT NULL,
            negativo_count INTEGER NOT NULL,
            ausente_count INTEGER NOT NULL,
            abstencion_count INTEGER NOT NULL,
            total_votes INTEGER NOT NULL,
            ausente_days_count INTEGER NOT NULL,
            FOREIGN KEY (senator_id) REFERENCES Senator(id)
        )
    ''')

def insert_data(cursor, data):
    for senator in data:
        cursor.execute('''
            SELECT id FROM Senator WHERE name = ?
        ''', (senator['name'],))
        result = cursor.fetchone()
        if result:
            senator_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Senator (name, img_url, info_url)
                VALUES (?, ?, ?)
            ''', (senator['name'], senator['img_url'], senator['info_url']))
            senator_id = cursor.lastrowid

        cursor.execute('''
            SELECT id FROM Party WHERE name = ?
        ''', (senator['party'],))
        result = cursor.fetchone()
        if result:
            party_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Party (name)
                VALUES (?)
            ''', (senator['party'],))
            party_id = cursor.lastrowid

        cursor.execute('''
            SELECT id FROM Subject WHERE name = ?
        ''', (senator['subject'],))
        result = cursor.fetchone()
        if result:
            subject_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Subject (name)
                VALUES (?)
            ''', (senator['subject'],))
            subject_id = cursor.lastrowid

        cursor.execute('''
            SELECT id FROM Province WHERE name = ?
        ''', (senator['province'],))
        result = cursor.fetchone()
        if result:
            province_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO Province (name)
                VALUES (?)
            ''', (senator['province'],))
            province_id = cursor.lastrowid

        try: 
            date = datetime.strptime(senator['date'][:10], '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            raise

        cursor.execute('''
            INSERT INTO Vote (senator_id, party_id, subject_id, province_id, vote, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (senator_id, party_id, subject_id, province_id, senator['vote'], date))

def summarize_data(cursor):
    cursor.execute('''
        SELECT 
            Senator.id, 
            Senator.name, 
            Senator.info_url, 
            Senator.img_url, 
            (SELECT Party.name 
             FROM Vote 
             JOIN Party ON Party.id = Vote.party_id 
             WHERE Vote.senator_id = Senator.id 
             ORDER BY Vote.date DESC 
             LIMIT 1) AS party_name, 
            (SELECT Province.name
             FROM Vote 
             JOIN Province ON Province.id = Vote.province_id 
             WHERE Vote.senator_id = Senator.id 
             ORDER BY Vote.date DESC 
             LIMIT 1) AS province_name, 
            (SELECT Vote.date
             FROM Vote 
             WHERE Vote.senator_id = Senator.id 
             ORDER BY Vote.date DESC 
             LIMIT 1) AS last_vote_date, 
            SUM(CASE WHEN Vote.vote = 'AFIRMATIVO' THEN 1 ELSE 0 END) AS afirmativo_count,
            SUM(CASE WHEN Vote.vote = 'NEGATIVO' THEN 1 ELSE 0 END) AS negativo_count,
            SUM(CASE WHEN Vote.vote = 'AUSENTE' THEN 1 ELSE 0 END) AS ausente_count,
            SUM(CASE WHEN Vote.vote = 'ABSTENCION' THEN 1 ELSE 0 END) AS abstencion_count,
            COUNT(*) AS total_votes,
            COUNT(DISTINCT CASE WHEN Vote.vote = 'AUSENTE' THEN Vote.date ELSE NULL END) AS ausente_days_count
        FROM Vote
        JOIN Senator ON Senator.id = Vote.senator_id
        GROUP BY Senator.id
    ''')
    summarized_votes = cursor.fetchall()
    for vote in summarized_votes:
        cursor.execute('''
            INSERT INTO SummarizedVote (senator_id, senator_name, senator_info_url, senator_img_url, party_name, province_name, last_vote_date, afirmativo_count, negativo_count, ausente_count, abstencion_count, total_votes, ausente_days_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', vote)

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_file_name = f'./senators{timestamp}.db'

    print(db_file_name)
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    create_schema(cursor)

    with open('senators_20250119_205841.json', 'r', encoding='latin-1') as json_file:
        data = json.load(json_file)

    insert_data(cursor, data, conn)
    summarize_data(cursor=cursor)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()