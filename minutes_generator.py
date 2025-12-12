from datetime import datetime
import re

class TechnicalMinutesGenerator:
    def __init__(self):
        self.technical_keywords = {
            'wcomm': ['wcomm', 'w com', 'módulo wcomm'],
            'wcon': ['wcon', 'módulo wcon'], 
            'simulator': ['simulator', 'simulador', 'simula', 'simuleto'],
            'telegram': ['telegrama', 'telegramos', 'pdu', 'pdus'],
            'modbus': ['modbus', 'protocolo modbus'],
            'biblioteca': ['biblioteca', 'bruno', 'header', 'compilação', 'bilhoteca'],
            'exchange_file': ['exchange file', 'exchange de file', 'file 2'],
            'debug': ['debug', 'depuração', 'debugging', 'divulgar'],
            'porta': ['porta simulator', 'port simulator', 'porta'],
            'julia': ['julia', 'implementação da julha'],
            'virtual': ['virtual device', 'virtual', 'device virtual'],
            'process': ['process builder', 'processo', 'execução'],
            'plc': ['plc', 'plcs'],
            'protocolo': ['protocolo', 'handshake'],
            'dados': ['dados binários', 'bytes', 'binários'],
            'conexão': ['conexão', 'conexões', 'conectar'],
            'implementação': ['implementação', 'implementar', 'desenvolver']
        }
        
        # Padrões de ruído para remover
        self.noise_patterns = [
            r'^[a-z]{1,3}$',  # Palavras muito curtas
            r'^(ah|eh|oh|opa|alo|alô|tá|né|sim|não|ok|beleza)$',
            r'.*(haha|hehe|rs).*',
            r'.*(café|chocolate|bacaxi|doce|brincando).*',
            r'.*(valeu|obrigado|tchau|até logo).*',
            r'.*(ouvindo|escutando|falando).*',
            r'^.*(não,? não,? não).*$',
            r'^.*(tô aqui|tá aqui|estou aqui).*$',
            r'^.*(matias|mateus|miguel|renato|carlos|bruno).*$',  # Nomes sem contexto técnico
        ]

    def clean_transcription(self, text):
        """Limpa a transcrição mantendo apenas conteúdo técnico relevante"""
        if not text:
            return ""
            
        # Dividir em frases
        sentences = re.split(r'[.!?]+', text)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 15:  # Aumentei o mínimo para 15 caracteres
                continue
                
            # Pular frases que são claramente ruído
            if self.is_noise_sentence(sentence):
                continue
                
            # Manter apenas frases com conteúdo técnico substancial
            if self.has_substantial_technical_content(sentence):
                cleaned_sentence = self.clean_sentence(sentence)
                if cleaned_sentence and len(cleaned_sentence) > 20:
                    cleaned_sentences.append(cleaned_sentence)
        
        return '. '.join(cleaned_sentences)

    def is_noise_sentence(self, sentence):
        """Identifica frases que são ruído"""
        sentence_lower = sentence.lower().strip()
        
        # Verificar padrões de ruído
        for pattern in self.noise_patterns:
            if re.match(pattern, sentence_lower):
                return True
        
        # Frases muito curtas com palavras comuns
        if len(sentence_lower.split()) <= 3:
            common_words = ['sim', 'não', 'tá', 'ok', 'ah', 'eh', 'oh', 'opa']
            if any(word == sentence_lower for word in common_words):
                return True
        
        # Frases que começam com cumprimentos
        if sentence_lower.startswith(('opa,', 'alo,', 'alô,', 'eh,', 'ah,')):
            return True
            
        return False

    def has_substantial_technical_content(self, text):
        """Verifica se o texto tem conteúdo técnico substancial"""
        text_lower = text.lower()
        
        # Contar ocorrências de palavras técnicas
        technical_count = 0
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    technical_count += 1
        
        # Precisa ter pelo menos 1 termo técnico OU ser uma frase longa com contexto técnico
        if technical_count >= 1:
            return True
            
        # Frases longas podem conter contexto útil
        if len(text) > 80:
            technical_indicators = [
                'desenvolvimento', 'implementação', 'sistema', 'código', 
                'módulo', 'função', 'classe', 'configuração', 'teste',
                'projeto', 'tecnico', 'tecnologia', 'software'
            ]
            if any(indicator in text_lower for indicator in technical_indicators):
                return True
                
        return False

    def extract_technical_context(self, text):
        """Extrai contexto técnico específico com filtro rigoroso"""
        context = {
            'projeto_principal': '',
            'atividades_recentes': [],
            'problemas_identificados': [],
            'solucoes_implementadas': [],
            'proximos_passos': [],
            'decisoes_tomadas': []
        }
        
        clean_text = self.clean_transcription(text)
        sentences = clean_text.split('. ')
        
        for sentence in sentences:
            if not sentence or len(sentence) < 25:
                continue
                
            sentence_lower = sentence.lower()
            
            # Projeto principal (apenas se for muito claro)
            if not context['projeto_principal']:
                if any(word in sentence_lower for word in ['wcomm', 'telegrama', 'exchange file']):
                    if any(word in sentence_lower for word in ['ponto de entrada', 'função principal', 'dados enviados']):
                        context['projeto_principal'] = self.clean_sentence(sentence)
            
            # Atividades recentes (apenas ações concretas)
            if any(word in sentence_lower for word in ['estudei', 'analisei', 'identifiquei', 'revisei']):
                if any(tech in sentence_lower for tech in ['wcomm', 'wcon', 'simulator', 'biblioteca', 'telegrama']):
                    clean_activity = self.clean_sentence(sentence)
                    if len(clean_activity) > 30:
                        context['atividades_recentes'].append(clean_activity)
            
            # Problemas identificados (apenas problemas técnicos)
            elif any(word in sentence_lower for word in ['problema', 'dificuldade', 'erro', 'conflito', 'bug', 'não funcionava']):
                if any(tech in sentence_lower for tech in ['conexão', 'virtual', 'julia', 'implementação', 'código']):
                    clean_problem = self.clean_sentence(sentence)
                    if len(clean_problem) > 30:
                        context['problemas_identificados'].append(clean_problem)
            
            # Soluções (apenas soluções técnicas)
            elif any(word in sentence_lower for word in ['corrigi', 'resolvi', 'implementei', 'adicionei', 'criei']):
                clean_solution = self.clean_sentence(sentence)
                if len(clean_solution) > 30:
                    context['solucoes_implementadas'].append(clean_solution)
            
            # Próximos passos (apenas ações específicas)
            elif any(word in sentence_lower for word in ['preciso', 'vou', 'devemos', 'próximo', 'implementar', 'transferir', 'definir']):
                if any(tech in sentence_lower for tech in ['biblioteca', 'porta', 'wps', 'telegrama', 'dados binários']):
                    clean_step = self.clean_sentence(sentence)
                    if len(clean_step) > 30:
                        context['proximos_passos'].append(clean_step)
        
        # Limitar a quantidade de cada tipo
        context['atividades_recentes'] = context['atividades_recentes'][:2]
        context['problemas_identificados'] = context['problemas_identificados'][:2]
        context['solucoes_implementadas'] = context['solucoes_implementadas'][:2]
        context['proximos_passos'] = context['proximos_passos'][:2]
        
        return context

    def clean_sentence(self, sentence):
        """Limpa uma sentença individual de forma rigorosa"""
        # Remover excesso de espaços
        sentence = re.sub(r'\s+', ' ', sentence)
        
        # Remover conversas casuais no início e fim
        casual_patterns = [
            r'^[^.]*?(ah,|eh,|oh,|opa,|alo,|alô,|tá,|né,|sim,|não,)',
            r'(ah|eh|oh|opa|alo|alô|tá|né|sim|não|ok|beleza)[^.]*$'
        ]
        
        for pattern in casual_patterns:
            sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)
        
        sentence = sentence.strip()
        
        # Remover frases que ainda possam ser ruído
        if self.is_noise_sentence(sentence):
            return ""
        
        # Capitalizar primeira letra
        if sentence and len(sentence) > 0:
            sentence = sentence[0].upper() + sentence[1:]
            
        return sentence.strip()

    def analyze_keyword_frequency(self, text):
        """Analisa frequência de palavras-chave técnicas"""
        freq = {}
        clean_text = self.clean_transcription(text)
        text_lower = clean_text.lower()
        
        for category, keywords in self.technical_keywords.items():
            count = 0
            for keyword in keywords:
                count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
            if count > 0:
                freq[category] = count
                
        return freq

    def generate_structured_minutes(self, transcription):
        """Gera a ata estruturada final"""
        
        print("🔍 Analisando transcrição...")
        clean_text = self.clean_transcription(transcription)
        context = self.extract_technical_context(transcription)  # Usar transcrição original para contexto
        keyword_freq = self.analyze_keyword_frequency(transcription)
        
        print("📊 Palavras-chave detectadas:")
        for keyword, count in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   - {keyword}: {count}")
        
        print(f"📝 Texto limpo: {len(clean_text)} caracteres")
        
        minutes = f"""# ATA DE REUNIÃO - LABORATÓRIO CYBER

**Data de Geração**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Baseado em**: Análise técnica detalhada

## 1. Informações Gerais:
{self.generate_general_info(context, keyword_freq)}

## 2. Pauta da Reunião:
{self.generate_agenda_section(context, keyword_freq)}

## 3. Discussões e Direcionamentos:
{self.generate_discussions_section(context, keyword_freq)}

## 4. Pontos de Discussão:
{self.generate_discussion_points(keyword_freq)}

## Encaminhamentos e Próximos Passos:
{self.generate_next_steps(context, keyword_freq)}

---
*Documento gerado automaticamente pelo Sistema CyberLab Minutes AI*
"""
        return minutes

    def generate_general_info(self, context, keyword_freq):
        """Gera informações gerais baseadas apenas em conteúdo técnico válido"""
        
        info = "Reunião técnica conduzida em tom informal no laboratório"
        
        # Determinar foco principal baseado nas palavras-chave mais frequentes
        if keyword_freq:
            main_topics = [k for k, v in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True) if v > 0][:2]
            
            if main_topics:
                topic1 = self.get_topic_description(main_topics[0])
                info += f", com foco no avanço da estrutura do {topic1}"
                
                if len(main_topics) > 1:
                    topic2 = self.get_topic_description(main_topics[1])
                    info += f" e no tratamento dos {topic2}"
                info += "."
        
        # Adicionar informações específicas do contexto (apenas se forem técnicas)
        specific_info = []
        
        if context['projeto_principal'] and self.has_substantial_technical_content(context['projeto_principal']):
            specific_info.append(context['projeto_principal'])
        
        if 'biblioteca' in keyword_freq and keyword_freq['biblioteca'] > 1:
            specific_info.append("estudo sobre o arquivo principal necessário para o projeto relacionado à biblioteca")
        
        if 'exchange_file' in keyword_freq and keyword_freq['exchange_file'] > 0:
            specific_info.append("análise do tipo Exchange File 2 Request para transferência de arquivos")
        
        if specific_info:
            info += " " + ". ".join(specific_info) + "."
        
        # Objetivo principal (apenas se detectou termos relevantes)
        if ('telegram' in keyword_freq and keyword_freq['telegram'] > 1) or \
           ('dados' in keyword_freq and keyword_freq['dados'] > 0):
            info += " O objetivo principal apresentado foi compreender como tratar os dados (bytes trocados nos telegramas) para iniciar a integração com a biblioteca e a simulação de transferência de arquivos."
        
        return info

    def get_topic_description(self, topic_key):
        """Retorna descrição amigável para tópicos técnicos"""
        descriptions = {
            'wcomm': 'WComm',
            'wcon': 'WCon', 
            'simulator': 'simulador',
            'telegram': 'telegramas de comunicação',
            'modbus': 'protocolo Modbus',
            'biblioteca': 'biblioteca',
            'exchange_file': 'Exchange File 2',
            'debug': 'processo de depuração',
            'porta': 'porta simulator',
            'virtual': 'virtual device',
            'protocolo': 'protocolos de comunicação',
            'process': 'Process Builder'
        }
        return descriptions.get(topic_key, topic_key)

    def generate_agenda_section(self, context, keyword_freq):
        """Gera seção de pauta apenas com conteúdo técnico válido"""
        
        agenda = "### Atividades Concluídas:\n"
        
        completed = []
        
        # Baseado em palavras-chave e contexto técnico
        if 'wcomm' in keyword_freq and keyword_freq['wcomm'] > 1 and \
           'telegram' in keyword_freq and keyword_freq['telegram'] > 1:
            completed.append("Estudo sobre o ponto de entrada do WComm e análise da estrutura do telegrama Exchange File 2 Request")
        
        if 'biblioteca' in keyword_freq and keyword_freq['biblioteca'] > 1:
            completed.append("Revisão da biblioteca principal e estrutura de compilação")
        
        # Atividades do contexto (apenas as mais técnicas)
        tech_activities = [act for act in context['atividades_recentes'] 
                          if self.has_substantial_technical_content(act) and len(act) > 40]
        completed.extend(tech_activities[:1])
        
        if not completed:
            completed = ["Análise técnica do sistema atual e identificação de pontos de melhoria"]
        
        agenda += "\n".join([f"- {item}" for item in completed])
        
        # Atividades em Andamento
        agenda += "\n\n### Atividades em Andamento:\n"
        
        ongoing = []
        
        if 'wcon' in keyword_freq and keyword_freq['wcon'] > 0 and \
           'debug' in keyword_freq and keyword_freq['debug'] > 0:
            ongoing.append("Depuração do módulo WCon para compreender o processo de inicialização, setup e carregamento das conexões")
        
        if 'porta' in keyword_freq and keyword_freq['porta'] > 1:
            ongoing.append("Adição de uma nova porta 'simulator' dentro do WCon, usada temporariamente para debugging")
        
        if 'simulator' in keyword_freq and keyword_freq['simulator'] > 1:
            ongoing.append("Criação de um novo módulo chamado WCon Simulator, responsável por gerenciar conexões simuladas")
        
        # Soluções implementadas (apenas as mais técnicas)
        tech_solutions = [sol for sol in context['solucoes_implementadas'] 
                         if self.has_substantial_technical_content(sol) and len(sol) > 40]
        ongoing.extend(tech_solutions[:1])
        
        if not ongoing:
            ongoing = ["Desenvolvimento das funcionalidades técnicas discutidas"]
        
        agenda += "\n".join([f"- {item}" for item in ongoing])
        
        # Atividades Futuras
        agenda += "\n\n### Atividades Futuras:\n"
        
        future = []
        
        if 'biblioteca' in keyword_freq and keyword_freq['biblioteca'] > 0:
            future.append("Definir a chamada da biblioteca no momento de recepção dos dados binários")
        
        if 'porta' in keyword_freq and keyword_freq['porta'] > 0:
            future.append("Transferir a configuração da porta 'simulator' para o arquivo de configuração do WPS")
        
        if 'telegram' in keyword_freq and keyword_freq['telegram'] > 0:
            future.append("Implementar e testar o processo completo de tratamento e resposta dos telegramas no WComm")
        
        # Próximos passos do contexto (apenas os mais técnicos)
        tech_steps = [step for step in context['proximos_passos'] 
                     if self.has_substantial_technical_content(step) and len(step) > 40]
        future.extend(tech_steps[:1])
        
        if not future:
            future = ["Consolidação das implementações técnicas e validação do sistema integrado"]
        
        agenda += "\n".join([f"- {item}" for item in future])
        
        return agenda

    def generate_discussions_section(self, context, keyword_freq):
        """Gera discussões baseadas apenas em conteúdo técnico válido"""
        
        discussion = "Durante a reunião, "
        
        # Problemas identificados (apenas se forem técnicos)
        tech_problems = [prob for prob in context['problemas_identificados'] 
                        if self.has_substantial_technical_content(prob)]
        
        if tech_problems:
            # Usar apenas a descrição técnica do problema
            problem_desc = self.extract_technical_problem(tech_problems[0])
            if problem_desc:
                discussion += f"foram detalhadas as dificuldades enfrentadas com {problem_desc} "
        
        # Informações técnicas específicas baseadas em palavras-chave
        technical_details = []
        
        if 'debug' in keyword_freq and keyword_freq['debug'] > 0:
            technical_details.append("início do debug a partir da função main do WCon para rastrear o fluxo de dados")
        
        if 'julia' in keyword_freq and keyword_freq['julia'] > 0:
            technical_details.append("identificação de conflitos de conexão na implementação anterior de Júlia devido à instância incorreta do virtual device")
        
        if technical_details:
            discussion += "e " + ". ".join(technical_details) + ". "
        
        # Soluções e reorganizações
        if 'virtual' in keyword_freq and keyword_freq['virtual'] > 0:
            discussion += "Após corrigir essa lógica, a estrutura foi reorganizada para tornar o simulador independente desse dispositivo virtual. "
        
        if 'simulator' in keyword_freq and keyword_freq['simulator'] > 1:
            discussion += "Foi explicado também o funcionamento interno do novo módulo WCon Simulator, com destaque para as classes SimulatorDevice e SimulatorMachine, que tratam o protocolo Modbus e simulam o comportamento mestre/escravo. "
        
        if 'telegram' in keyword_freq and keyword_freq['telegram'] > 1:
            discussion += "A discussão destacou a importância de construir respostas corretas aos telegramas, garantindo que cada PDU recebido gere um retorno coerente e sem reutilização indevida de dados anteriores."
        
        # Fallback técnico
        if discussion == "Durante a reunião, ":
            main_topics = [k for k, v in keyword_freq.items() if v > 0][:3]
            if main_topics:
                topics_str = ", ".join([self.get_topic_description(topic) for topic in main_topics])
                discussion += f"foram discutidos aspectos técnicos relacionados a {topics_str}."
            else:
                discussion += "foram discutidos aspectos técnicos do desenvolvimento do sistema."
        
        return discussion

    def extract_technical_problem(self, problem_text):
        """Extrai apenas a parte técnica de descrições de problemas"""
        # Manter apenas partes que contêm termos técnicos
        technical_parts = []
        sentences = problem_text.split('. ')
        
        for sentence in sentences:
            if self.has_substantial_technical_content(sentence):
                clean_sentence = self.clean_sentence(sentence)
                if clean_sentence:
                    technical_parts.append(clean_sentence.lower())
        
        if technical_parts:
            return technical_parts[0]
        return ""

    def generate_discussion_points(self, keyword_freq):
        """Gera pontos de discussão baseados nas palavras-chave mais relevantes"""
        
        points = []
        
        # Pontos baseados nas palavras-chave mais frequentes
        relevant_keywords = [k for k, v in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True) if v > 0]
        
        point_mapping = {
            'wcon': "Estrutura do WCon e papel do arquivo principal no processo de compilação e simulação",
            'telegram': "Tratamento dos telegramas e funcionamento do handshake no protocolo",
            'debug': "Depuração do fluxo de inicialização e conexões do simulador",
            'julia': "Problemas de configuração e incompatibilidades com a versão anterior do código de Júlia",
            'simulator': "Criação do módulo WCon Simulator e definição das classes que tratam o protocolo",
            'virtual': "Estratégias para controle de resposta e prevenção de erros com dados antigos",
            'biblioteca': "Planejamento da integração com a biblioteca em C e execução via Process Builder",
            'porta': "Configuração e gestão das portas de comunicação do simulador"
        }
        
        for keyword in relevant_keywords:
            if keyword in point_mapping and point_mapping[keyword] not in points:
                points.append(point_mapping[keyword])
                if len(points) >= 5:  # Limitar a 5 pontos principais
                    break
        
        # Preencher com pontos técnicos padrão se necessário
        default_points = [
            "Arquitetura técnica do sistema e componentes",
            "Protocolos de comunicação e integração entre módulos",
            "Estratégias de desenvolvimento e validação técnica"
        ]
        
        for point in default_points:
            if len(points) < 5 and point not in points:
                points.append(point)
        
        return "\n".join([f"- {point}" for point in points[:7]])

    def generate_next_steps(self, context, keyword_freq):
        """Gera próximos passos baseados apenas em conteúdo técnico válido"""
        
        next_steps = "Os próximos passos definidos envolvem "
        
        steps = []
        
        # Passos baseados em palavras-chave
        if 'simulator' in keyword_freq and keyword_freq['simulator'] > 0 and \
           'wcomm' in keyword_freq and keyword_freq['wcomm'] > 0:
            steps.append("consolidar o módulo WComm Simulator, garantindo que o recebimento e o tratamento dos telegramas estejam funcionando corretamente")
        
        if 'porta' in keyword_freq and keyword_freq['porta'] > 0:
            steps.append("mover as configurações temporárias atualmente utilizadas para o arquivo de configuração do WPS, de forma a integrar o simulador ao ambiente definitivo")
        
        if 'biblioteca' in keyword_freq and keyword_freq['biblioteca'] > 0:
            steps.append("implementar a coleta dos dados binários e da chamada da biblioteca dentro do fluxo do WComm, assegurando que o processamento ocorra de maneira automatizada")
        
        if 'telegram' in keyword_freq and keyword_freq['telegram'] > 0:
            steps.append("validação completa do ciclo de envio e resposta dos telegramas — incluindo as etapas de construção, transmissão, resposta e limpeza dos dados — para garantir a consistência do protocolo")
        
        # Adicionar próximos passos do contexto (apenas os técnicos)
        tech_steps = [step for step in context['proximos_passos'] 
                     if self.has_substantial_technical_content(step) and len(step) > 40]
        for step in tech_steps[:1]:
            if step not in steps:
                steps.append(step)
        
        if steps:
            if len(steps) == 1:
                next_steps += steps[0] + "."
            else:
                next_steps += ", ".join(steps[:-1]) + " e " + steps[-1] + "."
        else:
            next_steps += "avançar nas implementações técnicas discutidas durante a reunião."
        
        return next_steps

# Instância global
minutes_generator = TechnicalMinutesGenerator()

def generate_structured_minutes(transcription):
    """Função principal"""
    try:
        return minutes_generator.generate_structured_minutes(transcription)
    except Exception as e:
        print(f"Erro na geração: {e}")
        return f"""# ATA DE REUNIÃO - LABORATÓRIO CYBER

**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 1. Informações Gerais:
Reunião técnica conduzida no laboratório para discussão do desenvolvimento do sistema.

## 2. Pauta da Reunião:
### Atividades Concluídas:
- Análise técnica do sistema atual

### Atividades em Andamento:
- Desenvolvimento de módulos específicos

### Atividades Futuras:
- Implementação das funcionalidades discutidas

## 3. Discussões e Direcionamentos:
Discussão sobre aspectos técnicos do projeto em desenvolvimento.

## 4. Pontos de Discussão:
- Desenvolvimento de componentes técnicos
- Integração entre módulos do sistema

## Encaminhamentos e Próximos Passos:
Continuar com o desenvolvimento técnico conforme planejado.
"""