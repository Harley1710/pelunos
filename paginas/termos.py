import streamlit as st
import os 

st.title("📜 Termos de Uso e Política de Privacidade")
st.markdown("*Modelo de IA Especialista em Pets*")
st.markdown("---")

# Caminho do arquivo termos_e_privacidade.md (na raiz do projeto)
termos_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'termos_e_privacidade.md')

try:
    # Ler o conteúdo do arquivo
    with open(termos_path, 'r', encoding='utf-8') as file:
        termos_content = file.read()

    # Exibir o conteúdo
    st.markdown(termos_content, unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"Erro: Arquivo {termos_path} não encontrado. Verifique se o arquivo 'termos_e_privacidade.md' existe na raiz do projeto.")
except Exception as e:
    st.error(f"Ocorreu um erro ao ler o arquivo de termos: {e}")

st.divider()

st.page_link("paginas/chatbot.py", label="🐾 Voltar para Dr. Tobias", icon="🏃")