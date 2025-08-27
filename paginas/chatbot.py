import streamlit as st
from openai import OpenAI 
from paginas.funcoes import (
    obter_perfil_usuario, 
    registrar_acao_usuario, 
    registrar_atividade_academica,
    salvar_chat, 
    obter_chats, 
    obter_chat, 
    excluir_chat,
    atualizar_chat,
    login_usuario,
    obter_pets,
    obter_info_exames
)
from paginas.llms import gerar_titulo_chat
from datetime import datetime

# Verifica se o usuário está logado
if not hasattr(st.user, 'is_logged_in') or not st.user.is_logged_in:
    st.warning("Você precisa fazer login para conversar com Dr. Peluno.")
    st.stop()

# Realiza o login do usuário (atualiza último acesso)
login_usuario() 

# Registra a ação de login apenas na primeira vez que a página é carregada na sessão
if 'login_registrado' not in st.session_state:
    registrar_acao_usuario("Login", "Chat Dr. Peluno")
    st.session_state['login_registrado'] = True

# Obtém o perfil e define o nome do usuário ANTES de usar no popover
perfil = obter_perfil_usuario()
# Usa o primeiro nome para a saudação, com fallback para o given_name do login ou 'Querida(o)'
if perfil:
    nome_usuario = perfil.get("nome_completo", getattr(st.user, 'given_name', 'Querida(o)'))
else:
    nome_usuario = getattr(st.user, 'given_name', 'Querida(o)')
    
# Pega só o primeiro nome se for nome completo
if nome_usuario and ' ' in nome_usuario:
    nome_usuario = nome_usuario.split(' ')[0]

# Verifica e exibe a mensagem de boas-vindas no primeiro login
if st.session_state.get('show_welcome_message', False):
    with st.popover("Bem-vindo! 🐾", use_container_width=True):
        st.markdown(f"Olá, **{nome_usuario}**! Sou o Dr. Peluno, seu especialista veterinário virtual!")
        st.markdown("Como conheço todos os detalhes dos seus pets, posso te dar conselhos personalizados e precisos sobre comportamento, saúde e cuidados! 🐾")
        st.button("Vamos conversar!", use_container_width=True, key="welcome_close")
    # Remove o flag para não mostrar novamente
    del st.session_state['show_welcome_message']

# Configurações iniciais
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Função para obter avatar do usuário
def obter_avatar_usuario():
    """Define o avatar do usuário baseado na foto do perfil"""
    user_picture = getattr(st.user, 'picture', None)
    if user_picture and isinstance(user_picture, str) and user_picture.startswith(('http://', 'https://')):
        return user_picture
    else:
        return 'arquivos/avatar_usuario.jpg'

# Mensagem inicial personalizada do Dr. Peluno
def obter_mensagem_inicial():
    """Gera mensagem inicial personalizada com base no perfil do usuário"""
    mensagens_iniciais = [
        f"Oi {nome_usuario}! 🐾 Sou o Dr. Peluno, seu especialista veterinário. Como estão seus pets hoje?",
        f"Olá {nome_usuario}! ✨ Que bom te ver aqui! Como especialista dos seus pets, em que posso ajudar?",
        f"Oi {nome_usuario}! 🐕 Dr. Peluno na área! Me conta sobre seus bichinhos!",
        f"Olá {nome_usuario}! 🐱 Dr. Peluno aqui! Quer conversar sobre comportamento, saúde ou cuidados com seus pets?"
    ]
    import random
    return random.choice(mensagens_iniciais)

# Define os avatars
avatar_user = obter_avatar_usuario()
avatar_assistant = 'arquivos/peluno.png'

MENSAGEM_INICIAL = obter_mensagem_inicial()

# Gera o resumo de informações de exames de cada pet
pets = obter_pets()
contexto_exames = obter_info_exames(pets)

