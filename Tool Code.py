import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

st.set_page_config(page_title="HVAC Permit Duration Estimator", layout="centered")
st.title(" HVAC Tool - Versione Ottimizzata")

@st.cache_data
def load_data():
    return pd.read_excel("total_x_ANN_e_tool_with_sequence.xlsx")[[
        'Work Type', 'Borough', 'Fascia_Edificio', 'Duration', 'Permit Sequence'
    ]].dropna()

@st.cache_resource
def load_models():
    model_duration = joblib.load("model_duration.pkl")
    model_sequence = joblib.load("model_sequence.pkl")
    encoder = joblib.load("encoder.pkl")
    return model_duration, model_sequence, encoder

df = load_data()
model_duration, model_sequence, encoder = load_models()

st.markdown("""
Questo tool stima:
- La **durata** del progetto HVAC
- Il **numero stimato di rilasci del permesso**
- Due simulazioni Monte Carlo
""")

period_choice = st.radio("Analisi Totale o Ultimi 10 anni?", ["Totale", "Ultimi 10 anni"])
building_filter = st.radio("Analisi Totale o per Categoria di Edificio?", ["Totale", "Per categoria"])
building_class = st.selectbox("Fascia di altezza edificio:", df['Fascia_Edificio'].unique()) if building_filter == "Per categoria" else None
borough_filter = st.radio("Analisi Totale o per Quartiere?", ["Totale", "Specifico"])
borough_choice = st.selectbox("Scegli il borough:", df['Borough'].unique()) if borough_filter == "Specifico" else None
work_type = st.selectbox("Tipo di intervento HVAC:", df['Work Type'].unique())

filtered_df = df.copy()
if building_class:
    filtered_df = filtered_df[filtered_df['Fascia_Edificio'] == building_class]
if borough_choice:
    filtered_df = filtered_df[filtered_df['Borough'] == borough_choice]
filtered_df = filtered_df[filtered_df['Work Type'] == work_type]

st.subheader(" Durata Stimata + Permit Sequence")

input_df = pd.DataFrame([{
    "Work Type": work_type,
    "Borough": borough_choice if borough_choice else "MANHATTAN",
    "Fascia_Edificio": building_class if building_class else "EDIFICI 6-10 PIANI"
}])

try:
    encoded_input = encoder.transform(input_df)
    predicted_duration = model_duration.predict(encoded_input)[0]
    predicted_sequence = model_sequence.predict(encoded_input)[0]
    st.success(f"Durata stimata: {predicted_duration:.1f} giorni")
    st.info(f"Numero stimato di rilasci del permesso (Permit Sequence): {predicted_sequence}")
except Exception as e:
    st.error("Errore nella previsione.")
    st.exception(e)

st.subheader(" Simulazione Monte Carlo - Durata")

if not filtered_df.empty:
    durations = filtered_df['Duration'].dropna()
    mu, sigma = durations.mean(), durations.std()
    simulated = np.random.normal(mu, sigma, 10000)
    simulated = simulated[simulated > 0]

    fig, ax = plt.subplots()
    ax.hist(simulated, bins=50, color='skyblue', edgecolor='black')
    ax.axvline(mu, color='red', linestyle='--', label=f"Media: {mu:.1f} giorni")
    ax.axvline(np.percentile(simulated, 5), color='orange', linestyle=':', label='5° percentile')
    ax.axvline(np.percentile(simulated, 95), color='green', linestyle=':', label='95° percentile')
    ax.set_title("Distribuzione durata simulata")
    ax.set_xlabel("Durata (giorni)")
    ax.set_ylabel("Frequenza")
    ax.legend()
    st.pyplot(fig)

    st.info(f"Durata media simulata: {mu:.1f} giorni")
    st.info(f"Intervallo 90% confidenza: {np.percentile(simulated, 5):.1f} - {np.percentile(simulated, 95):.1f} giorni")
else:
    st.warning("Non ci sono abbastanza dati per la simulazione della durata.")

st.subheader(" Simulazione Monte Carlo su Permit Sequence")

if not filtered_df.empty:
    sequences = filtered_df['Permit Sequence'].dropna().astype(int)
    sequence_counts = sequences.value_counts(normalize=True).sort_index()
    simulated_sequence = np.random.choice(sequence_counts.index, size=10000, p=sequence_counts.values)

    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_sequence, bins=np.arange(simulated_sequence.min(), simulated_sequence.max()+2)-0.5,
             color='lightgreen', edgecolor='black', rwidth=0.8)
    ax2.set_title("Distribuzione simulata dei rilasci del permesso")
    ax2.set_xlabel("Numero di rilasci (Permit Sequence)")
    ax2.set_ylabel("Frequenza")
    st.pyplot(fig2)

    p_multiple = np.mean(simulated_sequence >= 2) * 100
    st.info(f"Probabilità stimata di dover richiedere 2 o più rilasci: {p_multiple:.1f}%")
else:
    st.warning("Non ci sono abbastanza dati per simulare la Permit Sequence.")

st.subheader(" Analisi Rinnovo Permesso (Soglia Personalizzata)")

threshold = st.slider("Imposta la soglia durata massima prima di dover rinnovare il permesso (giorni):", 30, 365, 120, step=10)

if not filtered_df.empty:
    simulated_threshold_exceeded = simulated[simulated > threshold]
    p_exceeded = len(simulated_threshold_exceeded) / len(simulated) * 100
    st.info(f"Probabilità stimata di superare la soglia di {threshold} giorni: {p_exceeded:.1f}%")
else:
    st.warning("Dati insufficienti per stimare la probabilità di sforo soglia.")
