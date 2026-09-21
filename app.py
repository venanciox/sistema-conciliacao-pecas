from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def obter_dados_locacao():
    conexao = sqlite3.connect('sistema_pecas.db')
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT r.id, r.chassi_grupo, r.prateleira, p.codigo_peca, p.quantidade
        FROM reservas r
        LEFT JOIN pecas_reservadas p ON r.id = p.reserva_id
    ''')
    linhas = cursor.fetchall()
    conexao.close()

    dados_agrupados = {}
    for linha in linhas:
        chassi = linha['chassi_grupo']
        if chassi not in dados_agrupados:
            dados_agrupados[chassi] = {
                'prateleira': linha['prateleira'],
                'pecas': []
            }
        if linha['codigo_peca']:
            dados_agrupados[chassi]['pecas'].append({
                'codigo': linha['codigo_peca'],
                'quantidade': linha['quantidade']
            })
            
    return dados_agrupados

@app.route('/')
def index():
    dados_locacao = obter_dados_locacao()
    return render_template('index.html', dados_locacao=dados_locacao)

if __name__ == '__main__':
    app.run(debug=True)