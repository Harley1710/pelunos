import streamlit as st
from paginas.funcoes import obter_perfil_usuario, atualizar_perfil_usuario, registrar_acao_usuario

st.title("🐾 Meu Perfil - Dr. Tobias")

# Obter dados atuais do perfil
perfil = obter_perfil_usuario()
if perfil:
    # Cabeçalho do perfil com foto e nome
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Foto do perfil
        foto_url = perfil.get("foto", "")
        if foto_url:
            st.image(foto_url, width=120)
        else:
            # Placeholder de avatar
            st.markdown("🐾", help="Foto do perfil")
    
    with col2:
        # Nome do usuário
        st.subheader(perfil.get("nome_completo", "Não informado"))
    
    # Grid de informações pessoais
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📧 Email", perfil.get("email", "Não informado"))
        st.metric("🎂 Idade", f"{perfil.get('idade', 'Não informada')}" if perfil.get('idade') else "Não informada")
        
        # Tipos de Pets
        tipos_pets_str = ", ".join(perfil.get("tipos_pets", ["Nenhum informado"]))
        st.metric("🐕 Tipos de Pets", tipos_pets_str)
    
    with col2:
        st.metric("🎓 Experiência com Pets", perfil.get("experiencia_pets", "Não informada"))
        st.metric("🏠 Situação Atual", perfil.get("situacao_atual", "Não informada"))
        
        # Data de cadastro
        if perfil.get("data_criacao"):
            from datetime import datetime
            try:
                if hasattr(perfil["data_criacao"], "date"):
                    data_formatada = perfil["data_criacao"].date().strftime("%d/%m/%Y")
                else:
                    data_formatada = perfil["data_criacao"]
            except:
                data_formatada = "Data não disponível"
            
            st.metric("📅 Membro desde", data_formatada)

    # Seção para editar informações
    st.header("✏️ Editar Minhas Informações")
    st.markdown("Aqui você pode atualizar suas informações para que Dr. Tobias possa te ajudar melhor com seus pets!")
    
    with st.expander("🔧 Clique aqui para editar suas informações", expanded=False):
        with st.form("editar_perfil"):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_nome = st.text_input("Nome/Apelido", value=perfil.get("nome_completo", ""))
                nova_idade = st.number_input("Idade", min_value=16, max_value=120, value=int(perfil.get("idade", 18)))
                
                nova_experiencia = st.selectbox("Experiência com Pets", [
                    "Sou novo(a) no mundo dos pets",
                    "Tenho alguma experiência", 
                    "Tenho bastante experiência",
                    "Sou muito experiente",
                    "Trabalho profissionalmente com animais"
                ], index=0 if perfil.get("experiencia_pets") in [None, "", "Não informada"] else [
                    "Sou novo(a) no mundo dos pets",
                    "Tenho alguma experiência", 
                    "Tenho bastante experiência",
                    "Sou muito experiente",
                    "Trabalho profissionalmente com animais"
                ].index(perfil.get("experiencia_pets", "Sou novo(a) no mundo dos pets")))
            
            with col2:
                novos_tipos_pets = st.multiselect("Tipos de Pets que você tem/teve", [
                    "Cachorro",
                    "Gato",
                    "Pássaro",
                    "Peixe",
                    "Hamster/Roedor",
                    "Coelho",
                    "Réptil",
                    "Outros",
                    "Nunca tive pets"
                ], default=perfil.get("tipos_pets", []))
                
                nova_situacao = st.selectbox("Situação Atual com Pets", [
                    "Tenho pet(s) atualmente",
                    "Estou pensando em ter um pet",
                    "Tive pets no passado",
                    "Cuido de pets de outros",
                    "Trabalho com pets",
                    "Só tenho interesse no assunto"
                ], index=0 if perfil.get("situacao_atual") in [None, "", "Não informada"] else [
                    "Tenho pet(s) atualmente",
                    "Estou pensando em ter um pet",
                    "Tive pets no passado",
                    "Cuido de pets de outros",
                    "Trabalho com pets",
                    "Só tenho interesse no assunto"
                ].index(perfil.get("situacao_atual", "Tenho pet(s) atualmente")))
            
            if st.form_submit_button("🐾 Salvar Alterações", type="primary", use_container_width=True):
                dados_atualizar = {
                    "nome_completo": novo_nome,
                    "idade": nova_idade,
                    "experiencia_pets": nova_experiencia,
                    "tipos_pets": novos_tipos_pets,
                    "situacao_atual": nova_situacao
                }
                
                if atualizar_perfil_usuario(dados_atualizar):
                    st.success("✅ Suas informações foram atualizadas com sucesso!")
                    st.info("💡 Dr. Tobias agora pode te ajudar ainda melhor com seus pets usando essas informações atualizadas!")
                    registrar_acao_usuario("Atualizar Perfil", f"Usuário atualizou informações do perfil")
                    st.rerun()
                else:
                    st.error("❌ Houve um erro ao salvar suas informações. Tente novamente!")
    
    # Informações sobre privacidade
    st.info("🔒 **Privacidade**: Suas informações pessoais são usadas apenas para personalizar os conselhos do Dr. Tobias sobre pets e nunca são compartilhadas com terceiros.")

else:
    st.error("⚠️ Não foi possível carregar as informações do seu perfil.")
    if st.button("🔄 Tentar Novamente", type="primary"):
        st.rerun()