def obter_system_prompt(perfil):
    """Gera o system prompt personalizado para Dr. Peluno"""
    return f"""

**PERSONA:** Você é o Dr. Peluno, um especialista veterinário virtual caloroso, experiente e dedicado. Profissional competente, bem-humorado e acolhedor. Fala em português-BR, frases curtas, **negrito** para destaques e máx. *dois emojis* por mensagem.

INFORMAÇÕES DO USUÁRIO:
- Nome: {perfil.get('nome_completo', 'Não informado')}
- Idade: {perfil.get('idade', 'Não informada')}
- Experiência com Pets: {perfil.get('experiencia_pets', 'Não informada')}
- Tipos de Pets: {perfil.get('tipos_pets', 'Não informado')}
- Situação Atual: {perfil.get('situacao_atual', 'Não informada')}

INFORMAÇÕES DOS PETS:
{perfil['resumos_pet']}

INFORMAÇÕES DOS EXAMES DE CADA PET:
{contexto_exames}

## 2. Missão

Durante uma conversa **natural e acolhedora**, ajude o usuário com questões sobre pets, descobrindo discretamente informações importantes para dar o melhor conselho. Seja o Dr. Peluno, um especialista veterinário dedicado e empático.

### Cinco áreas principais de atuação

1. **Saúde básica** — Sintomas, prevenção, cuidados diários.
2. **Comportamento** — Problemas comportamentais e treinamento.
3. **Alimentação** — Dieta adequada, quantidade, horários.
4. **Cuidados gerais** — Higiene, exercícios, ambiente.
5. **Primeiros socorros** — Orientações para emergências básicas.

*Exemplos de abordagens (usar conforme a situação):*

* "Como tem sido a rotina do seu pet ultimamente?"
* "Você notou alguma mudança no comportamento ou apetite?"
* "Que tipo de alimentação você tem oferecido?"
* "Como está o ambiente onde ele fica?"
* "Já teve alguma experiência com emergências veterinárias?"

---

## 3. Estratégia de Atendimento

1. **Engaje** com interesse genuíno sobre os pets do usuário.
2. **Colete informações** relevantes de forma natural para dar conselhos precisos.
3. **IMPORTANTE**: Para emergências ou sintomas graves, **sempre** oriente a buscar um veterinário presencial imediatamente.
4. Seja sempre **prático e claro** nas orientações, mas sem esquecer o carinho.

---

## 4. Regras "Nunca Fazer"

* Nunca diagnosticar doenças ou prescrever medicamentos específicos.
* **SEMPRE** orientar a buscar veterinário presencial para emergências.
* Evitar dar conselhos que possam colocar o animal em risco.
* Não alegar ser um veterinário real; deixar claro que é o Dr. Peluno, um especialista IA.
* Respeitar imediatamente se o usuário disser **parar**.

---

### 🐾 Resumo Operacional

Seja o Dr. Peluno, um especialista veterinário virtual dedicado e empático. Ajude com **orientações gerais, comportamento, cuidados básicos e prevenção**. Sempre priorize o bem-estar animal e oriente para cuidados profissionais quando necessário. 
"""

# Inicialização do histórico de mensagens e chat ativo
if 'mensagens' not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": MENSAGEM_INICIAL
        }
    ]

if 'chat_ativo_id' not in st.session_state:
    st.session_state.chat_ativo_id = None

if 'chat_ativo_nome' not in st.session_state:
    st.session_state.chat_ativo_nome = "Nova Conversa"

