import streamlit as st
from supabase import create_client, Client

# --- CONFIGURAÇÃO DO BANCO (MANTENHA SUAS CHAVES AQUI) ---
# Se você usa segredos do Streamlit, mantenha como está abaixo:
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Meteorologia 360", page_icon="⛈️")
st.title("⛈️ Meteorologia 360 - Sistema de Monitoramento")

# --- CRIAÇÃO DAS ABAS ---
aba_registrar, aba_monitorar = st.tabs(["📝 Registrar Ocorrência", "📊 Painel de Controle"])

# --- ABA 1: REGISTRAR (O que você pediu agora) ---
with aba_registrar:
    st.header("Registrar Tempo Severo")
    with st.form("form_evento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cidade = st.text_input("📍 Cidade:", placeholder="Ex: Marataízes")
            estado = st.selectbox("Estado:", ["ES", "RJ", "MG", "SP", "Outro"])
        with col2:
            evento = st.selectbox("⚠️ Tipo de Evento:", ["Chuva Forte", "Granizo", "Vendaval", "Raios", "Inundação"])
            data = st.date_input("Data da Ocorrência")

        detalhes = st.text_area("📄 Descrição Detalhada:", placeholder="Conte o que aconteceu...")
        
        botao_enviar = st.form_submit_button("Enviar Registro para o Sistema 🚀")

    if botao_enviar:
        if cidade and detalhes:
            dados = {"cidade": cidade, "estado": estado, "evento": evento, "detalhes": detalhes}
            supabase.table("relatos_tempo").insert(dados).execute()
            st.success(f"✅ Sucesso! Ocorrência em {cidade} foi registrada.")
        else:
            st.error("❌ Por favor, preencha a cidade e a descrição.")

# --- ABA 2: MONITORAR E RELATÓRIO ---
with aba_monitorar:
    st.header("🕵️ Relatos Recebidos")
    
    # Buscar dados do banco
    res = supabase.table("relatos_tempo").select("*").order("id", desc=True).execute()
    
    if res.data:
        # Criar o arquivo para o Google Docs
        html_doc = "<html><head><meta charset='utf-8'></head><body><h1>Relatório Clima</h1>"
        for r in res.data:
            html_doc += f"<h3>📍 {r['cidade']} - {r['evento']}</h3><p>{r['detalhes']}</p><hr>"
        html_doc += "</body></html>"

        # Botão de Baixar
        st.download_button(
            label="📄 Baixar Relatório para Google Docs",
            data=html_doc,
            file_name="relatorio_meteorologia.html",
            mime="text/html"
        )
        
        st.divider()
        
        # Mostrar os cards na tela
        for r in res.data:
            with st.container(border=True):
                st.subheader(f"{r['evento']} em {r['cidade']} - {r['estado']}")
                st.write(r['detalhes'])
