# Sistema de Conciliação de Peças

Aplicação web desenvolvida em Python e Flask para o controle de peças automotivas separadas por chassi e prateleira, realizando a conciliação automatizada com relatórios gerados pelo sistema NBS.

## Funcionalidades

- Cadastro estruturado de chassis e registro de peças separadas por localidade (prateleira).
- Modificação dinâmica de prateleira na adição de novas peças a um chassi existente.
- Deleção em cascata (remoção do chassi limpa todas as peças associadas no banco).
- Importação de relatórios de estoque do NBS via arquivos `.xlsx`.
- Motor de conciliação que agrega quantidades duplicadas, valida dados ausentes e cruza o arquivo físico com o banco de dados.
- Dashboard indicativo do status do chassi (Completo, Faltante, Excedente).

## Tecnologias

- **Backend:** Python, Flask
- **Banco de Dados:** SQLite (com Foreign Keys e integridade referencial ativadas)
- **Processamento de Dados:** Pandas
- **Frontend:** HTML5, CSS3, Jinja2

## Como executar

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute o servidor: `python app.py`
4. Acesse via navegador local. O banco de dados (`sistema_pecas.db`) será gerado automaticamente na primeira execução, preservando as regras de segurança estipuladas no `.gitignore`.