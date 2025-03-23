
import streamlit as st
import openai
import requests
import pytesseract
from PIL import Image

openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

def estrai_testo_da_immagine(img: Image.Image) -> str:
    return pytesseract.image_to_string(img).strip()

def cerca_fonti_online(query, max_results=3):
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": SERPAPI_KEY, "engine": "google", "num": max_results}
    response = requests.get(url, params=params)
    risultati = response.json()
    link_fonti = []
    for item in risultati.get("organic_results", []):
        titolo = item.get("title")
        link = item.get("link")
        if titolo and link:
            link_fonti.append(f"{titolo}: {link}")
    return link_fonti

def valuta_veridicità(claim, fonti):
    prompt = f"Claim: {claim}\n\nFonti:\n{chr(10).join(fonti)}\n\nValuta se il claim è Verificato, Parzialmente vero, Falso o Non verificabile."
    risposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto in fact-checking."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return risposta.choices[0].message.content.strip()

st.title("🕵️ Fact-checker Instagram")
claim_text = st.text_area("Inserisci un claim da verificare")

uploaded_image = st.file_uploader("Oppure carica un'immagine", type=["jpg", "png", "jpeg"])
if uploaded_image:
    img = Image.open(uploaded_image)
    st.image(img, caption="Immagine caricata", use_column_width=True)
    claim_text = estrai_testo_da_immagine(img)
    st.success("Testo estratto dall'immagine!")

if st.button("Analizza Claim"):
    if claim_text.strip() == "":
        st.error("Inserisci un claim valido o carica un'immagine.")
    else:
        with st.spinner("Analisi in corso..."):
            fonti = cerca_fonti_online(claim_text)
            valutazione = valuta_veridicità(claim_text, fonti)
        st.subheader("Risultato")
        st.write(f"**Claim:** {claim_text}")
        st.write("**Fonti trovate:**")
        for fonte in fonti:
            st.markdown(f"- {fonte}")
        st.write("**Valutazione AI:**")
        st.info(valutazione)
