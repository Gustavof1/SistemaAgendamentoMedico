import pytest
import threading
import time
from app import create_app
from app.database import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

@pytest.fixture(scope="module")
def app_for_system_tests():
    """Fixture que cria a aplicação e pré-popula o banco de dados para os testes de UI."""
    app = create_app()
    app.config.update({"TESTING": True, "SERVER_NAME": "localhost:5001"})
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Pré-popula o banco com um médico e um paciente para o teste de agendamento
        d = Doctor(first_name="Dr. Exemplo", last_name="Interface", email="ui@email.com", specialty="UI/UX", clinic_address="Rua do Teste")
        p = Patient(first_name="Paciente", last_name="Selenium", phone="12345", address="Av. Browser", email="paciente@ui.com", has_insurance=True)
        db.session.add_all([d, p])
        db.session.commit()

    return app

@pytest.fixture(scope="module")
def live_server(app_for_system_tests):
    """Inicia a aplicação Flask em uma thread separada para que o navegador possa acessá-la."""
    server_thread = threading.Thread(target=app_for_system_tests.run, kwargs={"port": 5001})
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1) 
    yield

@pytest.fixture(scope="module")
def browser():
    """Inicializa e finaliza o navegador Firefox para os testes."""
    service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)    
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# --- TESTES DE SISTEMA (E2E) ---

def test_system_register_patient_and_verify_on_list(live_server, browser):
    """
    Simula um usuário cadastrando um novo paciente através da interface web.
    1. Navega até o formulário de cadastro de paciente.
    2. Preenche todos os campos do formulário.
    3. Clica no botão para cadastrar.
    4. Aguarda o redirecionamento para a lista de pacientes.
    5. Verifica se o nome e o email do novo paciente estão na tabela.
    """
    # 1. Navega para a página
    browser.get("http://localhost:5001/form/patient")

    # 2. Preenche o formulário
    browser.find_element(By.NAME, "first_name").send_keys("Maria")
    browser.find_element(By.NAME, "last_name").send_keys("Navegador")
    browser.find_element(By.NAME, "phone").send_keys("3199998888")
    browser.find_element(By.NAME, "address").send_keys("Avenida dos Testes, 123")
    browser.find_element(By.NAME, "email").send_keys("maria.nav@teste.com")
    browser.find_element(By.ID, "has_insurance").click() # Marca o checkbox de convênio

    # 3. Clica no botão de cadastro
    browser.find_element(By.CSS_SELECTOR, "button.btn-primary").click()

    # 4. Aguarda o redirecionamento
    WebDriverWait(browser, 10).until(EC.url_contains("/patients"))
    
    # 5. Verifica se o paciente novo está na página
    page_content = browser.page_source
    assert "Maria Navegador" in page_content
    assert "maria.nav@teste.com" in page_content
    assert "Sim" in page_content # Verifica se o convênio foi marcado como "Sim"