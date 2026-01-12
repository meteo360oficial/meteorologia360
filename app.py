import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime

# 1. CONEXÃO
SUPABASE_URL = "https://edaxcbqgjxnebpioanjf.supabase.co"
SUPABASE_KEY = "sb_publishable_oMpyFsCZS_YEis0iIYjAEQ_H7EWFJmj"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Relatos de tempo severo | Meteorologia360 - METEO", page_icon="⛈️", layout="wide")

# TÍTULO E ABAS
st.markdown("<h1 style='text-align: center; color: #1E3D59;'>⛈️ Relatos de tempo severo | Meteorologia360 - METEO</h1>", unsafe_allow_html=True)
aba_registro, aba_dashboard = st.tabs(["📍 Registrar Ocorrência", "📊 Painel de Monitoramento"])

# --- ABA 1: REGISTRO ---
with aba_registro:
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            cidade = st.text_input("Cidade *")
            estado = st.selectbox("Estado", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=7)
            evento = st.selectbox("Evento", ["Granizo", "Vendaval", "Tornado", "Raios", "Alagamento", "Outro"])
            detalhes = st.text_area("Descrição do ocorrido")

    with col2:
        with st.container(border=True):
            lat = st.text_input("Latitude (Opcional)")
            lon = st.text_input("Longitude (Opcional)")
            arquivo = st.file_uploader("📸 Enviar Foto da Ocorrência", type=['jpg', 'png', 'jpeg'])

    if st.button("🚀 ENVIAR RELATO COMPLETO"):
        if cidade:
            url_publica = None
            
            # LÓGICA DE UPLOAD DA FOTO
            if arquivo:
                try:
                    nome_arquivo = f"{datetime.datetime.now().timestamp()}_{arquivo.name}"
                    # Envia para o bucket fotos_clima
                    supabase.storage.from_("fotos_clima").upload(nome_arquivo, arquivo.getvalue())
                    # Pega o link da foto
                    url_publica = supabase.storage.from_("fotos_clima").get_public_url(nome_arquivo)
                except Exception as e:
                    st.error(f"Erro ao subir imagem: {e}")

            # SALVANDO NO BANCO
            dados = {
                "cidade": cidade, 
                "estado": estado, 
                "evento": evento, 
                "detalhes": detalhes,
                "url_foto": url_publica # Aqui salva o link da imagem!
            }
            if lat and lon:
                dados["evento"] = f"{evento} [GPS: {lat},{lon}]"

            try:
                supabase.table("relatos_tempo").insert(dados).execute()
                st.balloons()
                st.success("✅ Relato enviado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")
        else:
            st.warning("Preencha os campos obrigatórios!")

# --- ABA 2: DASHBOARD ---
with aba_dashboard:
    st.subheader("🕵️ Últimos Relatos com Evidências")
    try:
        res = supabase.table("relatos_tempo").select("*").order("created_at", desc=True).limit(15).execute()
        if res.data:
            for item in res.data:
                with st.expander(f"📍 {item['cidade']} - {item['evento']} ({item['created_at'][:10]})"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        if item.get('url_foto'):
                            st.image(item['url_foto'], use_container_width=True)
                        else:
                            st.info("Sem foto disponível")
                    with c2:
                        st.write(f"**Estado:** {item['estado']}")
                        st.write(f"**Relato:** {item['detalhes']}")
        else:
            st.info("Nenhum dado encontrado.")
    except Exception as e:

        st.error(f"Erro ao carregar painel: {e}")

# --- BOTÃO DE RELATÓRIO PARA GOOGLE DOCS ---
st.sidebar.markdown("---")
st.sidebar.subheader("Relatórios")
try:
    # Busca os dados para o relatório
    rel_res = supabase.table("relatos_tempo").select("*").order("id", desc=True).execute()
    if rel_res.data:
        html_doc = "<html><head><meta charset='utf-8'></head><body>"
        html_doc += "<h1>Relatório de Ocorrências - Meteorologia 360</h1>"
        for r in rel_res.data:
            html_doc += f"<h3>📍 {r['cidade']} - {r['estado']}</h3>"
            html_doc += f"<p><b>Evento:</b> {r['evento']}<br>"
            html_doc += f"<b>Descrição:</b> {r['detalhes']}</p>"
            if r.get('url_foto'):
                html_doc += f"<img src='{r['url_foto']}' width='300'><br>"
            html_doc += "<hr>"
        html_doc += "</body></html>"

        st.sidebar.download_button(
            label="📄 Baixar para Google Docs",
            data=html_doc,
            file_name="relatorio_meteorologia.html",
            mime="text/html"
        )
except Exception as e:
    pass
