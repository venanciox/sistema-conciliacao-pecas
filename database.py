import sqlite3

def inicializar_banco():
    conexao = sqlite3.connect('sistema_pecas.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chassi_grupo TEXT NOT NULL,
            prateleira TEXT,
            data_separacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pecas_reservadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            codigo_peca TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (reserva_id) REFERENCES reservas (id)
        )
    ''')

    conexao.commit()
    conexao.close()

if __name__ == '__main__':
    inicializar_banco()