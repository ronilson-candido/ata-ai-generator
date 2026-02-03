#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script para validar a geração de atas melhorada"""

from minutes_generator import TechnicalMinutesGenerator

# Sua transcrição de exemplo (truncada para teste)
test_transcription = """
O que você está fazendo? Não. Para mostrar os avanços ali na semana que a gente teve um projeto. 
Tem tividades concluídas. A questão ali é das funções do simulador, as funções que a biblioteca pedia para o usuário implementar, foram implementadas.
Então todas as funções necessárias no momento que foram implementadas, algumas delas. 
O equipamento que está sendo simulado. E algumas que nem precisou, sem implementado, como essa daqui.

Depois que eu me tentei isso, eu vi aqui o código está assim, por enquanto.
O negócio que ele faz, ele pega ali o sistema e leus binários.
Depois ele coloca os indeleços que está no file system, nessa extract que eu criei.

E, no início, ele coloca aqui nessa função aqui para ler os restantes dos arquivos que estão aqui.
E daí depois peito isso, ele inicia aqui o PLC. Antes estava dando erro hoje não está dando mais.

Ele agora está retornando zero, ou seja, ele conseguiu iniciar o PLC.
Aqui também tem esse call, aí ele entra no loop aqui que vai ser o loop do runtime.
Ele chama esse PLC call aqui e depois só incrementa aqui o contador.

O Bruno falou que Machado poderia ser uma tarefa para fazer esse incremento.
E acordo com o tempo e sem me pros segundos, mas agora por enquanto está incrementando por ciclo aqui desse loop.

E em pintar está funcionando aqui, o pelo menos o início ali das coisas está incrementando e não está tendo nenhum problema.
O negócio aqui agora, aí eu falei com Bruno ali sobre os próximos passos.
E ele falou que para a monitorata, porque ele falou que o WPS linha via telegrama de um tipo especial enrichment da data access.

Um debug que ele pega em cidades ali do equipamento esses telegramas aí e faz a monitoração com isso.
Aí eu falei se eu integrar esse telegramas com essa função aqui ele vai pegar os dados ali para a monitoração ele falou que sim.

O único problema disso é que como é que eu vou chamar essas funções de maneira adequada.
A estratégia antes era o seguinte a gente tem ali um biblioteca-tech a gente usa o jatendir para chamar as funções.
Mas para isso não é possível porque ele tem um runtime e não tem como chamar a linha Funcion.

Não é um biblioteca-tech convencional. Aí a outra estratégia era usar a memória compartilhada.
Se tivesse uma memória compartilhada ali com o WCone e tivesse escrevendo aqui o runtime.
Tivesse escrevendo na memória do PLC ou do simulador aqui né.

A gente poderia ler direto a informação da memória do simulador.
Assim como é no simulador do WCone só que aqui é a estratégia diferente.
Que ele está executando ali nessa memória enfim tem implementação dos telegramas já fazendo essa leitura na memória.
"""

def test_generation():
    """Testa a geração de atas com a transcrição de exemplo"""
    print("=" * 80)
    print("TESTANDO GERACAO DE MINUTES COM TRANSCRICAO CORROMPIDA")
    print("=" * 80)
    print()
    
    generator = TechnicalMinutesGenerator()
    
    print("[ETAPA 1] Limpeza da transcricao")
    print("-" * 80)
    clean_text = generator.clean_transcription(test_transcription)
    print(f"Caracteres originais: {len(test_transcription)}")
    print(f"Caracteres após limpeza: {len(clean_text)}")
    print(f"\nAmostra do texto limpo:\n{clean_text[:300]}...\n")
    
    print("[ETAPA 2] Gerando ata estruturada")
    print("-" * 80)
    ata = generator.generate_structured_minutes(test_transcription)
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL - ATA GERADA:")
    print("=" * 80)
    print(ata)
    
    # Validação
    print("\n" + "=" * 80)
    print("VALIDACAO:")
    print("=" * 80)
    
    # Verificar se as seções não estão repetidas
    lines = ata.split('\n')
    
    # Contar seções
    concluidas_section = False
    andamento_section = False
    futuras_section = False
    
    for i, line in enumerate(lines):
        if "**Concluidas**" in line:
            concluidas_section = True
        elif "**Em andamento**" in line:
            andamento_section = True
        elif "**Proximos passos**" in line:
            futuras_section = True
    
    if concluidas_section and andamento_section and futuras_section:
        print("[OK] Todas as 3 secoes foram geradas")
    else:
        print("[ERRO] Algumas secoes estao faltando")
    
    # Verificar repetições
    bullet_lines = [line for line in lines if line.startswith('- ')]
    if len(bullet_lines) > 0:
        print(f"[OK] Total de bullets: {len(bullet_lines)}")
        
        # Verificar se há muita repetição
        unique_bullets = set(bullet_lines)
        if len(unique_bullets) == len(bullet_lines):
            print("[OK] Nenhuma repeticao detectada entre bullets")
        else:
            repeat_count = len(bullet_lines) - len(unique_bullets)
            print(f"[AVISO] {repeat_count} bullets repetidos")
    
    return ata

if __name__ == "__main__":
    test_generation()
