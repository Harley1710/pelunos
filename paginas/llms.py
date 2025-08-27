import streamlit as st
from openai import OpenAI

# Modelo padrão para as funções auxiliares (pode ser ajustado ou passado como argumento)
MODELO_PADRAO = 'gpt-4o-mini'

# Helper para obter cliente OpenAI (evita repetição e centraliza erro de chave)
def _get_openai_client():
    """Retorna um cliente OpenAI inicializado ou None se a chave não for encontrada."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        return OpenAI(api_key=api_key)
    except KeyError:
        st.error("Erro de configuração: Chave secreta 'OPENAI_API_KEY' não encontrada.")
        return None
    except Exception as e:
        st.error(f"Erro ao inicializar cliente OpenAI: {e}")
        return None

def gerar_titulo_chat(mensagens):
    """
    Gera um título profissional e objetivo para um chat baseado nas mensagens.
    
    Args:
        mensagens: Lista de mensagens do chat
        
    Returns:
        str: Título gerado ou None se falhou
    """
    client = _get_openai_client()
    if not client:
        return None
        
    # Pega as primeiras mensagens para gerar o título
    conteudo_chat = ""
    for msg in mensagens[:4]:  # Aumenta para 4 mensagens para melhor contexto
        if msg["role"] == "user":
            conteudo_chat += f"Usuário: {msg['content']}\n"
        elif msg["role"] == "assistant":
            conteudo_chat += f"Dr. Peluno: {msg['content']}\n"
    
    prompt = f"""Analise esta conversa inicial e crie um título PROFISSIONAL, OBJETIVO e DESCRITIVO para a consulta veterinária.

REGRAS IMPORTANTES:
- Título deve ter entre 30-60 caracteres
- Use linguagem médica/veterinária apropriada
- Seja específico sobre o problema ou tema principal
- Evite linguagem casual ou engraçada
- Use formato: "Tema Principal - Pet/Nome" quando possível
- Exemplos de títulos bons:
  * "Consulta Comportamental - Cão Rex"
  * "Avaliação Nutricional - Gato Luna"
  * "Sintomas Respiratórios - Pet Toby"
  * "Prevenção Vacinal - Filhotes"

CONVERSA:
{conteudo_chat}

Responda APENAS com o título, sem aspas ou explicações."""

    try:
        completion = client.chat.completions.create(
            model=MODELO_PADRAO,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3  # Reduzido para mais consistência
        )
        titulo = completion.choices[0].message.content.strip()
        
        # Limpa o título de caracteres especiais e aspas
        titulo = titulo.replace('"', '').replace("'", "").strip()
        
        # Garante tamanho adequado
        if len(titulo) > 60:
            titulo = titulo[:57] + "..."
        elif len(titulo) < 20:
            titulo = titulo + " - Consulta Veterinária"
            
        return titulo
        
    except Exception as e:
        print(f"Erro ao gerar título do chat: {e}")
        return None 