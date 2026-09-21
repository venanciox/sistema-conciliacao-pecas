import sqlite3

def inicializar_banco():
    conexao = sqlite3.connect('sistema_pecas.db')
    conexao.execute('PRAGMA foreign_keys = ON')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chassi_grupo TEXT NOT NULL UNIQUE,
            prateleira TEXT,
            data_separacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pecas_reservadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            codigo_peca TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            FOREIGN KEY (reserva_id) REFERENCES reservas (id) ON DELETE CASCADE
        )
    ''')

    conexao.commit()
    conexao.close()

def get_conexao():
    conexao = sqlite3.connect('sistema_pecas.db')
    conexao.execute('PRAGMA foreign_keys = ON')
    conexao.row_factory = sqlite3.Row
    return conexao

if __name__ == '__main__':
    inicializar_banco()