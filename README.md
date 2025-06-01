# Sistema de Agendamento Médico

## 1. Membros do Grupo

- Vinicius Trindade Dias Abel  
- Gustavo Ferreira Dias

---

## 2. Explicação do Sistema

O **Sistema de Agendamento Médico** é uma aplicação web desenvolvida em Flask para gerenciamento de consultas médicas.  
Ele permite:
- Cadastrar médicos e pacientes.
- Agendar consultas únicas ou recorrentes.
- Listar pacientes, médicos e consultas em um calendário.
- Calcular automaticamente o valor pago considerando convênio (50% de desconto).
- Cancelar consultas e editar registros existentes.

A interface web foi construída com Bootstrap.

---

## 3. Tecnologias Utilizadas

- **Linguagem:** Python
- **Framework Web:** Flask  
- **Banco de Dados:** SQLite (via Flask-SQLAlchemy)  
- **Testes:** Pytest  
- **CI/CD:** GitHub Actions 
- **Outros:** HTML, CSS (Bootstrap), Jinja2

---

## Como rodar localmente e testar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor Flask:
   ```bash
   python run.py
   ```
   
3. Acesse no navegador:
   ```bash
   http://localhost:5000
   ```

4. Como rodar os testes:
   ```bash
   python -m pytest
   ```

5. Como conferir a cobertura dos testes:
   ```bash
   python -m coverage run -m pytest
   python -m coverage report
   ```