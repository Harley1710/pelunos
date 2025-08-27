import streamlit as st
import json
import firebase_admin
import PyPDF2
import io
from openai import OpenAI 
from paginas.funcoes import COLECAO_USUARIOS
from firebase_admin import firestore, credentials, storage


# Função para ler os exames e extrair informações mais importantes

def relator(pet_id, exame_doc_id, pdf):
    
    """
    Estrutura as informações obrigatórias e opcionais do exame:
    data, tipo, resultado e mini-relatório (opcional)

    Args:
        - pet_id: id do respectivo pet
        - exame_doc_id: id do documento do respectivo exame
        - pdf: arquivo pdf presente na memória do streamlit
    """
    # Extraindo o texto dos pdfs
    texto = ""
    try:
        pdf.seek(0)
        leitor = PyPDF2.PdfReader(pdf)
        for pagina in leitor.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += texto_pagina
    except Exception as erro:
        return f"Erro ao extrair o texto do pdf: {erro}"

    # Definindo o prompt para o agente
    prompt = """Você é um agente de IA treinado para ler, extrair e interpretar informações de laudos de exames veterinários.
    Analise o texto do exame fornecido e extraia os dados-chave.
    As informações a serem extraídas são: data do exame, tipo de exame, um resumo da conclusão e um mini-relatório
    com detalhes adicionais que podem ser relevantes. Não adicione nenhuma informação que não esteja explicitamente no texto.
    Se qualquer um dos campos obrigatórios não puderem ser encontrados, seus respectivos valores no JSON devem ser a string 'Não encontrado'.
    """

    # Criando o modelo
    openai_api_key = st.secrets['OPENAI_API_KEY']
    client = OpenAI(api_key=openai_api_key)

    # Definindo o esquema para o output estruturado

    esquema = {
        "schema": {
            "type": "object",
            "properties": {
                "data_exame":{
                    "type": "string",
                    "description": "Data em que o exame do pet foi realizado, em formato DD-MM-AAAA",
                },
                "tipo_exame":{
                    "type": "string",
                    "description": "Nome ou descrição do exame do pet",
                },
                "resultado_exame":{
                    "type": "string",
                    "description": "Conclusão ou indicativo da saúde do pet",
                },
                "mini_relatorio":{
                    "type": "string",
                    "description": "Breve resumo com informações adicionais que possam ser revelantes para a saúde do pet",
                },
            },
            "required": ["data_exame", "tipo_exame", "resultado_exame", "mini_relatorio"],
            "additionalProperties": False
        },
        "strict": True
    }
    
    # Definindo o modelo com os respectivos argumentos
    resposta = client.chat.completions.create(
        model = 'gpt-4o-mini',

        # Direciona o agente com as instruções
        messages = [{'role': 'system', 'content' : prompt},
                    {'role': 'user', 'content': texto}],
    
        # Garante o formato JSON ao final 
        response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "exame_schema",  # <- ESSA LINHA É O QUE FALTAVA
            "schema": esquema["schema"],
            "strict": esquema["strict"]
        }
        }
        )

    # Saída em formato de texto, objetivando JSON
    saida = json.loads(resposta.choices[0].message.content)

    db = firestore.client()
    exames_doc = db.collection(COLECAO_USUARIOS).document(st.user.email).collection("pets").document(pet_id).collection("exames").document(exame_doc_id)

    try:
        print(saida)
        exames_doc.set(saida, merge=True)
        return True
    except Exception as e:
        return f"Erro ao extrair informações do exame: {e}"