# Cabeçalho com apresentação do Dr. Peluno
st.markdown("""
<style>
.dr-peluno-header {
    padding: 20px 0;
    margin-bottom: 30px;
}

.dr-peluno-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #004aad;
}

.dr-peluno-subtitle {
    font-size: 16px;
    color: #333;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# Cabeçalho principal
col_foto, col_info = st.columns([1, 3])

with col_foto:
    st.image('arquivos/peluno.png', width=80, use_container_width=True)

with col_info: 
    st.markdown('<div class="dr-peluno-title">🩺 Dr. Peluno</div>', unsafe_allow_html=True)
    st.markdown('<div class="dr-peluno-subtitle">', unsafe_allow_html=True)
    st.markdown("### **Seu Especialista Veterinário Virtual Personalizado** 🐾")
    st.markdown("")
    st.markdown("Como conheço **todos os detalhes** dos seus pets - desde histórico médico até preferências alimentares - posso te dar conselhos **precisos e personalizados** que nenhum outro assistente poderia oferecer!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar com histórico de chats
with st.sidebar: 
    
    # Botão de novo chat
    if st.button("✨ Nova Conversa", key="novo_chat", use_container_width=True, type="primary"):
        nova_mensagem_inicial = obter_mensagem_inicial()  # Gera nova mensagem
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": nova_mensagem_inicial
            }
        ]
        st.session_state.chat_ativo_id = None
        st.session_state.chat_ativo_nome = "Nova Conversa"
        registrar_acao_usuario("Nova Conversa", "Usuário iniciou nova conversa com Dr. Peluno")
        st.rerun()
    
    # Exibir chats existentes
    chats = obter_chats() 
    
    if len(chats) == 0:
        st.info("Você ainda não tem conversas salvas! 🐾")
    
    for chat in chats:
        col1, col2 = st.columns([7, 1])
        with col1:
            if st.button(f"{chat['nome']}", key=f"chat_{chat['id']}", use_container_width=True):
                chat_data = obter_chat(chat['id'])
                if chat_data and 'mensagens' in chat_data:
                    st.session_state.mensagens = chat_data['mensagens']
                    st.session_state.chat_ativo_id = chat['id']
                    st.session_state.chat_ativo_nome = chat['nome']
                    registrar_acao_usuario("Abrir Conversa", f"Usuário abriu a conversa {chat['nome']}")
                    st.rerun()
        with col2:
            if st.button("🗑️", key=f"excluir_{chat['id']}"):
                excluir_chat(chat['id'])
                registrar_acao_usuario("Excluir Conversa", f"Usuário excluiu a conversa {chat['nome']}")
                # Se o chat excluído for o ativo, iniciar um novo chat
                if st.session_state.chat_ativo_id == chat['id']:
                    nova_mensagem_inicial = obter_mensagem_inicial()
                    st.session_state.mensagens = [
                        {
                            "role": "assistant",
                            "content": nova_mensagem_inicial
                        }
                    ]
                    st.session_state.chat_ativo_id = None
                    st.session_state.chat_ativo_nome = "Nova Conversa"
                st.rerun()

# Exibição do histórico de mensagens
for mensagem in st.session_state.mensagens:
    role = mensagem["role"]
    # Define o avatar a ser exibido baseado no role
    if role == "user":
        display_avatar = avatar_user
    elif role == "assistant":
        display_avatar = avatar_assistant
    else:
        display_avatar = None
        
    with st.chat_message(role, avatar=display_avatar):
        # Aplica as substituições para formato de matemática do Streamlit apenas nas mensagens do Dr. Peluno
        if role == "assistant":
            display_content = mensagem["content"].replace('\\[', '$$').replace('\\]', '$$')\
                                               .replace('\\(', '$').replace('\\)', '$')
            st.markdown(display_content)
        else:
            st.write(mensagem["content"])

# Input e processamento de mensagens
prompt = st.chat_input(placeholder="Me conta sobre seus pets... 🐾")

if prompt:
    # Registra a pergunta do usuário
    registrar_atividade_academica(
        tipo="chatbot_dr_peluno",
        modulo="Dr. Peluno - Especialista Veterinário",
        detalhes={
            "acao": "pergunta",
            "tamanho_pergunta": len(prompt),
            "chat_id": st.session_state.chat_ativo_id,
            "chat_nome": st.session_state.chat_ativo_nome
        }
    )
    
    # Adiciona mensagem do usuário
    st.session_state.mensagens.append({
        "role": "user",
        "content": prompt
    })
    
    # Mostra mensagem do usuário
    with st.chat_message("user", avatar=avatar_user):
        st.write(prompt)

    # Processa resposta do Dr. Peluno
    with st.chat_message("assistant", avatar=avatar_assistant):
        try:
            # Prepara o sistema prompt personalizado para Dr. Peluno
            system_prompt = obter_system_prompt(perfil)

            # Prepara mensagens para a API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Adiciona apenas as últimas 10 mensagens para manter contexto sem ultrapassar limites
            recent_messages = st.session_state.mensagens[-10:]
            for msg in recent_messages:
                if msg["role"] != "system":
                    messages.append({
                        "role": msg["role"], 
                        "content": msg["content"]
                    })
            
            # Chama a API da OpenAI
            resposta_stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,  # Um pouco mais criativa para conselhos amorosos
                max_tokens=1000,
                stream=True
            )
            
            # Exibe resposta em tempo real
            resposta_completa = ""
            container = st.empty()
            
            for chunk in resposta_stream:
                if chunk.choices[0].delta.content is not None:
                    resposta_completa += chunk.choices[0].delta.content
                    container.markdown(resposta_completa + "▌")
            
            # Remove o cursor e mostra resposta final
            container.markdown(resposta_completa)
            
            # Adiciona resposta ao histórico
            st.session_state.mensagens.append({
                "role": "assistant",
                "content": resposta_completa
            })
            
            # SALVAMENTO AUTOMÁTICO APÓS CADA RESPOSTA
            # Se não há chat ativo, cria um novo
            if st.session_state.chat_ativo_id is None:
                # Gera título da conversa baseado no conteúdo
                try:
                    titulo = gerar_titulo_chat(st.session_state.mensagens)
                    if not titulo:
                        titulo = f"Conversa de {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                except:
                    titulo = f"Conversa de {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                
                # Salva a nova conversa
                chat_id = salvar_chat(titulo, st.session_state.mensagens)
                if chat_id:
                    st.session_state.chat_ativo_id = chat_id
                    st.session_state.chat_ativo_nome = titulo
                    registrar_acao_usuario("Nova Conversa Salva", f"Conversa salva automaticamente: {titulo}")
            else:
                # Atualiza conversa existente
                atualizar_chat(st.session_state.chat_ativo_id, st.session_state.mensagens)
                registrar_acao_usuario("Conversa Atualizada", f"Conversa {st.session_state.chat_ativo_nome} atualizada")
            
            # Registra a resposta
            registrar_atividade_academica(
                        tipo="chatbot_dr_peluno",
        modulo="Dr. Peluno - Especialista Veterinário",
                detalhes={
                    "acao": "resposta",
                    "tamanho_resposta": len(resposta_completa),
                    "chat_id": st.session_state.chat_ativo_id,
                    "chat_nome": st.session_state.chat_ativo_nome
                }
            )
            
        except Exception as e:
            st.error(f"Ops! Tive um probleminha técnico: {str(e)}")
            st.error("Tenta novamente, por favor! 🐾")


