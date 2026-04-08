"""
dashboard.py
Dashboard Streamlit para SIT-RFID — Estilo industrial/tech
Ejecutar: streamlit run dashboard.py
"""
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(
    page_title="SIT-RFID | Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API     = "http://localhost:5000/api"
TIMEOUT = 3

# ══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700;900&display=swap');

html, body, .stApp {
    background-color: #0a0c10 !important;
    color: #c8d0e0;
    font-family: 'Barlow', sans-serif;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section.main > div { padding: 0 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #10141c !important;
    border-bottom: 1px solid #1e2535 !important;
    padding: 0 24px !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4a5568 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
    padding: 14px 20px !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ff88 !important;
    border-bottom: 2px solid #00ff88 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #0a0c10 !important;
    padding: 20px 24px !important;
}

/* Inputs */
.stTextInput input {
    background: #10141c !important;
    border: 1px solid #1e2535 !important;
    color: #c8d0e0 !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput input:focus {
    border-color: #00ff88 !important;
    box-shadow: 0 0 0 1px #00ff88 !important;
}
.stTextInput label {
    color: #4a5568 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: #10141c !important;
    border-color: #1e2535 !important;
    color: #c8d0e0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stSelectbox label {
    color: #4a5568 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Botones */
.stButton > button {
    background: #10141c !important;
    border: 1px solid #1e2535 !important;
    color: #c8d0e0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #00ff88 !important;
    color: #00ff88 !important;
    background: rgba(0,255,136,0.05) !important;
}

/* Alertas */
.stSuccess, .stWarning, .stError {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    border-radius: 8px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e2535; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=TIMEOUT)
        return r.json()
    except:
        return {}

def api_post(path, body):
    try:
        r = requests.post(f"{API}{path}", json=body, timeout=TIMEOUT)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_patch(path, body):
    try:
        requests.patch(f"{API}{path}", json=body, timeout=TIMEOUT)
        st.cache_data.clear()
    except:
        pass

@st.cache_data(ttl=2)
def fetch_stats():
    return api_get("/turns/stats").get("data", {})

@st.cache_data(ttl=2)
def fetch_turns():
    return api_get("/turns").get("data", [])

@st.cache_data(ttl=2)
def fetch_detections():
    return api_get("/detect/recent").get("data", [])

@st.cache_data(ttl=3)
def fetch_vehicles():
    return api_get("/vehicles").get("data", [])

def check_api():
    try:
        r = requests.get(f"{API}/health", timeout=2)
        return r.json().get("ok", False)
    except:
        return False

STATUS_MAP = {
    "waiting":   ("#ffd60a", "⏳ Esperando"),
    "attending": ("#00ff88", "▶ Atendiendo"),
    "done":      ("#4a5568", "✓ Finalizado"),
    "cancelled": ("#ff3b5c", "✕ Cancelado"),
}


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
api_ok   = check_api()
stats    = fetch_stats()
now_str  = datetime.now().strftime("%H:%M:%S")
date_str = datetime.now().strftime("%d/%m/%Y")
dot_col  = "#00ff88" if api_ok else "#ff3b5c"
api_lbl  = "API ONLINE" if api_ok else "API OFFLINE"

st.markdown(f"""
<div style="background:#10141c;border-bottom:1px solid #1e2535;
            padding:14px 28px;display:flex;align-items:center;
            justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="width:44px;height:44px;border:2px solid #00ff88;border-radius:10px;
                display:flex;align-items:center;justify-content:center;font-size:22px;
                box-shadow:0 0 16px rgba(0,255,136,0.3);">🚗</div>
    <div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:20px;
                  color:#00ff88;letter-spacing:3px;">SIT-RFID</div>
      <div style="font-size:10px;color:#4a5568;letter-spacing:3px;text-transform:uppercase;">
        Sistema Inteligente de Turnos</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:32px;">
    <div style="display:flex;align-items:center;gap:8px;">
      <div style="width:9px;height:9px;background:{dot_col};border-radius:50%;
                  box-shadow:0 0 8px {dot_col};"></div>
      <span style="font-family:'Share Tech Mono',monospace;font-size:12px;
                   color:{dot_col};">{api_lbl}</span>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'Share Tech Mono',monospace;font-size:26px;
                  color:#ffd60a;letter-spacing:3px;">{now_str}</div>
      <div style="font-size:10px;color:#4a5568;letter-spacing:2px;">{date_str}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STATS BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='padding:16px 24px 0;'>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

def stat_card(col, icon, value, label, color):
    col.markdown(f"""
    <div style="background:#10141c;border:1px solid #1e2535;border-radius:12px;
                padding:18px 20px;display:flex;align-items:center;gap:16px;">
      <div style="font-size:30px;width:52px;height:52px;display:flex;align-items:center;
                  justify-content:center;background:rgba(255,255,255,0.04);
                  border-radius:10px;">{icon}</div>
      <div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:38px;
                    font-weight:700;color:{color};line-height:1;">{value}</div>
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:3px;
                    color:#4a5568;margin-top:4px;">{label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

stat_card(c1, "📋", stats.get("total",0),     "Total hoy",   "#00b4ff")
stat_card(c2, "⏳", stats.get("waiting",0),   "En espera",   "#ffd60a")
stat_card(c3, "✅", stats.get("attending",0), "Atendiendo",  "#00ff88")
stat_card(c4, "🏁", stats.get("done",0),      "Finalizados", "#4a5568")

st.markdown("</div><div style='height:4px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🚦  Cola de Turnos",
    "📷  Detecciones en Vivo",
    "🚗  Vehículos Registrados",
    "➕  Registrar Vehículo",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — COLA DE TURNOS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    turns = fetch_turns()

    st.markdown("""
    <div style="display:grid;grid-template-columns:60px 150px 120px 90px 70px 150px 1fr;
                gap:8px;padding:10px 16px;border-bottom:1px solid #1e2535;
                font-family:'Share Tech Mono',monospace;font-size:10px;
                letter-spacing:2px;color:#4a5568;text-transform:uppercase;">
      <div>#</div><div>Placa</div><div>Tipo</div>
      <div>Confianza</div><div>Hora</div><div>Estado</div><div>Acción</div>
    </div>
    """, unsafe_allow_html=True)

    if not turns:
        st.markdown("""
        <div style="text-align:center;padding:70px;color:#4a5568;
                    font-family:'Share Tech Mono',monospace;letter-spacing:2px;">
          <div style="font-size:52px;margin-bottom:14px;">🚦</div>
          SIN TURNOS AÚN HOY
        </div>""", unsafe_allow_html=True)
    else:
        for t in turns:
            color, label = STATUS_MAP.get(t["status"], ("#fff", t["status"]))
            hora  = str(t["created_at"])[11:16]
            score = f"{t['score']:.0f}%" if t.get("score") else "—"
            ptype = (t.get("plate_type") or "—").upper()
            num   = str(t["turn_number"]).zfill(2)

            st.markdown(f"""
            <div style="display:grid;
                        grid-template-columns:60px 150px 120px 90px 70px 150px 1fr;
                        gap:8px;padding:14px 16px;
                        border-bottom:1px solid rgba(30,37,53,0.7);align-items:center;">
              <div style="font-family:'Share Tech Mono',monospace;font-size:26px;
                          font-weight:700;color:#ffd60a;">{num}</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:18px;
                          font-weight:700;letter-spacing:3px;">{t['plate']}</div>
              <div style="font-size:11px;color:#4a5568;text-transform:uppercase;
                          letter-spacing:1px;">{ptype}</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:14px;
                          color:#00b4ff;">{score}</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:12px;
                          color:#4a5568;">{hora}</div>
              <div><span style="padding:4px 14px;border-radius:14px;font-size:10px;
                                font-family:'Share Tech Mono',monospace;letter-spacing:1px;
                                background:rgba(255,255,255,0.04);
                                color:{color};border:1px solid {color};">{label}</span></div>
            </div>
            """, unsafe_allow_html=True)

            _, ba, bd, bc, _ = st.columns([0.4, 1, 1, 1, 2])
            if t["status"] == "waiting":
                with ba:
                    if st.button("▶ Atender", key=f"a{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"attending"})
                        st.rerun()
            if t["status"] == "attending":
                with bd:
                    if st.button("✓ Finalizar", key=f"d{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"done"})
                        st.rerun()
            if t["status"] in ("waiting","attending"):
                with bc:
                    if st.button("✕ Cancelar", key=f"c{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"cancelled"})
                        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — DETECCIONES EN VIVO
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    detections = fetch_detections()
    col_l, col_r = st.columns([1, 1.4])

    with col_l:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                    letter-spacing:3px;color:#4a5568;text-transform:uppercase;
                    margin-bottom:16px;">● LIVE — ÚLTIMA DETECCIÓN</div>
        """, unsafe_allow_html=True)

        if not detections:
            st.markdown("""
            <div style="background:#10141c;border:1px solid #1e2535;border-radius:12px;
                        padding:60px 20px;text-align:center;color:#4a5568;
                        font-family:'Share Tech Mono',monospace;letter-spacing:2px;">
              <div style="font-size:48px;margin-bottom:12px;">📷</div>
              ESPERANDO CÁMARA...
            </div>""", unsafe_allow_html=True)
        else:
            d        = detections[0]
            is_known = bool(d.get("is_known"))
            bc       = "#ff3b5c" if is_known else "#00ff88"
            shadow   = f"0 0 40px rgba({'255,59,92' if is_known else '0,255,136'},0.35)"
            msg      = "⚠️ YA REGISTRADA" if is_known else "✅ NUEVA — TURNO ASIGNADO"
            sub      = "No se agregó a la base de datos" if is_known else "Registrada correctamente"
            conf     = d.get("confidence", 0)
            hora     = str(d.get("detected_at",""))[11:19]

            st.markdown(f"""
            <div style="background:#10141c;border:2px solid {bc};border-radius:14px;
                        padding:28px;box-shadow:{shadow};text-align:center;">
              <div style="background:#fff;border-radius:10px;padding:14px 30px;
                          display:inline-block;margin-bottom:20px;min-width:220px;">
                <div style="font-size:9px;font-weight:700;letter-spacing:4px;
                            color:#1a1a2e;margin-bottom:2px;">🇨🇴  COLOMBIA</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:46px;
                            font-weight:900;color:#0d0d0d;letter-spacing:7px;">
                  {d['plate']}
                </div>
              </div>
              <div style="margin-bottom:16px;">
                <div style="display:inline-block;padding:7px 20px;border-radius:20px;
                            background:rgba(255,255,255,0.05);color:{bc};
                            border:1px solid {bc};font-family:'Share Tech Mono',monospace;
                            font-size:12px;letter-spacing:2px;font-weight:700;">{msg}</div>
                <div style="font-size:11px;color:#4a5568;margin-top:6px;">{sub}</div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:left;">
                <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:9px;
                              color:#4a5568;letter-spacing:2px;">CONFIANZA OCR</div>
                  <div style="font-family:'Share Tech Mono',monospace;font-size:26px;
                              color:#00b4ff;font-weight:700;">{conf:.0f}%</div>
                </div>
                <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;">
                  <div style="font-family:'Share Tech Mono',monospace;font-size:9px;
                              color:#4a5568;letter-spacing:2px;">HORA</div>
                  <div style="font-family:'Share Tech Mono',monospace;font-size:26px;
                              color:#ffd60a;font-weight:700;">{hora}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                    letter-spacing:3px;color:#4a5568;text-transform:uppercase;
                    margin-bottom:16px;">HISTORIAL RECIENTE</div>
        """, unsafe_allow_html=True)

        if not detections:
            st.markdown("""<div style="color:#4a5568;font-family:'Share Tech Mono',monospace;
                            font-size:12px;letter-spacing:2px;">Sin detecciones aún</div>""",
                        unsafe_allow_html=True)
        else:
            for d in detections:
                is_k  = bool(d.get("is_known"))
                col   = "#ff3b5c" if is_k else "#00ff88"
                badge = "EXISTENTE" if is_k else "NUEVA"
                hora  = str(d.get("detected_at",""))[11:16]
                conf  = d.get("confidence", 0)
                bg    = "rgba(255,59,92,0.04)" if is_k else "rgba(0,255,136,0.04)"

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                            border-radius:8px;margin-bottom:6px;background:{bg};
                            border:1px solid rgba(255,255,255,0.04);">
                  <div style="width:9px;height:9px;background:{col};border-radius:50%;
                              flex-shrink:0;box-shadow:0 0 6px {col};"></div>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:17px;
                               font-weight:700;letter-spacing:3px;flex:1;">{d['plate']}</span>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:11px;
                               color:#00b4ff;">{conf:.0f}%</span>
                  <span style="padding:3px 10px;border-radius:10px;font-size:9px;
                               background:rgba(255,255,255,0.04);color:{col};
                               border:1px solid {col};font-family:'Share Tech Mono',monospace;
                               letter-spacing:1px;">{badge}</span>
                  <span style="font-family:'Share Tech Mono',monospace;font-size:11px;
                               color:#4a5568;min-width:40px;">{hora}</span>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — VEHÍCULOS REGISTRADOS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    vehicles = fetch_vehicles()
    search   = st.text_input("🔍 Buscar por placa", placeholder="Ej: ABC123",
                              label_visibility="collapsed")
    filtered = [v for v in vehicles if not search or search.upper() in v["plate"]]

    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:10px;letter-spacing:3px;
                color:#4a5568;text-transform:uppercase;margin:8px 0 16px;">
      {len(filtered)} VEHÍCULOS
    </div>""", unsafe_allow_html=True)

    if not filtered:
        st.markdown("""
        <div style="text-align:center;padding:60px;color:#4a5568;
                    font-family:'Share Tech Mono',monospace;letter-spacing:2px;">
          <div style="font-size:48px;margin-bottom:12px;">🚗</div>
          SIN VEHÍCULOS REGISTRADOS
        </div>""", unsafe_allow_html=True)
    else:
        cols_v = st.columns(2)
        for i, v in enumerate(filtered):
            active = bool(v.get("active", 1))
            color  = "#00ff88" if active else "#4a5568"
            estado = "ACTIVO" if active else "INACTIVO"
            turns  = v.get("total_turns", 0)
            owner  = v.get("owner_name") or "Sin propietario"
            doc    = v.get("owner_doc")  or "—"
            fecha  = str(v.get("created_at",""))[:10]
            ptype  = (v.get("plate_type") or "—").upper()

            with cols_v[i % 2]:
                st.markdown(f"""
                <div style="background:#10141c;border:1px solid #1e2535;
                            border-left:3px solid {color};border-radius:10px;
                            padding:16px 18px;margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;
                              align-items:center;margin-bottom:10px;">
                    <span style="font-family:'Share Tech Mono',monospace;font-size:20px;
                                 font-weight:700;letter-spacing:4px;">{v['plate']}</span>
                    <div style="display:flex;align-items:center;gap:10px;">
                      <span style="font-size:10px;color:#4a5568;text-transform:uppercase;
                                   letter-spacing:2px;">{ptype}</span>
                      <span style="font-family:'Share Tech Mono',monospace;font-size:10px;
                                   color:{color};letter-spacing:2px;">● {estado}</span>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;
                              font-size:12px;color:#4a5568;margin-bottom:8px;">
                    <div>👤 {owner}</div>
                    <div>🪪 {doc}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;
                              font-family:'Share Tech Mono',monospace;font-size:11px;">
                    <span style="color:#00b4ff;">🎫 {turns} turno{'s' if turns!=1 else ''}</span>
                    <span style="color:#4a5568;">📅 {fecha}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — REGISTRAR VEHÍCULO
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    col_f, col_p = st.columns([1, 1])

    with col_f:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                    letter-spacing:3px;color:#4a5568;text-transform:uppercase;
                    margin-bottom:20px;">REGISTRO MANUAL</div>
        """, unsafe_allow_html=True)

        plate_in = st.text_input("Placa *", placeholder="Ej: ABC123",
                                  max_chars=7).upper().replace(" ","")
        ptype_in = st.selectbox("Tipo de vehículo", ["particular","moto","diplomatica"])
        oname_in = st.text_input("Nombre del propietario", placeholder="Opcional")
        odoc_in  = st.text_input("Documento", placeholder="Opcional")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("➕  Registrar Vehículo", use_container_width=True):
            if not plate_in:
                st.error("⚠️ La placa es obligatoria.")
            else:
                res = api_post("/vehicles", {
                    "plate": plate_in, "plate_type": ptype_in,
                    "owner_name": oname_in or None,
                    "owner_doc":  odoc_in  or None
                })
                if res.get("ok"):
                    st.success(f"✅ {res.get('message','Vehículo registrado.')}")
                    st.cache_data.clear()
                elif res.get("error") == "PLATE_EXISTS":
                    st.warning(f"⚠️ La placa **{plate_in}** ya está registrada en la base de datos.")
                else:
                    st.error(f"Error: {res.get('error','desconocido')}")

    with col_p:
        preview = plate_in if plate_in else "ABC123"
        bc_p    = "#00ff88"
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    padding:40px 20px;gap:20px;">
          <div style="background:#fff;border-radius:10px;padding:18px 34px;
                      text-align:center;min-width:230px;
                      box-shadow:0 0 30px rgba(0,255,136,0.25);
                      border:2px solid {bc_p};">
            <div style="font-size:9px;font-weight:700;letter-spacing:4px;
                        color:#1a1a2e;margin-bottom:4px;">🇨🇴  COLOMBIA</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:44px;
                        font-weight:900;color:#0d0d0d;letter-spacing:7px;">{preview}</div>
          </div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                      color:#4a5568;letter-spacing:3px;text-transform:uppercase;">
            {ptype_in.upper()} · PREVISUALIZACIÓN
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH cada 3 segundos
# ══════════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH cada 3 segundos
st.markdown("""
<script>setTimeout(function(){window.location.reload();}, 3000);</script>
""", unsafe_allow_html=True)