def analisador_saude_pet(pet_data, exames_data):
    """
    Agente de IA que analisa os dados do pet e exames para gerar uma interpretação técnica
    do estado de saúde atual e possíveis implicações/indicativos.
    
    Args:
        pet_data: Dicionário com dados do pet (nome, idade, raça, histórico de saúde, etc.)
        exames_data: Lista de dicionários com dados dos exames (tipo, resultado, data, etc.)
        
    Returns:
        dict: Dicionário com a análise técnica estruturada
    """
    
    # Preparando o contexto para o agente
    contexto_pet = f"""
    INFORMAÇÕES DO PET:
    Nome: {pet_data.get('nome', 'N/A')}
    Espécie: {pet_data.get('especie', 'N/A')}
    Idade: {pet_data.get('idade', 'N/A')}
    Raça: {pet_data.get('raca', 'N/A')}
    Sexo: {pet_data.get('sexo', 'N/A')}
    Castrado: {pet_data.get('castrado', 'N/A')}
    Peso: {pet_data.get('peso', 'N/A')}
    Altura: {pet_data.get('altura', 'N/A')}
    Histórico de Saúde: {pet_data.get('saude', 'N/A')}
    Histórico de Alimentação: {pet_data.get('alimentacao', 'N/A')}
    """
    
    # Preparando informações dos exames
    if exames_data:
        contexto_exames = "\nEXAMES REALIZADOS:\n"
        for exame in exames_data:
            contexto_exames += f"""
            - Tipo: {exame.get('tipo_exame', 'N/A')}
            - Data: {exame.get('data_exame', 'N/A')}
            - Resultado: {exame.get('resultado_exame', 'N/A')}
            - Mini-relatório: {exame.get('mini_relatorio', 'N/A')}
            ---
            """
    else:
        contexto_exames = "\nEXAMES REALIZADOS: Nenhum exame encontrado."
    
    # Prompt para o agente de análise
    prompt = """Você é um veterinário especialista em análise clínica e interpretação de exames.
    
    Sua tarefa é analisar as informações do pet e seus exames para criar uma seção técnica
    que será incluída no relatório veterinário. Esta seção deve ser lida pelo veterinário
    antes de consultar os exames anexados.
    
    Analise os dados fornecidos e gere:
    1. Uma avaliação técnica do estado de saúde atual do animal
    2. Possíveis implicações ou indicativos baseados nos dados disponíveis
    3. Identificação das informações mais importantes
    4. Indicação de em qual exame cada informação importante aparece
    
    Seja técnico, preciso e use linguagem médica veterinária apropriada.
    Não faça diagnósticos definitivos, apenas apresente observações e indicativos.
    Se houver dados insuficientes, indique claramente as limitações.
    """
    
    try:
        # Criando o modelo OpenAI
        openai_api_key = st.secrets['OPENAI_API_KEY']
        client = OpenAI(api_key=openai_api_key)
        
        # Esquema para output estruturado
        esquema = {
            "schema": {
                "type": "object",
                "properties": {
                    "estado_saude_atual": {
                        "type": "string",
                        "description": "Avaliação técnica do estado de saúde atual do pet baseada nos dados disponíveis"
                    },
                    "implicacoes_indicativos": {
                        "type": "string",
                        "description": "Possíveis implicações ou indicativos baseados nos dados analisados"
                    },
                    "informacoes_importantes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "informacao": {
                                    "type": "string",
                                    "description": "Descrição da informação importante encontrada"
                                },
                                "exame_origem": {
                                    "type": "string",
                                    "description": "Nome do exame onde esta informação aparece"
                                },
                                "relevancia": {
                                    "type": "string",
                                    "description": "Explicação da relevância desta informação para a saúde do pet"
                                }
                            },
                            "required": ["informacao", "exame_origem", "relevancia"]
                        },
                        "description": "Lista das informações mais importantes encontradas e em qual exame aparecem"
                    },
                    "limites_analise": {
                        "type": "string",
                        "description": "Limitações da análise atual e dados que seriam necessários para uma avaliação mais completa"
                    },
                    "recomendacoes_gerais": {
                        "type": "string",
                        "description": "Recomendações gerais baseadas na análise realizada"
                    }
                },
                "required": ["estado_saude_atual", "implicacoes_indicativos", "informacoes_importantes", "limites_analise", "recomendacoes_gerais"],
                "additionalProperties": False
            },
            "strict": True
        }
        
        # Chamada para o modelo
        resposta = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': contexto_pet + contexto_exames}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "analise_saude_schema",
                    "schema": esquema["schema"],
                    "strict": esquema["strict"]
                }
            }
        )
        
        # Processando a resposta
        analise_tecnica = json.loads(resposta.choices[0].message.content)
        return analise_tecnica
        
    except Exception as e:
        print(f"Erro na análise técnica do pet: {e}")
        # Retorna análise padrão em caso de erro
        return {
            "estado_saude_atual": "Não foi possível realizar análise técnica devido a erro no sistema.",
            "implicacoes_indicativos": "Análise não disponível.",
            "informacoes_importantes": [],
            "limites_analise": f"Erro técnico: {str(e)}",
            "recomendacoes_gerais": "Consulte diretamente os exames anexados para análise detalhada."
        }


