import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Hemodynamic AI Dashboard",
    page_icon="🩺",
    layout="wide",
)

# --- Custom CSS for Mode B Highlighting ---
def apply_theme(mode_b):
    st.markdown("""
        <style>
        /* LIVE 표시등 깜빡임 애니메이션 */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        .live-indicator {
            color: #FF4B4B;
            font-weight: bold;
            animation: pulse 1s infinite;
        }
        </style>
    """, unsafe_allow_html=True)
    if mode_b:
        st.markdown("""
            <style>
            /* 헤더: 모드 B (위험) */
            .main-header {
                background-color: #FF4B4B !important;
                color: white !important;
                padding: 30px !important;
                border-radius: 15px !important;
                text-align: center !important;
                margin-bottom: 25px !important;
                border: 2px solid #000000 !important;
            }
            [data-testid="stMetric"] {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                padding: 15px !important;
                border-radius: 10px !important;
                border-left: 10px solid #FF4B4B !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            }
            [data-testid="stMetricValue"] > div { color: #FF4B4B !important; }
            [data-testid="stMetricLabel"] > div { color: #333333 !important; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            /* 헤더: 모드 A (정상) */
            .main-header {
                background-color: #F0F2F6 !important;
                color: #1E1E1E !important;
                padding: 30px !important;
                border-radius: 15px !important;
                text-align: center !important;
                margin-bottom: 25px !important;
                border: 1px solid #D0D0D0 !important;
            }
            [data-testid="stMetric"] {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                padding: 15px !important;
                border-radius: 10px !important;
                border-left: 10px solid #0068C9 !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            }
            [data-testid="stMetricValue"] > div { color: #0068C9 !important; }
            [data-testid="stMetricLabel"] > div { color: #333333 !important; }
            </style>
            """, unsafe_allow_html=True)

# --- Session State for History (Real-time Simulation) ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame({
        'Time': pd.Series(dtype='str'),
        'PAP': pd.Series(dtype='float'),
        'Flow': pd.Series(dtype='float'),
        'Temp': pd.Series(dtype='float')
    })

# --- Sidebar: Controls ---
st.sidebar.header("🎛️ Real-time Sensing Controls")
live_mode = st.sidebar.toggle("Real-time Simulation Mode", value=False, help="실제 센서 데이터처럼 미세한 떨림과 자동 갱신을 활성화합니다.")

pap_base = st.sidebar.slider("Pulmonary Artery Pressure (PAP) [mmHg]", 10, 60, 20)
flow_base = st.sidebar.slider("Blood Flow Rate [cm/s]", 10, 100, 50)
temp_base = st.sidebar.slider("Local Temperature [°C]", 36.0, 40.0, 37.0, step=0.1)

# --- Logic: Apply Real-time Jitter ---
if live_mode:
    # 슬라이더 값에 미세한 랜덤 노이즈 추가
    pap = pap_base + np.random.uniform(-1.0, 1.0)
    flow = flow_base + np.random.uniform(-2.5, 2.5)
    temp = temp_base + np.random.uniform(-0.05, 0.05)
    st.sidebar.markdown("<p class='live-indicator'>🔴 SENSING ACTIVE</p>", unsafe_allow_html=True)
else:
    pap = pap_base
    flow = flow_base
    temp = temp_base
    st.sidebar.markdown("<p style='color:gray;'>⚪ STANDBY</p>", unsafe_allow_html=True)

# --- Logic: Dual-Mode Trigger ---
# Mode B if PAP > 25, Flow < 30, or Temp > 38
is_mode_b = pap > 25 or flow < 30 or temp > 38.0
mode_label = "MODE B: Intensive Analysis" if is_mode_b else "MODE A: Monitoring"

apply_theme(is_mode_b)

# --- Header ---
st.markdown(f"<div class='main-header'><h1>Self-Powered Dual-Mode Hemodynamic Platform</h1><h3>Current Status: {mode_label}</h3></div>", unsafe_allow_html=True)

# --- Biomarker Mapping Logic ---
def get_biomarkers(p, f, t):
    nt_probnp = p * 12.5  # Simulated mapping
    ngal = (100 - f) * 1.5
    hscrp = "Elevated" if t > 38.0 else "Normal"
    return nt_probnp, ngal, hscrp

nt_val, ngal_val, hscrp_val = get_biomarkers(pap, flow, temp)

# --- AI Prognosis Logic ---
def get_prognosis(p, f, t):
    if p > 45 and f < 25:
        return "Cardiorenal Syndrome Type I", "Stage D", "🚨 72h Heart Failure Decompensation Risk: CRITICAL"
    elif p > 25:
        return "Cardiorenal Syndrome Type II", "Stage C", "⚠️ 72h Heart Failure Decompensation Risk: MODERATE"
    elif f < 30:
        return "Renal Risk Detected", "Stage B", "⚠️ 48h AKI Warning: MONITORING"
    else:
        return "Normal Hemodynamics", "Stage A", "✅ Condition Stable"

crs_type, hf_stage, risk_msg = get_prognosis(pap, flow, temp)

# --- Layout: Information Display ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🧬 Biomarker Mapping (AI-Inferred)")
    m1, m2, m3 = st.columns(3)
    m1.metric("NT-proBNP", f"{int(nt_val)} pg/mL", delta=f"{int(pap-25)}" if pap > 25 else None, delta_color="inverse")
    m2.metric("NGAL", f"{int(ngal_val)} ng/mL", delta=f"{int(30-flow)}" if flow < 30 else None, delta_color="inverse")
    m3.metric("hs-CRP", hscrp_val)
    
    st.caption("AI maps physical sensor data to biochemical markers in real-time.")

with col2:
    st.subheader("🧠 AI Prognosis Output")
    st.info(f"**Classification:** {crs_type}")
    st.info(f"**HF Stage:** {hf_stage}")
    
    if is_mode_b:
        st.error(risk_msg)
    else:
        st.success(risk_msg)

# --- Visualization: Real-time Data Streaming Simulation ---
st.divider()
st.subheader("📊 Hemodynamic Waveforms (Live Data)")

# Update history in session state
now = datetime.now().strftime("%H:%M:%S")
new_entry = pd.DataFrame({'Time': [now], 'PAP': [pap], 'Flow': [flow], 'Temp': [temp]})
st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True).tail(20)

# Multi-line chart for PAP, Flow, and Temp
chart_data = st.session_state.history.set_index('Time')
st.line_chart(chart_data)

st.markdown("""
**Note:** The waveform simulates the last 20 data points adjusted by the sidebar controls. 
In a production environment, this would be connected to the ESP32 serial/BLE stream.
""")

# --- Sidebar Footer ---
st.sidebar.divider()
st.sidebar.info("Developed for Hemodynamic Monitoring Research. Dual-mode logic ensures efficient power usage and critical event detection.")

# --- Auto-refresh for Live Simulation ---
if live_mode:
    time.sleep(0.5)  # 0.5초마다 갱신
    st.rerun()

