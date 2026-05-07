"""
dashboard.py — SIT-RFID | Centro de Control Inteligente
Versión responsiva para producción (Railway / Docker)
"""
import streamlit as st
import requests
import os

st.set_page_config(
    page_title="SIT-RFID | Control",
    page_icon="🛰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API     = os.getenv("API_URL", "http://localhost:5000") + "/api"
TIMEOUT = 3
PIN     = "1234"
USUARIOS = {
    "felipeocompo277@hotmail.com": "andres123",
    "admin": "andres123",
}

# ══════════════════════════════════════════════════════════════════════════════
# CSS — RESPONSIVO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Exo+2:wght@300;400;600;700&display=swap');

:root {
  --bg0:#020c18; --bg1:#041428; --bg2:#071e38; --bg3:#0a2848;
  --cyan:#00d4ff; --amber:#ffb800; --green:#00ff88;
  --red:#ff3355; --purple:#a78bfa;
  --text:#a8d4f0; --muted:#2a4a6a; --border:#0d3355;
}

/* ── Reset responsivo ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
  background: var(--bg0) !important;
  background-image: radial-gradient(ellipse 90% 60% at 50% -5%,rgba(0,120,255,.2) 0%,transparent 65%) !important;
  color: var(--text);
  font-family: 'Rajdhani', sans-serif;
  overflow-x: hidden !important;
}

#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;}

.block-container {
  padding: 0 12px !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
}
section.main > div { padding: 0 !important; }

/* ── Animaciones ── */
@keyframes pulse-cyan  {0%,100%{box-shadow:0 0 8px var(--cyan),0 0 20px rgba(0,212,255,.15)}50%{box-shadow:0 0 20px var(--cyan),0 0 50px rgba(0,212,255,.4)}}
@keyframes pulse-green {0%,100%{box-shadow:0 0 8px var(--green),0 0 20px rgba(0,255,136,.15)}50%{box-shadow:0 0 20px var(--green),0 0 50px rgba(0,255,136,.4)}}
@keyframes pulse-amber {0%,100%{box-shadow:0 0 8px var(--amber),0 0 20px rgba(255,184,0,.15)}50%{box-shadow:0 0 20px var(--amber),0 0 50px rgba(255,184,0,.4)}}
@keyframes pulse-dot   {0%,100%{opacity:1}50%{opacity:.3}}
@keyframes fadeIn      {from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes loginIn     {from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #030e1e !important;
  border-right: 1px solid #081830 !important;
  min-width: 220px !important;
  max-width: 220px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebarNav"]    { display: none !important; }

section[data-testid="stSidebar"] .stButton > button {
  width: 100% !important; text-align: left !important;
  background: transparent !important; border: none !important;
  border-radius: 8px !important; color: #6b5a9e !important;
  font-family: 'Exo 2', sans-serif !important; font-size: 13px !important;
  padding: 10px 14px !important; transition: all .2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(167,139,250,.08) !important;
  color: #c4b5fd !important; border: none !important; box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput input {
  background: rgba(7,30,56,.9) !important;
  border: 1px solid var(--border) !important;
  color: var(--cyan) !important; border-radius: 6px !important;
  font-family: 'Orbitron', monospace !important;
  font-size: 13px !important; letter-spacing: 2px !important;
  padding: 12px 16px !important;
}
.stTextInput input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 1px rgba(0,212,255,.4), 0 0 20px rgba(0,212,255,.15) !important;
}
.stTextInput input::placeholder { color: #1a3a5a !important; }
.stTextInput label, .stSelectbox label {
  color: var(--muted) !important; font-family: 'Orbitron', monospace !important;
  font-size: 8px !important; letter-spacing: 3px !important;
}
[data-baseweb="select"] > div {
  background: var(--bg2) !important; border-color: var(--border) !important;
  color: var(--cyan) !important; font-family: 'Orbitron', monospace !important;
}

/* ── Botones ── */
.stButton > button {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; font-family: 'Orbitron', monospace !important;
  font-size: 9px !important; letter-spacing: 2px !important;
  border-radius: 4px !important; transition: all .2s !important;
  text-transform: uppercase !important;
}
.stButton > button:hover {
  border-color: var(--cyan) !important; color: var(--cyan) !important;
  background: rgba(0,212,255,.05) !important;
  box-shadow: 0 0 14px rgba(0,212,255,.2) !important;
}
div[data-testid="column"] .stButton > button { width: 100%; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg1) !important; border-bottom: 1px solid var(--border) !important;
  padding: 0 16px !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: var(--muted) !important;
  font-family: 'Orbitron', monospace !important; font-size: 9px !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
  border-bottom: 2px solid transparent !important; padding: 16px 18px !important;
  border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
  color: var(--cyan) !important; border-bottom: 2px solid var(--cyan) !important;
  text-shadow: 0 0 12px rgba(0,212,255,.5) !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 20px 8px !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #0d2a4a; border-radius: 2px; }

.sit-card {
  background: var(--bg1); border: 1px solid var(--border);
  border-radius: 8px; padding: 18px 20px;
  position: relative; overflow: hidden; animation: fadeIn .4s ease;
}
.sit-card::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg,transparent,var(--cyan),transparent); opacity: .3;
}

/* ── Media queries ── */
@media (max-width: 1200px) {
  [data-testid="stSidebar"] { min-width: 180px !important; max-width: 180px !important; }
  .stTabs [data-baseweb="tab-panel"] { padding: 14px 4px !important; }
}
@media (max-width: 900px) {
  [data-testid="stSidebar"] { display: none !important; }
  .block-container { padding: 0 6px !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def api_get(p):
    try: return requests.get(f"{API}{p}", timeout=TIMEOUT).json()
    except: return {}

def api_post(p, b):
    try: return requests.post(f"{API}{p}", json=b, timeout=TIMEOUT).json()
    except Exception as e: return {"ok":False,"error":str(e)}

def api_patch(p, b):
    try: requests.patch(f"{API}{p}", json=b, timeout=TIMEOUT); st.cache_data.clear()
    except: pass

def api_delete(p, b=None):
    try: return requests.delete(f"{API}{p}", json=b or {}, timeout=TIMEOUT).json()
    except Exception as e: return {"ok":False,"error":str(e)}

@st.cache_data(ttl=2)
def fetch_stats():      return api_get("/turns/stats").get("data",{})
@st.cache_data(ttl=2)
def fetch_turns():      return api_get("/turns").get("data",[])
@st.cache_data(ttl=2)
def fetch_detections(): return api_get("/detect/recent").get("data",[])
@st.cache_data(ttl=3)
def fetch_vehicles():   return api_get("/vehicles").get("data",[])

def check_api():
    try: return requests.get(f"{API}/health",timeout=2).json().get("ok",False)
    except: return False

STATUS = {
    "waiting":   ("#ffb800","⬡ EN ESPERA"),
    "attending": ("#00ff88","▶ ATENDIENDO"),
    "done":      ("#3a6080","✓ FINALIZADO"),
    "cancelled": ("#ff3355","✕ CANCELADO"),
}

for k,v in [("logged_in",False),("usuario",""),("pagina","dashboard"),("login_error",False)]:
    if k not in st.session_state: st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    st.markdown("""
    <style>
    html,body,.stApp{height:100%!important;}
    .block-container{
      display:flex!important;align-items:center!important;
      justify-content:center!important;min-height:100vh!important;
      padding:20px!important;
    }
    section.main>div{
      width:100%!important;max-width:440px!important;margin:0 auto!important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:32px;animation:loginIn .6s ease;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:76px;height:76px;border-radius:18px;
                  border:1px solid rgba(0,212,255,.2);
                  background:rgba(0,212,255,.04);margin-bottom:16px;
                  animation:pulse-cyan 3s ease-in-out infinite;">
        <span style="font-size:38px;">🛰</span>
      </div>
      <div style="font-family:'Orbitron',monospace;font-size:clamp(22px,4vw,30px);
                  font-weight:900;color:#fff;letter-spacing:clamp(4px,1vw,8px);
                  text-shadow:0 0 28px rgba(0,212,255,.5);">
        SIT<span style="color:#00d4ff;">·</span>RFID</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:11px;
                  color:#2a4a6a;letter-spacing:4px;margin-top:6px;text-transform:uppercase;">
        Sistema Inteligente de Turnos</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#041428;border:1px solid #0d3355;border-radius:14px;
                padding:clamp(24px,4vw,36px) clamp(20px,5vw,40px);
                box-shadow:0 30px 80px rgba(0,0,0,.7),0 0 0 1px rgba(0,212,255,.05);
                animation:loginIn .7s ease .1s both;">
      <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;
                  letter-spacing:4px;text-transform:uppercase;margin-bottom:26px;
                  display:flex;align-items:center;gap:10px;">
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,#0d3355);"></div>
        ACCESO AL SISTEMA
        <div style="flex:1;height:1px;background:linear-gradient(90deg,#0d3355,transparent);"></div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:5px;font-family:Orbitron,monospace;font-size:8px;color:#2a4a6a;letter-spacing:3px;">USUARIO</div>', unsafe_allow_html=True)
    usuario_in = st.text_input("u", placeholder="correo o usuario", label_visibility="collapsed", key="li_u")

    st.markdown('<div style="margin:14px 0 5px;font-family:Orbitron,monospace;font-size:8px;color:#2a4a6a;letter-spacing:3px;">CONTRASEÑA</div>', unsafe_allow_html=True)
    password_in = st.text_input("p", type="password", placeholder="········", label_visibility="collapsed", key="li_p")

    if st.session_state.login_error:
        st.markdown("""
        <div style="background:rgba(255,51,85,.08);border:1px solid rgba(255,51,85,.3);
                    border-radius:6px;padding:10px 14px;margin-top:12px;
                    font-family:'Orbitron',monospace;font-size:9px;color:#ff3355;letter-spacing:2px;">
          ⚠ CREDENCIALES INCORRECTAS</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    if st.button("⟶  INGRESAR AL SISTEMA", use_container_width=True, key="btn_login"):
        if usuario_in in USUARIOS and USUARIOS[usuario_in] == password_in:
            st.session_state.logged_in   = True
            st.session_state.usuario     = usuario_in
            st.session_state.login_error = False
            st.rerun()
        else:
            st.session_state.login_error = True
            st.rerun()

    st.markdown("""</div>
    <div style="text-align:center;margin-top:20px;font-family:'Orbitron',monospace;
                font-size:8px;color:#0d2a4a;letter-spacing:2px;">
      ACCESO RESTRINGIDO · SOLO PERSONAL AUTORIZADO</div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:26px 18px 20px;border-bottom:1px solid #081830;">
      <div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;
                  color:#a78bfa;letter-spacing:4px;">SITRFID</div>
      <div style="font-size:9px;color:#3b2a7a;letter-spacing:3px;
                  text-transform:uppercase;margin-top:4px;">Panel de control</div>
    </div>
    <div style="padding:14px 12px 0;">
      <div style="font-size:9px;color:#2a1f5a;letter-spacing:2px;
                  text-transform:uppercase;padding:0 6px;margin-bottom:4px;">Principal</div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("dashboard",   "📊", "Dashboard"),
        ("turnos",      "🚦", "Turnos"),
        ("detecciones", "📡", "Detecciones"),
        ("vehiculos",   "🚗", "Vehículos"),
        ("registrar",   "➕", "Registrar"),
    ]

    for key, icon, label in nav_items:
        if key == "turnos":
            st.markdown("""<div style="padding:10px 12px 0;">
              <div style="font-size:9px;color:#2a1f5a;letter-spacing:2px;
                          text-transform:uppercase;padding:0 6px;margin-bottom:4px;">Gestión</div>
            </div>""", unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"btn_{key}"):
            st.session_state.pagina = key; st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    usr = st.session_state.usuario
    if len(usr) > 24: usr = usr[:21]+"..."
    st.markdown(f"""
    <div style="padding:14px 16px;border-top:1px solid #081830;">
      <div style="font-family:'Exo 2',sans-serif;">
        <div style="color:#9980d4;font-weight:600;font-size:12px;margin-bottom:2px;">Administrador</div>
        <div style="color:#4a3f6b;font-size:10px;">{usr}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("🔓  Cerrar sesión", key="logout"):
        for k in ["logged_in","usuario","pagina","login_error"]:
            st.session_state[k] = False if k=="logged_in" else ("dashboard" if k=="pagina" else "")
        st.cache_data.clear(); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DATOS COMUNES
# ══════════════════════════════════════════════════════════════════════════════
api_ok    = check_api()
stats     = fetch_stats() or {}
total     = int(stats.get("total",0) or 0)
waiting   = int(stats.get("waiting",0) or 0)
attending = int(stats.get("attending",0) or 0)
done      = int(stats.get("done",0) or 0)
sc  = "#00ff88" if api_ok else "#ff3355"
sl  = "SISTEMA EN LÍNEA" if api_ok else "SISTEMA FUERA DE LÍNEA"
pag = st.session_state.pagina

TITULOS = {
    "dashboard":   ("Dashboard",   "Resumen del sistema en tiempo real"),
    "turnos":      ("Turnos",      "Cola de atención del día"),
    "detecciones": ("Detecciones", "Lecturas OCR en tiempo real"),
    "vehiculos":   ("Vehículos",   "Unidades registradas en el sistema"),
    "registrar":   ("Registrar",   "Alta manual de nueva unidad"),
}
titulo, subtitulo = TITULOS.get(pag,("Dashboard",""))


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:#041428;border-bottom:1px solid #0d3355;
            padding:0 20px;display:flex;align-items:center;
            justify-content:space-between;height:64px;
            box-shadow:0 4px 40px rgba(0,0,0,.5);overflow:hidden;">
  <div style="display:flex;align-items:center;gap:14px;min-width:0;">
    <div style="width:40px;height:40px;border-radius:10px;flex-shrink:0;
                border:1px solid rgba(0,212,255,.2);
                display:flex;align-items:center;justify-content:center;
                background:rgba(0,212,255,.04);animation:pulse-cyan 3s ease-in-out infinite;">
      <span style="font-size:20px;">🛰</span></div>
    <div style="min-width:0;">
      <div style="font-family:'Exo 2',sans-serif;font-size:clamp(14px,2vw,17px);
                  font-weight:600;color:#f0ebff;white-space:nowrap;">{titulo}</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:11px;
                  color:#2a4a6a;white-space:nowrap;">{subtitulo}</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:clamp(12px,2vw,32px);flex-shrink:0;">
    <div style="display:flex;align-items:center;gap:7px;">
      <div style="width:7px;height:7px;border-radius:50%;background:{sc};
                  box-shadow:0 0 7px {sc};animation:pulse-dot 1.5s ease-in-out infinite;"></div>
      <span style="font-family:'Orbitron',monospace;font-size:8px;
                   color:{sc};letter-spacing:1px;white-space:nowrap;">{sl}</span>
    </div>
    <div style="border-left:1px solid #0d3355;padding-left:clamp(12px,2vw,24px);text-align:right;">
      <div id="sit-clock"
           style="font-family:'Orbitron',monospace;font-size:clamp(18px,2.5vw,26px);
                  font-weight:700;color:#ffb800;letter-spacing:3px;
                  text-shadow:0 0 12px rgba(255,184,0,.4);">--:--:--</div>
      <div id="sit-date" style="font-family:'Rajdhani',sans-serif;font-size:9px;
                                 color:#2a4a6a;letter-spacing:1px;margin-top:1px;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STATS — 2 filas de 2 en móvil, 4 en escritorio via columnas de Streamlit
# ══════════════════════════════════════════════════════════════════════════════
def stat_card(val, label, color, anim):
    bar = min(int(val)*12, 100)
    return f"""
    <div style="background:#041428;border:1px solid {color}1a;
                border-left:3px solid {color};border-radius:8px;
                padding:18px 18px;height:100%;
                {'animation:'+anim+' 2.5s ease-in-out infinite;' if anim else ''}">
      <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;
                  letter-spacing:2px;margin-bottom:10px;text-transform:uppercase;">{label}</div>
      <div style="font-family:'Orbitron',monospace;
                  font-size:clamp(32px,5vw,52px);font-weight:900;
                  color:{color};line-height:1;text-shadow:0 0 16px {color}44;">
        {str(val).zfill(2)}</div>
      <div style="margin-top:10px;height:2px;background:#0a2848;border-radius:1px;">
        <div style="height:100%;width:{bar}%;background:{color};border-radius:1px;opacity:.7;"></div>
      </div>
    </div>"""

if pag in ("dashboard","turnos"):
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(stat_card(total,     "TOTAL HOY",   "#a8d4f0", ""),            unsafe_allow_html=True)
    s2.markdown(stat_card(waiting,   "EN ESPERA",   "#ffb800", "pulse-amber"),  unsafe_allow_html=True)
    s3.markdown(stat_card(attending, "ATENDIENDO",  "#00ff88", "pulse-green"),  unsafe_allow_html=True)
    s4.markdown(stat_card(done,      "FINALIZADOS", "#00d4ff", "pulse-cyan"),   unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════════════════════

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if pag == "dashboard":
    col_t, col_d = st.columns([1, 1])

    with col_t:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:8px;
                    color:#2a4a6a;letter-spacing:3px;margin-bottom:10px;">TURNOS RECIENTES</div>""",
                    unsafe_allow_html=True)
        turns = fetch_turns()
        if not turns:
            st.markdown("""<div class="sit-card" style="text-align:center;padding:40px;">
              <div style="font-family:'Orbitron',monospace;font-size:9px;
                          color:#2a4a6a;letter-spacing:3px;">SIN TURNOS HOY</div></div>""",
                        unsafe_allow_html=True)
        else:
            for t in turns[:5]:
                color, lbl = STATUS.get(t["status"],("#fff","—"))
                hora  = str(t["created_at"])[11:16]
                ptype = (t.get("plate_type") or "—").upper()
                num   = str(t["turn_number"]).zfill(2)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                            margin-bottom:5px;background:#041428;border-radius:7px;
                            border:1px solid #0d3355;border-left:3px solid {color};
                            animation:fadeIn .3s ease;overflow:hidden;">
                  <div style="font-family:'Orbitron',monospace;font-size:clamp(16px,2vw,22px);
                              font-weight:900;color:{color};min-width:36px;flex-shrink:0;">{num}</div>
                  <div style="flex:1;min-width:0;">
                    <div style="font-family:'Orbitron',monospace;font-size:clamp(12px,1.5vw,15px);
                                font-weight:700;letter-spacing:2px;color:#e8f4ff;
                                white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{t['plate']}</div>
                    <div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:#2a4a6a;margin-top:1px;">
                      {ptype} · {hora}</div>
                  </div>
                  <span style="padding:3px 10px;border-radius:4px;font-size:8px;flex-shrink:0;
                               font-family:'Orbitron',monospace;letter-spacing:1px;
                               color:{color};border:1px solid {color}33;background:{color}0d;
                               white-space:nowrap;">{lbl}</span>
                </div>""", unsafe_allow_html=True)

    with col_d:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:8px;
                    color:#2a4a6a;letter-spacing:3px;margin-bottom:10px;">ÚLTIMAS DETECCIONES</div>""",
                    unsafe_allow_html=True)
        dets = fetch_detections()
        if not dets:
            st.markdown("""<div class="sit-card" style="text-align:center;padding:40px;">
              <div style="font-size:36px;margin-bottom:10px;opacity:.2;">📡</div>
              <div style="font-family:'Orbitron',monospace;font-size:9px;
                          color:#2a4a6a;letter-spacing:3px;">SIN LECTURAS</div></div>""",
                        unsafe_allow_html=True)
        else:
            for d in dets[:6]:
                is_k = bool(d.get("is_known"))
                col  = "#ff3355" if is_k else "#00ff88"
                badge= "EXISTENTE" if is_k else "NUEVA"
                hora = str(d.get("detected_at",""))[11:16]
                conf = d.get("confidence",0)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:11px 14px;
                            margin-bottom:4px;background:#041428;border-radius:6px;
                            border:1px solid #0d3355;border-left:2px solid {col}55;
                            overflow:hidden;">
                  <div style="width:6px;height:6px;border-radius:50%;background:{col};
                              box-shadow:0 0 5px {col};flex-shrink:0;"></div>
                  <span style="font-family:'Orbitron',monospace;font-size:clamp(11px,1.5vw,14px);
                               font-weight:700;letter-spacing:2px;flex:1;color:#d0e8ff;
                               white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{d['plate']}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;color:#00d4ff;flex-shrink:0;">{conf:.0f}%</span>
                  <span style="padding:2px 8px;border-radius:3px;font-size:7px;flex-shrink:0;
                               font-family:'Orbitron',monospace;color:{col};
                               border:1px solid {col}33;background:{col}0d;white-space:nowrap;">{badge}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;
                               color:#2a4a6a;flex-shrink:0;">{hora}</span>
                </div>""", unsafe_allow_html=True)


# ── TURNOS ────────────────────────────────────────────────────────────────────
elif pag == "turnos":
    turns = fetch_turns()
    if not turns:
        st.markdown("""<div style="text-align:center;padding:80px;">
          <div style="font-family:'Orbitron',monospace;font-size:9px;
                      color:#2a4a6a;letter-spacing:4px;">SIN TURNOS ACTIVOS</div></div>""",
                    unsafe_allow_html=True)
    else:
        for t in turns:
            color, lbl = STATUS.get(t["status"],("#fff","—"))
            hora  = str(t["created_at"])[11:16]
            score = f"{t['score']:.0f}%" if t.get("score") else "—"
            ptype = (t.get("plate_type") or "—").upper()
            num   = str(t["turn_number"]).zfill(2)
            active = t["status"] in ("waiting","attending")

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:14px 16px;
                        margin-bottom:5px;background:#041428;border-radius:6px;
                        border:1px solid {'rgba(0,212,255,.1)' if active else '#0d3355'};
                        border-left:3px solid {color};overflow:hidden;">
              <div style="font-family:'Orbitron',monospace;font-size:clamp(16px,2vw,22px);
                          font-weight:900;color:{color};min-width:36px;flex-shrink:0;">{num}</div>
              <div style="flex:1;min-width:0;">
                <div style="font-family:'Orbitron',monospace;font-size:clamp(12px,1.5vw,15px);
                            font-weight:700;letter-spacing:2px;color:#e8f4ff;">{t['plate']}</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:#2a4a6a;margin-top:1px;">
                  {ptype} · {hora} · OCR: {score}</div>
              </div>
              <span style="padding:4px 12px;border-radius:4px;font-size:8px;flex-shrink:0;
                           font-family:'Orbitron',monospace;letter-spacing:1px;
                           color:{color};border:1px solid {color}33;background:{color}0d;">{lbl}</span>
            </div>""", unsafe_allow_html=True)

            _, ca, cd, cc, __ = st.columns([.3,1,1,1,2])
            if t["status"]=="waiting":
                with ca:
                    if st.button("▶ ATENDER",  key=f"a{t['id']}"): api_patch(f"/turns/{t['id']}/status",{"status":"attending"}); st.rerun()
            if t["status"]=="attending":
                with cd:
                    if st.button("✓ FINALIZAR",key=f"d{t['id']}"): api_patch(f"/turns/{t['id']}/status",{"status":"done"}); st.rerun()
            if active:
                with cc:
                    if st.button("✕ CANCELAR", key=f"c{t['id']}"): api_patch(f"/turns/{t['id']}/status",{"status":"cancelled"}); st.rerun()


# ── DETECCIONES ───────────────────────────────────────────────────────────────
elif pag == "detecciones":
    dets = fetch_detections()
    col_l, col_r = st.columns([1, 1.4])

    with col_l:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
          <div style="width:7px;height:7px;border-radius:50%;background:#ff3355;
                      animation:pulse-dot 1s ease-in-out infinite;box-shadow:0 0 7px #ff3355;"></div>
          <span style="font-family:'Orbitron',monospace;font-size:8px;
                       color:#2a4a6a;letter-spacing:3px;">LIVE — ÚLTIMA DETECCIÓN</span>
        </div>""", unsafe_allow_html=True)

        if not dets:
            st.markdown("""<div class="sit-card" style="padding:50px 20px;text-align:center;">
              <div style="font-size:40px;margin-bottom:12px;opacity:.2;">📡</div>
              <div style="font-family:'Orbitron',monospace;font-size:9px;
                          color:#2a4a6a;letter-spacing:4px;">ESPERANDO SEÑAL...</div></div>""",
                        unsafe_allow_html=True)
        else:
            d = dets[0]; is_k=bool(d.get("is_known"))
            ac="#ff3355" if is_k else "#00ff88"
            msg="⚠ VEHÍCULO REGISTRADO" if is_k else "✓ TURNO ASIGNADO"
            conf=d.get("confidence",0); hora=str(d.get("detected_at",""))[11:19]
            st.markdown(f"""
            <div class="sit-card" style="border-color:{ac}22;border-left:3px solid {ac};padding:22px;">
              <div style="background:#fff;border-radius:10px;padding:16px 24px;
                          text-align:center;margin-bottom:18px;
                          box-shadow:0 0 40px {ac}1a,0 6px 24px rgba(0,0,0,.4);">
                <div style="font-size:8px;font-weight:700;letter-spacing:4px;
                            color:#1a3a6a;margin-bottom:4px;">🇨🇴  C O L O M B I A</div>
                <div style="font-family:'Orbitron',monospace;
                            font-size:clamp(28px,4vw,44px);font-weight:900;
                            color:#050c1a;letter-spacing:clamp(3px,0.8vw,7px);">{d['plate']}</div>
              </div>
              <div style="text-align:center;margin-bottom:18px;">
                <span style="padding:6px 18px;border-radius:4px;
                             font-family:'Orbitron',monospace;font-size:9px;letter-spacing:2px;
                             color:{ac};border:1px solid {ac}44;background:{ac}0d;font-weight:700;">{msg}</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:#020c18;border-radius:6px;padding:12px;border:1px solid #0d3355;">
                  <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;
                              letter-spacing:2px;margin-bottom:5px;">CONFIANZA OCR</div>
                  <div style="font-family:'Orbitron',monospace;font-size:clamp(20px,3vw,28px);
                              font-weight:700;color:#00d4ff;">{conf:.0f}%</div>
                </div>
                <div style="background:#020c18;border-radius:6px;padding:12px;border:1px solid #0d3355;">
                  <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;
                              letter-spacing:2px;margin-bottom:5px;">HORA</div>
                  <div style="font-family:'Orbitron',monospace;font-size:clamp(20px,3vw,28px);
                              font-weight:700;color:#ffb800;">{hora[:5]}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:8px;
                    color:#2a4a6a;letter-spacing:3px;margin-bottom:10px;">HISTORIAL</div>""",
                    unsafe_allow_html=True)
        if not dets:
            st.markdown("<div style='color:#2a4a6a;font-family:Orbitron,monospace;font-size:9px;'>Sin registros</div>", unsafe_allow_html=True)
        else:
            for d in dets:
                is_k=bool(d.get("is_known")); col="#ff3355" if is_k else "#00ff88"
                badge="EXISTENTE" if is_k else "NUEVA"
                hora=str(d.get("detected_at",""))[11:16]; conf=d.get("confidence",0)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:11px 14px;
                            margin-bottom:4px;background:#041428;border-radius:6px;
                            border:1px solid #0d3355;border-left:2px solid {col}44;overflow:hidden;">
                  <div style="width:6px;height:6px;border-radius:50%;background:{col};
                              box-shadow:0 0 5px {col};flex-shrink:0;"></div>
                  <span style="font-family:'Orbitron',monospace;font-size:clamp(11px,1.5vw,14px);
                               font-weight:700;letter-spacing:2px;flex:1;color:#d0e8ff;
                               white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{d['plate']}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;color:#00d4ff;flex-shrink:0;">{conf:.0f}%</span>
                  <span style="padding:2px 8px;border-radius:3px;font-size:7px;flex-shrink:0;
                               font-family:'Orbitron',monospace;color:{col};
                               border:1px solid {col}33;background:{col}0d;">{badge}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;color:#2a4a6a;flex-shrink:0;">{hora}</span>
                </div>""", unsafe_allow_html=True)


# ── VEHÍCULOS ─────────────────────────────────────────────────────────────────
elif pag == "vehiculos":
    vehs   = fetch_vehicles()
    search = st.text_input("🔍 Buscar placa", placeholder="Ej: ABC123", label_visibility="collapsed")
    filtered = [v for v in vehs if not search or search.upper() in v["plate"]]
    st.markdown(f"""<div style="font-family:'Orbitron',monospace;font-size:8px;
                letter-spacing:2px;color:#2a4a6a;margin:6px 0 14px;">
                {len(filtered)} UNIDADES REGISTRADAS</div>""", unsafe_allow_html=True)

    if not filtered:
        st.markdown("<div style='text-align:center;padding:60px;font-family:Orbitron,monospace;font-size:9px;color:#2a4a6a;'>SIN VEHÍCULOS</div>", unsafe_allow_html=True)
    else:
        for v in filtered:
            active=bool(v.get("active",1)); hx="#00ff88" if active else "#2a4a6a"
            est="ACTIVO" if active else "INACTIVO"
            turns=v.get("total_turns",0); owner=v.get("owner_name") or "Sin propietario"
            doc=v.get("owner_doc") or "—"; fecha=str(v.get("created_at",""))[:10]
            ptype=(v.get("plate_type") or "—").upper()
            st.markdown(f"""
            <div class="sit-card" style="border-left:3px solid {hx};padding:14px 18px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;align-items:center;
                          margin-bottom:7px;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:baseline;gap:12px;min-width:0;">
                  <span style="font-family:'Orbitron',monospace;font-size:clamp(14px,2vw,20px);
                               font-weight:900;letter-spacing:3px;color:#e8f4ff;">{v['plate']}</span>
                  <span style="font-family:'Rajdhani',sans-serif;font-size:11px;color:#2a4a6a;">{ptype}</span>
                </div>
                <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
                  <span style="font-family:'Orbitron',monospace;font-size:8px;color:{hx};">● {est}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:9px;color:#00d4ff;">◈ {turns} turno{'s' if turns!=1 else ''}</span>
                  <span style="font-family:'Rajdhani',sans-serif;font-size:11px;color:#2a4a6a;">{fecha}</span>
                </div>
              </div>
              <div style="display:flex;gap:18px;font-family:'Rajdhani',sans-serif;font-size:12px;color:#2a4a6a;flex-wrap:wrap;">
                <span>👤 {owner}</span><span>🪪 {doc}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            cp,cb,_ = st.columns([1,1,3])
            with cp: pin_v=st.text_input("PIN",type="password",key=f"pin_{v['plate']}",placeholder="PIN admin",label_visibility="collapsed")
            with cb:
                if st.button("✕ ELIMINAR",key=f"del_{v['plate']}"):
                    if pin_v==PIN:
                        res=api_delete(f"/vehicles/{v['plate']}/force",{"pin":pin_v})
                        if res.get("ok"): st.success(f"✓ {v['plate']} eliminado."); st.cache_data.clear(); st.rerun()
                        else: st.error(f"Error: {res.get('error','desconocido')}")
                    else: st.error("PIN incorrecto.")


# ── REGISTRAR ─────────────────────────────────────────────────────────────────
elif pag == "registrar":
    col_f, col_p = st.columns([1, 1])
    with col_f:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:8px;
                    color:#2a4a6a;letter-spacing:3px;margin-bottom:22px;">
                    ▸ REGISTRO MANUAL DE UNIDAD</div>""", unsafe_allow_html=True)
        plate_in=st.text_input("Matrícula *",placeholder="Ej: ABC123",max_chars=7).upper().replace(" ","")
        ptype_in=st.selectbox("Clasificación",["particular","moto","diplomatica"])
        oname_in=st.text_input("Propietario",placeholder="Opcional")
        odoc_in =st.text_input("Documento",  placeholder="Opcional")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("＋  REGISTRAR UNIDAD",use_container_width=True):
            if not plate_in: st.error("La matrícula es obligatoria.")
            else:
                res=api_post("/vehicles",{"plate":plate_in,"plate_type":ptype_in,"owner_name":oname_in or None,"owner_doc":odoc_in or None})
                if res.get("ok"): st.success(f"✓ {res.get('message','Unidad registrada.')}"); st.cache_data.clear()
                elif res.get("error")=="PLATE_EXISTS": st.warning(f"La matrícula {plate_in} ya existe.")
                else: st.error(f"Error: {res.get('error','desconocido')}")

    with col_p:
        preview=plate_in if plate_in else "ABC·123"
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:32px 16px;gap:20px;">
          <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;letter-spacing:3px;">PREVISUALIZACIÓN</div>
          <div style="background:#fff;border-radius:12px;padding:16px clamp(16px,4vw,36px);
                      text-align:center;width:100%;max-width:280px;
                      box-shadow:0 0 50px rgba(0,255,136,.12),0 6px 30px rgba(0,0,0,.4);
                      border:2px solid rgba(0,255,136,.2);">
            <div style="font-size:8px;font-weight:700;letter-spacing:4px;color:#1a3a6a;margin-bottom:4px;">🇨🇴  C O L O M B I A</div>
            <div style="font-family:'Orbitron',monospace;font-size:clamp(24px,4vw,42px);
                        font-weight:900;color:#050c1a;letter-spacing:clamp(3px,0.8vw,6px);">{preview}</div>
          </div>
          <div style="font-family:'Orbitron',monospace;font-size:8px;color:#2a4a6a;letter-spacing:2px;">{ptype_in.upper()}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RELOJ + AUTO-REFRESH
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<script>
const D=['DOMINGO','LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO'];
const M=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'];
function clk(){
  const n=new Date(new Date().toLocaleString("en-US",{timeZone:"America/Bogota"}));
  const cl=document.getElementById('sit-clock'),dt=document.getElementById('sit-date');
  if(cl)cl.textContent=[n.getHours(),n.getMinutes(),n.getSeconds()].map(x=>String(x).padStart(2,'0')).join(':');
  if(dt)dt.textContent=D[n.getDay()]+' '+String(n.getDate()).padStart(2,'0')+' '+M[n.getMonth()]+' '+n.getFullYear();
}
clk(); setInterval(clk,1000); setTimeout(()=>location.reload(),30000);
</script>
""", unsafe_allow_html=True)