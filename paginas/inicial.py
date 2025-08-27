import streamlit as st
from datetime import date, datetime
from paginas.funcoes import (
    obter_pets, 
    excluir_pet, 
    registrar_acao_usuario,
    gerar_relatorio_pet_html,
    fazer_upload_exame_pet,
    salvar_exame_pet,
    obter_exames_pet,
    salvar_acontecimento_pet,
    obter_acontecimentos_pet,
    fazer_upload_foto_acontecimento,
    editar_acontecimento_pet
)
from paginas.agentes_funcoes import (
    relator
)


coluna_logo, coluna_titulo = st.columns([1, 10])

with coluna_logo:
    st.image('arquivos/imagem_logo.png', use_container_width = True)

with coluna_titulo:
    st.title("Pelunos")
    st.markdown("*Bem-vindo ao Pelunos! Aqui você pode acompanhar seus pets e acessar todas as funcionalidades.*")

# CSS global para padronizar tamanhos dos botões
st.markdown("""
<style>
/* Garante que todos os botões tenham o mesmo tamanho */
.stButton > button {
    height: 40px !important;
    min-height: 40px !important;
    max-height: 40px !important;
    font-size: 14px !important;
    line-height: 1.2 !important;
    padding: 8px 16px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Ajusta o tamanho das colunas para distribuição igual */
[data-testid="column"] {
    width: 33.33% !important;
    flex: 1 1 33.33% !important;
}

/* Garante que os botões dos pets tenham tamanhos consistentes */
.pet-actions .stButton > button {
    height: 40px !important;
    min-height: 40px !important;
    max-height: 40px !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DIÁLOGO PARA ADICIONAR EXAME
# ============================================================================

@st.dialog("📄 Adicionar Exame", width = "large")
def dialog_adicionar_exame(pet_id, pet_nome):
    st.markdown(f"### Adicionar exame para **{pet_nome}**")
    
    with st.form("form_adicionar_exame"):
        nome_exame = st.text_input(
            "Nome/Descrição do Exame *",
            placeholder="Ex: Exame de Sangue, Raio-X, Ultrassom..."
        )
        
        arquivo_pdf = st.file_uploader(
            "Arquivo do Exame (PDF) *",
            type=['pdf'],
            help="Selecione o arquivo PDF do exame"
        )
        
        if arquivo_pdf is not None:
            st.info(f"📄 Arquivo selecionado: {arquivo_pdf.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("📄 Adicionar Exame", type="primary", use_container_width=True):
                if not nome_exame or not arquivo_pdf:
                    st.error("Por favor, preencha o nome do exame e selecione um arquivo PDF!")
                else:
                    with st.spinner("Fazendo upload do exame..."):
                        # Upload do PDF
                        url_pdf = fazer_upload_exame_pet(arquivo_pdf, pet_id, nome_exame)
                        
                        if url_pdf:
                            # Salva no Firestore
                            exame_id = salvar_exame_pet(pet_id, nome_exame, url_pdf)
                            
                            if exame_id:
                                st.success(f"✅ Exame '{nome_exame}' adicionado com sucesso!", width="stretch")
                                registrar_acao_usuario("Adicionar Exame", f"Usuário adicionou exame '{nome_exame}' para o pet {pet_nome}")
                                
                                # Encaminha as informações gerais do exame, tratadas pela IA, para o banco de dados
                                resultado = relator(pet_id = pet_id, exame_doc_id = exame_id, pdf = arquivo_pdf)
                                st.success(f"✅ Ótimo! Nosso assistente digital já estudou o exame de {pet_nome} e está pronto para conversar sobre os resultados.",
                                    width="stretch")
                            else:
                                st.error("❌ Erro ao salvar exame no banco de dados.")
                        else:
                            st.error("❌ Erro ao fazer upload do arquivo. Tente novamente.")
                    st.balloons()

                    # Pausa antes de fechar o diálogo
                    import time
                    time.sleep(5)
                    st.rerun()
                    
        
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.rerun()

# ============================================================================
# DIÁLOGO PARA REGISTRAR ACONTECIMENTO
# ============================================================================

@st.dialog("📝 Registrar Acontecimento", width = "large")
def dialog_registrar_acontecimento(pet_id, pet_nome):
    st.markdown(f"### Registrar acontecimento para **{pet_nome}**")
    
    with st.form("form_registrar_acontecimento"):
        col_data, col_hora = st.columns(2)
        
        with col_data:
            data_acontecimento = st.date_input(
                "Data do Acontecimento *",
                value=None,
                min_value=date(1980, 1, 1),
                max_value=date.today(),
                format="DD/MM/YYYY"
            )
        
        with col_hora:
            hora_acontecimento = st.time_input(
                "Hora do Acontecimento *",
                value=None
            )
        
        descricao = st.text_area(
            "Descrição do Acontecimento *",
            placeholder="Descreva o que aconteceu com seu pet...",
            height=100
        )
        
        foto_acontecimento = st.file_uploader(
            "Foto do Acontecimento (opcional)",
            type=['png', 'jpg', 'jpeg'],
            help="Formatos aceitos: PNG, JPG, JPEG"
        )
        
        if foto_acontecimento is not None:
            st.image(foto_acontecimento, caption="Preview da foto", width=300)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("📝 Registrar Acontecimento", type="primary", use_container_width=True):
                if not data_acontecimento or not hora_acontecimento or not descricao:
                    st.error("Por favor, preencha a data, hora e descrição do acontecimento!")
                else:
                    with st.spinner("Registrando acontecimento..."):
                        # Combina data e hora em um datetime
                        data_hora = datetime.combine(data_acontecimento, hora_acontecimento)
                        
                        # Primeiro salva o acontecimento sem foto para obter o ID
                        acontecimento_id = salvar_acontecimento_pet(pet_id, data_hora, descricao)
                        
                        if acontecimento_id:
                            url_foto = None
                            
                            # Se há foto, faz o upload
                            if foto_acontecimento is not None:
                                with st.spinner("Fazendo upload da foto..."):
                                    url_foto = fazer_upload_foto_acontecimento(foto_acontecimento, pet_id, acontecimento_id)
                                
                                if url_foto:
                                    # Atualiza o acontecimento com a URL da foto
                                    editar_acontecimento_pet(acontecimento_id, pet_id, data_hora, descricao, url_foto)
                                    st.success("✅ Upload da foto concluído!")
                                else:
                                    st.warning("⚠️ Erro ao fazer upload da foto. Acontecimento registrado sem imagem.")
                            
                            st.success(f"✅ Acontecimento registrado com sucesso!", width="stretch")
                            registrar_acao_usuario("Registrar Acontecimento", f"Usuário registrou acontecimento para o pet {pet_nome}")
                        else:
                            st.error("❌ Erro ao registrar acontecimento no banco de dados.")
                    
                    st.balloons()

                    # Pausa antes de fechar o diálogo
                    import time
                    time.sleep(3)
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.rerun()

# ============================================================================
# DIÁLOGO PARA ADICIONAR MOTIVO DA CONSULTA
# ============================================================================
@st.dialog("🩺 Motivo da Consulta", width = "stretch")
def dialog_motivo_consulta(pet, formato="html"):
    st.markdown(f"### Adicione o principal motivo da consulta para {pet['nome']}")
    
    st.info("📋 Gerando relatório veterinário para download")

    with st.form("motivo_da_consulta"):
        motivo = st.text_area(
            label = "Qual o motivo da consulta? *",
            max_chars = 300,
            placeholder = "Ex: Meu cachorro está sem apetite e muito cansado nos últimos dias",
            height = 100
        )

        submitted = st.form_submit_button(
            "📋 Gerar Relatório",
            use_container_width=True,
            type="primary"
        )
        
        condicao = False
        html_content = None

        if submitted:
            # Validação para garantir que o campo não está vazio
            if not motivo:
                st.error("Por favor, preencha o motivo da consulta antes de gerar o relatório.")
            else:
                with st.spinner("Gerando o relatório, por favor aguarde..."):
                    html_content = gerar_relatorio_pet_html(pet, motivo_consulta=motivo)
                    st.success("✅ Relatório gerado com sucesso! Clique abaixo para baixar.")
                    condicao = True
    
    if condicao:
        # Botão para download do relatório
        st.download_button(
            label="💾 Baixar relatório",
            data=html_content,
            file_name=f"relatorio_{pet['nome']}.html",
            mime="text/html",
            use_container_width=True,
            type="primary"
        )



        

# ============================================================================
# WELCOME MESSAGE
# ============================================================================

# Informações do usuário
if hasattr(st.user, 'name') and st.user.name:
    st.markdown(f"### Olá, **{st.user.name}**! 👋")
else:
    st.markdown("### Olá! 👋")

# ============================================================================
# LISTAGEM DOS PETS CADASTRADOS
# ============================================================================

pets = obter_pets()

if len(pets) > 0: 
    st.subheader(f"🐾 Seus Pets ({len(pets)})")
    
    # Organiza pets em grupos de 3 para as colunas
    for i in range(0, len(pets), 3):
        cols = st.columns(3)
        
        # Para cada pet no grupo atual (máximo 3)
        for idx, pet in enumerate(pets[i:i+3]):
            with cols[idx]:
                # Container do pet com borda
                with st.container(border=True):
                    # Foto do pet centralizada
                    if pet["url_foto"]:
                        st.image(pet["url_foto"], use_container_width=True)
                    else:
                        st.markdown("🐾", help="Sem foto")
                    
                    # Nome do pet
                    st.markdown(f"### {pet['nome']}")
                    
                    # Informações básicas essenciais
                    st.markdown(f"**{pet['especie']}** • **{pet['raca']}**")
                    st.markdown(f"**{pet['sexo']}** • **{pet['idade']}**")
                    
                    # Contador de exames e acontecimentos
                    exames_count = len(obter_exames_pet(pet['id']))
                    acontecimentos_count = len(obter_acontecimentos_pet(pet['id']))
                    
                    if exames_count > 0:
                        st.markdown(f"📋 **{exames_count}** exame(s) cadastrado(s)")
                    else:
                        st.markdown("📋 Nenhum exame cadastrado")
                    
                    if acontecimentos_count > 0:
                        st.markdown(f"📝 **{acontecimentos_count}** acontecimento(s) registrado(s)")
                    else:
                        st.markdown("📝 Nenhum acontecimento registrado")
                    
                    
                    # Informações detalhadas agrupadas em "Saber mais"
                    with st.expander("ℹ️ Saber mais", expanded=False):
                        st.divider()
                        # Estrutura de coluna
                        coluna1, coluna2 = st.columns(2)
                        with coluna1:
                            # Informações de castração
                            if pet['castrado'] == "Sim":
                                castrado_icon = "✅"
                            elif pet['castrado'] == "Não":
                                castrado_icon = "❌"
                            elif pet['castrado'] == "Não sei":
                                castrado_icon = "❓"
                            else:
                                # Para pets antigos que podem ter valor boolean
                                castrado_icon = "✅" if pet['castrado'] else "❌"
                            st.markdown(f"**🔸 Castrado:** {castrado_icon} {pet['castrado']}")
                        
                        with coluna2:
                            # Data de cadastro
                            if pet["data_cadastro"]:
                                try:
                                    if hasattr(pet["data_cadastro"], "date"):
                                        data_formatada = pet["data_cadastro"].date().strftime("%d/%m/%Y")
                                    else:
                                        data_formatada = str(pet["data_cadastro"])[:10]
                                except:
                                    data_formatada = "Data não disponível"
                                st.markdown(f"**📅 Cadastrado em:** {data_formatada}")
                        
                        coluna3, coluna4 = st.columns(2)
                        with coluna3:
                            if pet['historia']:
                                st.markdown("**📖 História do Pet:**")
                                st.write(pet['historia'])
                        with coluna4:
                            if pet['saude']:
                                st.markdown("**🏥 Saúde Geral:**")
                                st.write(pet['saude'])
                        
                        if pet['alimentacao']:
                            st.markdown("**🍽️ Alimentação:**")
                            st.write(pet['alimentacao'])
                        
                        # Seção de exames
                        exames = obter_exames_pet(pet['id'])
                        if exames:
                            st.markdown("---")
                            st.markdown(f"**📋 Exames ({len(exames)}):**")
                            
                            for idx, exame in enumerate(exames, 1):
                                # Data do exame formatada
                                if exame["data_upload"]:
                                    try:
                                        if hasattr(exame["data_upload"], "date"):
                                            data_exame = exame["data_upload"].date().strftime("%d/%m/%Y")
                                            hora_exame = exame["data_upload"].strftime("%H:%M")
                                            data_completa = f"{data_exame} às {hora_exame}"
                                        else:
                                            data_completa = str(exame["data_upload"])[:19].replace("T", " às ")
                                    except:
                                        data_completa = "Data não disponível"
                                else:
                                    data_completa = "Data não disponível"
                                
                                # Exibe informações detalhadas do exame
                                st.markdown(f"**{idx}. {exame['nome_exame']}**")
                                st.markdown(f"   📅 **Enviado em:** {data_completa}")
                                
                                # Determina o tipo de exame baseado no nome
                                nome_lower = exame['nome_exame'].lower()
                                if any(palavra in nome_lower for palavra in ['sangue', 'hemograma', 'bioquimic']):
                                    tipo_exame = "🩸 Exame de Sangue"
                                elif any(palavra in nome_lower for palavra in ['raio', 'radiograf', 'rx']):
                                    tipo_exame = "📷 Raio-X"
                                elif any(palavra in nome_lower for palavra in ['ultra', 'ecograf']):
                                    tipo_exame = "📡 Ultrassom/Ecografia"
                                elif any(palavra in nome_lower for palavra in ['urina', 'urinalis']):
                                    tipo_exame = "🧪 Exame de Urina"
                                elif any(palavra in nome_lower for palavra in ['fezes', 'parasit']):
                                    tipo_exame = "🔬 Exame de Fezes"
                                elif any(palavra in nome_lower for palavra in ['cardiologico', 'coração', 'eco']):
                                    tipo_exame = "❤️ Exame Cardiológico"
                                elif any(palavra in nome_lower for palavra in ['oftalmologic', 'olho', 'visão']):
                                    tipo_exame = "👁️ Exame Oftalmológico"
                                else:
                                    tipo_exame = "📋 Exame Geral"
                                
                                st.markdown(f"   🏷️ **Tipo:** {tipo_exame}")
                                
                                if exame['url_pdf']:
                                    st.markdown(f"   [📄 Baixar PDF do Exame]({exame['url_pdf']})")
                                
                                if idx < len(exames):  # Não adiciona divisor após o último exame
                                    st.markdown("")
                        else:
                            st.markdown("---")
                            st.markdown("**📋 Exames:** Nenhum exame cadastrado")
                        
                    
                    # Expander específico para acontecimentos
                    acontecimentos = obter_acontecimentos_pet(pet['id'])
                    with st.expander(f"📝 Acontecimentos ({len(acontecimentos)})", expanded=False):
                        if acontecimentos:
                            for idx, acontecimento in enumerate(acontecimentos, 1):
                                # Data do acontecimento formatada
                                if acontecimento["data_hora"]:
                                    try:
                                        if hasattr(acontecimento["data_hora"], "strftime"):
                                            data_acontecimento = acontecimento["data_hora"].strftime("%d/%m/%Y")
                                            hora_acontecimento = acontecimento["data_hora"].strftime("%H:%M")
                                            data_completa = f"{data_acontecimento} às {hora_acontecimento}"
                                        else:
                                            data_completa = str(acontecimento["data_hora"])[:19].replace("T", " às ")
                                    except:
                                        data_completa = "Data não disponível"
                                else:
                                    data_completa = "Data não disponível"
                                
                                # Layout com foto à esquerda e informações à direita
                                col_foto, col_info = st.columns([1, 3])
                                
                                with col_foto:
                                    if acontecimento['url_foto']:
                                        st.image(acontecimento['url_foto'], use_container_width=True)
                                    else:
                                        st.markdown("📷")
                                
                                with col_info:
                                    st.markdown(f"**📅 {data_completa}**")
                                    st.markdown(f"📝 {acontecimento['descricao']}")
                                
                                if idx < len(acontecimentos):  # Adiciona divisor entre acontecimentos
                                    st.divider()
                        else:
                            st.markdown("Nenhum acontecimento registrado ainda.")
                    
                    # Botões de ação divididos em 3 colunas com tamanhos iguais
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        # Botão de gerar relatório
                        exames_pet = obter_exames_pet(pet['id'])
                        num_exames = len(exames_pet)
                        
                        if num_exames > 0:
                            help_text = f"Baixar relatório completo + {num_exames} exame(s) listado(s)"
                            label_texto = "📋 Gerar Relatório + Exames"
                        else:
                            help_text = "Baixar relatório veterinário completo"
                            label_texto = "📋 Gerar Relatório"

                        chave_unica_html = f"btn_gerar_relatorio_html_{pet['nome']}"
                        if st.button(label = label_texto, key=chave_unica_html, help = help_text, use_container_width=True,
                            type = "primary"):
                            dialog_motivo_consulta(pet)
                    
                    with col_btn2:
                        # Botão de adicionar exame
                        if st.button(
                            "📋 Adicionar Exame",
                            key=f"add_exame_{pet['id']}",
                            help="Adicionar exame em PDF",
                            use_container_width=True,
                            type="secondary"
                        ):
                            dialog_adicionar_exame(pet['id'], pet['nome'])
                    
                    with col_btn3:
                        # Botão de registrar acontecimento
                        if st.button(
                            "📝 Registrar Acontecimento",
                            key=f"add_acontecimento_{pet['id']}",
                            help="Registrar acontecimento do pet",
                            use_container_width=True,
                            type="secondary"
                        ):
                            dialog_registrar_acontecimento(pet['id'], pet['nome'])
                    

else:
    # Mensagem quando não há pets cadastrados
    st.info("🐾 **Você ainda não cadastrou nenhum pet!**")
    
    # Botão de ação direta
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Cadastrar Meu Pet", type="primary", use_container_width=True):
            st.switch_page("paginas/pets.py")

# ============================================================================
# RESUMO E AÇÕES RÁPIDAS
# ============================================================================

if len(pets) > 0:
    st.markdown("---")
    st.subheader("🎯 Ações Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Cadastrar Novo Pet", type="primary", use_container_width=True):
            st.switch_page("paginas/pets.py")
    
    with col2:
        if st.button("🩺 Conversar com Dr. Peluno", type="secondary", use_container_width=True):
            st.switch_page("paginas/chatbot.py")
    
    with col3:
        if st.button("👤 Ver Perfil", type="secondary", use_container_width=True):
            st.switch_page("paginas/perfil.py")

# ============================================================================
# INFORMAÇÕES SOBRE DR. PELUNO
# ============================================================================

# Seção simplificada - expander removido


