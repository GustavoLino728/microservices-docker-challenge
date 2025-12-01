import streamlit as st
import requests
import json

API_URL = "http://api:8080"

st.title("🧑‍💻 CRUD Usuários - Desafio 3")

try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    st.success("API e Redis conectados!")
except:
    st.error("Erro de conexão com API")

tab1, tab2, tab3 = st.tabs(["Listar", "Criar", "Editar/Deletar"])

with tab1:
    if st.button("🔄 Atualizar Lista"):
        try:
            response = requests.get(f"{API_URL}/users")
            users = response.json()
            st.dataframe(users)
            st.success(f"Carregado do cache Redis! ({len(users)} usuários)")
        except Exception as e:
            st.error(f"Erro: {e}")

with tab2:
    with st.form("create_user"):
        name = st.text_input("Nome")
        email = st.text_input("Email")
        if st.form_submit_button("Criar"):
            try:
                response = requests.post(f"{API_URL}/users", 
                                       json={"name": name, "email": email})
                if response.status_code == 201:
                    st.success("✅ Usuário criado!")
                    st.rerun()
                else:
                    st.error(response.json()["error"])
            except Exception as e:
                st.error(f"Erro: {e}")

with tab3:
    user_id = st.number_input("ID do usuário", min_value=1)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Deletar"):
            try:
                response = requests.delete(f"{API_URL}/users/{user_id}")
                if response.status_code == 200:
                    st.success("✅ Usuário deletado!")
                else:
                    st.error(response.json()["error"])
            except Exception as e:
                st.error(f"Erro: {e}")
    
    with col2:
        if st.button("👁️ Ver usuário"):
            try:
                response = requests.get(f"{API_URL}/users/{user_id}")
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.error("Usuário não encontrado")
            except Exception as e:
                st.error(f"Erro: {e}")