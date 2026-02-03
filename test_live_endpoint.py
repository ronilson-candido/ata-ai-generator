#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the live transcription endpoint"""

import requests
import json

# Test data
test_transcription = """
O que voce esta fazendo. Nao. Para mostrar os avancos ali na semana que a gente teve um projeto. 
Tem atividades concluidas. A questao ali e das funcoes do simulador, as funcoes que a biblioteca pedia para o usuario implementar foram implementadas.
Entao todas as funcoes necessarias no momento que foram implementadas, algumas delas.
O equipamento que esta sendo simulado.

Depois que eu me tentei isso, eu vi aqui o codigo esta assim, por enquanto.
O negocio que ele faz, ele pega ali o sistema e os binarios.
Depois ele coloca os enderecos que estao no file system, nessa extract que eu criei.

E, no inicio, ele coloca aqui nessa funcao aqui para ler os restantes dos arquivos que estao aqui.
E dai depois isso, ele inicia aqui o PLC. Antes estava dando erro hoje nao esta dando mais.

Ele agora esta retornando zero, ou seja, ele conseguiu iniciar o PLC.
Aqui tambem tem esse call, ai ele entra no loop aqui que vai ser o loop do runtime.
Ele chama esse PLC call aqui e depois só incrementa aqui o contador.

O Bruno falou que Machado poderia ser uma tarefa para fazer esse incremento.
E acordo com o tempo e sem me pros segundos, mas agora por enquanto esta incrementando por ciclo aqui desse loop.

E em funcionamento esta aqui, o pelo menos o inicio ali das coisas esta incrementando e nao esta tendo nenhum problema.
O negocio aqui agora, ai eu falei com Bruno ali sobre os proximos passos.
E ele falou que para a monitoracao, porque ele falou que o WPS linha via telegrama de um tipo especial enrichment da data access.

Um debug que ele pega em valores ali do equipamento esses telegramas ai e faz a monitoracao com isso.
Ai eu falei se eu integrar esses telegramas com essa funcao aqui ele vai pegar os dados ali para a monitoracao ele falou que sim.

O unico problema disso e que como e que eu vou chamar essas funcoes de maneira adequada.
A estrategia antes era o seguinte a gente tem ali uma biblioteca-tech a gente usa o jatendir para chamar as funcoes.
Mas para isso nao e possivel porque ele tem um runtime e nao tem como chamar a linha Funcao.

Nao e uma biblioteca-tech convencional. Ai a outra estrategia era usar a memoria compartilhada.
Se tivesse uma memoria compartilhada ali com o WCone e tivesse escrevendo aqui o runtime.
Tivesse escrevendo na memoria do PLC ou do simulador aqui ne.

A gente poderia ler direto a informacao da memoria do simulador.
Assim como e no simulador do WCone so que aqui e a estrategia diferente.
Que ele esta executando ali nessa memoria enfim tem implementacao dos telegramas ja fazendo essa leitura na memoria.
"""

def get_auth_token():
    """Get authentication token"""
    # Tentar login com usuario teste
    login_url = "http://localhost:8000/api/auth/login"
    
    print("Tentando autenticacao...")
    try:
        # Login com form data (OAuth2PasswordRequestForm expects username/password)
        login_data = {
            "username": "testuser",
            "password": "test123"
        }
        
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"[OK] Token obtido: {token[:20]}...")
            return token
        elif response.status_code == 401:
            # Criar novo usuario
            print(f"[INFO] Usuario nao encontrado, criar novo...")
            register_url = "http://localhost:8000/api/auth/register"
            register_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "test123",
                "full_name": "Test User"
            }
            reg_response = requests.post(register_url, json=register_data)
            if reg_response.status_code == 201:
                print("[OK] Usuario criado, fazendo login...")
                # Tentar login novamente
                login_response = requests.post(login_url, data=login_data)
                if login_response.status_code == 200:
                    token = login_response.json().get('access_token')
                    print(f"[OK] Token obtido: {token[:20]}...")
                    return token
            else:
                print(f"[ERROR] Erro ao registrar usuario: {reg_response.status_code}")
                print(f"Response: {reg_response.text}")
                return None
        else:
            print(f"[ERROR] Erro na autenticacao: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception na autenticacao: {e}")
        return None

def test_live_transcription():
    """Test POST /api/minutes/live endpoint"""
    
    # Get token
    token = get_auth_token()
    if not token:
        print("[ERROR] Nao foi possivel obter token de autenticacao")
        return
    
    url = "http://localhost:8000/api/minutes/live"
    
    payload = {
        "title": "Reuniao de Desenvolvimento - 26/01/2026",
        "transcription": test_transcription
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "=" * 80)
    print("TESTANDO ENDPOINT /api/minutes/live")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Titulo: {payload['title']}")
    print(f"Tamanho da transcricao: {len(payload['transcription'])} caracteres")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            minute_id = result.get('id')
            print(f"\n[SUCCESS] Minuto criado com ID: {minute_id}")
            print(f"Titulo: {result.get('title')}")
            print(f"Tempo de processamento: {result.get('processing_time'):.2f}s")
            
            # Fetch the created minute with the structured content
            if minute_id:
                print("\n" + "-" * 80)
                print("ATA GERADA:")
                print("-" * 80)
                if 'structured_minutes' in result and result['structured_minutes']:
                    print(result['structured_minutes'])
                else:
                    print("[WARNING] Structured minutes nao retornado, exibindo resposta completa:")
                    print(json.dumps(result, indent=2))
        else:
            print(f"[ERROR] {response.status_code}")
            try:
                error_data = response.json()
                print(f"Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    test_live_transcription()