def gerar_secao_interpretacao_tecnica(pet_id):
    """
    Função principal para gerar a seção de interpretação técnica do relatório.
    Busca os dados do pet e exames, e utiliza o analisador de IA para criar a seção.
    Implementa cache inteligente para evitar reprocessamento desnecessário.
    
    Args:
        pet_id: ID do pet para análise
        
    Returns:
        dict: Dicionário com a análise técnica completa
    """
    
    print(f"🚀 Iniciando gerar_secao_interpretacao_tecnica para pet_id: {pet_id}")
    
    try:
        print("🔥 Conectando ao Firestore...")
        db = firestore.client()
        print("✅ Firestore conectado!")
        
        # Verifica se o usuário está logado
        if not hasattr(st, 'user') or not hasattr(st.user, 'email'):
            print("❌ Usuário não logado")
            return {"erro": "Usuário não logado"}
        
        user_email = st.user.email
        print(f"👤 Usuário logado: {user_email}")
        
        # Buscando dados do pet
        print(f"🔍 Buscando pet {pet_id} para usuário {user_email}...")
        pet_ref = db.collection(COLECAO_USUARIOS).document(user_email).collection("pets").document(pet_id)
        pet_doc = pet_ref.get()
        
        if not pet_doc.exists:
            print(f"❌ Pet {pet_id} não encontrado")
            return {"erro": "Pet não encontrado"}
        
        print("✅ Pet encontrado!")
        pet_data = pet_doc.to_dict()
        print(f"📊 Dados do pet: {list(pet_data.keys())}")
        
        # Verificando se já existe uma análise recente (cache inteligente)
        analise_existente = pet_data.get('analise_tecnica')
        data_analise_existente = pet_data.get('data_analise')
        
        print(f"💾 Cache existente: {analise_existente is not None}")
        print(f"📅 Data da análise: {data_analise_existente}")
        
        # Buscando exames do pet para verificar se houve mudanças
        print("🔬 Buscando exames do pet...")
        exames_ref = pet_ref.collection("exames")
        exames_docs = exames_ref.stream()
        exames_data = [doc.to_dict() for doc in exames_docs]
        print(f"📋 Exames encontrados: {len(exames_data)}")
        
        # Verificando se deve usar cache ou gerar nova análise
        deve_regenerar = False
        
        if analise_existente and data_analise_existente:
            # Verifica se a análise tem menos de 24 horas
            from datetime import datetime, timedelta
            if hasattr(data_analise_existente, 'timestamp'):
                data_analise = data_analise_existente.timestamp()
                agora = datetime.now().timestamp()
                diferenca_horas = (agora - data_analise) / 3600
                
                if diferenca_horas < 24:
                    print(f"✅ Usando análise em cache (tempo: {diferenca_horas:.1f}h)")
                    return analise_existente
                else:
                    print(f"⏰ Cache expirado ({diferenca_horas:.1f}h), regenerando análise...")
                    deve_regenerar = True
            else:
                print("⚠️ Data da análise não tem timestamp, regenerando...")
                deve_regenerar = True
        else:
            print("🆕 Primeira análise, gerando nova...")
            deve_regenerar = True
        
        # Verificando se houve mudanças nos exames
        if analise_existente:
            exames_anteriores = analise_existente.get('exames_analisados', [])
            exames_atuais = [exame.get('tipo_exame', '') + exame.get('data_exame', '') for exame in exames_data]
            
            if exames_anteriores == exames_atuais:
                print("✅ Nenhuma mudança nos exames, usando análise em cache")
                return analise_existente
            else:
                print("🔄 Exames alterados, regenerando análise...")
                deve_regenerar = True
        
        if deve_regenerar:
            print("🤖 Gerando nova análise técnica por IA...")
            # Gerando análise técnica
            analise = analisador_saude_pet(pet_data, exames_data)
            print(f"📊 Análise gerada: {type(analise)}")
            
            if analise and not analise.get('erro'):
                # Adicionando metadados da análise
                analise['exames_analisados'] = [exame.get('tipo_exame', '') + exame.get('data_exame', '') for exame in exames_data]
                analise['versao_analise'] = '1.0'
                
                # Salvando a análise no documento do pet para uso futuro
                print("💾 Salvando análise no cache...")
                pet_ref.update({
                    "analise_tecnica": analise,
                    "data_analise": firestore.SERVER_TIMESTAMP
                })
                
                print("✅ Análise técnica salva no cache")
                return analise
            else:
                print(f"❌ Erro na análise: {analise}")
                return {"erro": "Falha na geração da análise"}
        else:
            return analise_existente
        
    except Exception as e:
        print(f"❌ Erro ao gerar seção de interpretação técnica: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return {"erro": f"Erro técnico: {str(e)}"}

