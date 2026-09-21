from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from database import inicializar_banco, get_conexao

app = Flask(__name__)

inicializar_banco()

def obter_dados_locacao():
    conexao = get_conexao()
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT r.id as reserva_id, r.chassi_grupo, r.prateleira, p.id as peca_id, p.codigo_peca, p.quantidade
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
                'id': linha['peca_id'],
                'codigo': linha['codigo_peca'],
                'quantidade': linha['quantidade']
            })
            
    return dados_agrupados

@app.route('/')
def index():
    dados_locacao = obter_dados_locacao()
    return render_template('index.html', dados_locacao=dados_locacao)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    chassi = request.form.get('chassi', '').strip()
    prateleira = request.form.get('prateleira', '').strip()
    codigo_peca = request.form.get('codigo_peca', '').strip()
    
    try:
        quantidade = int(request.form.get('quantidade', 0))
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        return redirect(url_for('index'))

    conexao = get_conexao()
    cursor = conexao.cursor()

    cursor.execute('SELECT id, prateleira FROM reservas WHERE chassi_grupo = ?', (chassi,))
    reserva = cursor.fetchone()

    if reserva:
        reserva_id = reserva['id']
        if reserva['prateleira'] != prateleira:
            cursor.execute('UPDATE reservas SET prateleira = ? WHERE id = ?', (prateleira, reserva_id))
    else:
        cursor.execute('INSERT INTO reservas (chassi_grupo, prateleira) VALUES (?, ?)', (chassi, prateleira))
        reserva_id = cursor.lastrowid

    cursor.execute('INSERT INTO pecas_reservadas (reserva_id, codigo_peca, quantidade) VALUES (?, ?, ?)', (reserva_id, codigo_peca, quantidade))

    conexao.commit()
    conexao.close()

    return redirect(url_for('index'))

@app.route('/apagar_chassi/<chassi>', methods=['POST'])
def apagar_chassi(chassi):
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM reservas WHERE chassi_grupo = ?', (chassi,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('index'))

@app.route('/apagar_peca/<int:peca_id>', methods=['POST'])
def apagar_peca(peca_id):
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM pecas_reservadas WHERE id = ?', (peca_id,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('index'))

@app.route('/conciliar', methods=['POST'])
def conciliar():
    arquivo = request.files.get('arquivo_nbs')
    
    if not arquivo or not arquivo.filename.lower().endswith('.xlsx'):
        return redirect(url_for('index'))

    try:
        df = pd.read_excel(arquivo, dtype={'chassi': str, 'codigo_peca': str})
    except Exception:
        return redirect(url_for('index'))

    colunas_obrigatorias = {'chassi', 'codigo_peca', 'quantidade'}
    if not colunas_obrigatorias.issubset(set(df.columns)):
        return redirect(url_for('index'))

    df = df.dropna(subset=['chassi', 'codigo_peca'])
    df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
    df = df[df['quantidade'] > 0]
    
    df_agrupado = df.groupby(['chassi', 'codigo_peca'], as_index=False)['quantidade'].sum()

    conexao = get_conexao()
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT r.chassi_grupo, p.codigo_peca, SUM(p.quantidade) 
        FROM reservas r
        JOIN pecas_reservadas p ON r.id = p.reserva_id
        GROUP BY r.chassi_grupo, p.codigo_peca
    ''')
    
    reservas_db = {}
    for linha in cursor.fetchall():
        chave = (str(linha[0]).strip(), str(linha[1]).strip())
        reservas_db[chave] = linha[2]
        
    conexao.close()

    resultados = []
    for index, linha in df_agrupado.iterrows():
        chassi_nbs = str(linha['chassi']).strip()
        codigo = str(linha['codigo_peca']).strip()
        qtd_nbs = int(linha['quantidade'])
        
        chave = (chassi_nbs, codigo)
        qtd_separada = reservas_db.get(chave, 0)
        
        falta_separar = qtd_nbs - qtd_separada
        
        resultados.append({
            'chassi': chassi_nbs,
            'codigo': codigo,
            'qtd_nbs': qtd_nbs,
            'qtd_separada': qtd_separada,
            'status': falta_separar
        })
        
    return render_template('conciliacao.html', resultados=resultados)

if __name__ == '__main__':
    app.run()