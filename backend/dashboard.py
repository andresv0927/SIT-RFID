"""
dashboard.py — SIT-RFID | Centro de Control Inteligente
"""
import streamlit as st
import requests
from datetime import datetime
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
  --bg0: #020c18;
  --bg1: #041428;
  --bg2: #071e38;
  --bg3: #0a2848;
  --cyan: #00d4ff;
  --amber: #ffb800;
  --green: #00ff88;
  --red: #ff3355;
  --text: #a8d4f0;
  --muted: #2a4a6a;
  --border: #0d3355;
}

@keyframes pulse-cyan {
  0%,100% { box-shadow: 0 0 8px var(--cyan), 0 0 20px rgba(0,212,255,.15); }
  50%      { box-shadow: 0 0 16px var(--cyan), 0 0 40px rgba(0,212,255,.35); }
}
@keyframes pulse-green {
  0%,100% { box-shadow: 0 0 8px var(--green), 0 0 20px rgba(0,255,136,.15); }
  50%      { box-shadow: 0 0 16px var(--green), 0 0 40px rgba(0,255,136,.35); }
}
@keyframes pulse-amber {
  0%,100% { box-shadow: 0 0 8px var(--amber), 0 0 20px rgba(255,184,0,.15); }
  50%      { box-shadow: 0 0 16px var(--amber), 0 0 40px rgba(255,184,0,.35); }
}
@keyframes pulse-dot {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:.4; transform:scale(.7); }
}
@keyframes fadeIn {
  from { opacity:0; transform:translateY(6px); }
  to   { opacity:1; transform:translateY(0); }
}

html,body,.stApp {
  background: var(--bg0) !important;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,100,200,.25) 0%, transparent 70%),
    linear-gradient(180deg, rgba(0,40,80,.4) 0%, transparent 40%) !important;
  color: var(--text);
  font-family: 'Rajdhani', sans-serif;
}

#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;}
.block-container{padding:0!important;max-width:100%!important;}
section.main>div{padding:0!important;}

.stTabs [data-baseweb="tab-list"]{
  background:var(--bg1)!important;border-bottom:1px solid var(--border)!important;
  padding:0 32px!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{
  background:transparent!important;color:var(--muted)!important;
  font-family:'Orbitron',monospace!important;font-size:9px!important;
  letter-spacing:3px!important;text-transform:uppercase!important;
  border-bottom:2px solid transparent!important;padding:18px 28px!important;
  border-radius:0!important;transition:color .2s!important;}
.stTabs [aria-selected="true"]{
  color:var(--cyan)!important;border-bottom:2px solid var(--cyan)!important;
  text-shadow:0 0 12px rgba(0,212,255,.6)!important;}
.stTabs [data-baseweb="tab-panel"]{
  background:transparent!important;padding:28px 32px!important;}

.stTextInput input{
  background:var(--bg2)!important;border:1px solid var(--border)!important;
  color:var(--cyan)!important;border-radius:4px!important;
  font-family:'Orbitron',monospace!important;font-size:12px!important;
  letter-spacing:2px!important;}
.stTextInput input:focus{
  border-color:var(--cyan)!important;
  box-shadow:0 0 0 1px var(--cyan),0 0 12px rgba(0,212,255,.2)!important;}
.stTextInput input::placeholder{color:var(--muted)!important;}
.stTextInput label,.stSelectbox label{
  color:var(--muted)!important;font-family:'Orbitron',monospace!important;
  font-size:8px!important;letter-spacing:3px!important;}
[data-baseweb="select"]>div{
  background:var(--bg2)!important;border-color:var(--border)!important;
  color:var(--cyan)!important;font-family:'Orbitron',monospace!important;
  font-size:10px!important;}

.stButton>button{
  background:var(--bg2)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;font-family:'Orbitron',monospace!important;
  font-size:8px!important;letter-spacing:2px!important;border-radius:3px!important;
  transition:all .2s!important;text-transform:uppercase!important;}
.stButton>button:hover{
  border-color:var(--cyan)!important;color:var(--cyan)!important;
  background:rgba(0,212,255,.06)!important;
  box-shadow:0 0 12px rgba(0,212,255,.2)!important;}

::-webkit-scrollbar{width:3px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
div[data-testid="column"] .stButton>button{width:100%;}

.sit-card{
  background:var(--bg1);border:1px solid var(--border);border-radius:6px;
  padding:20px 24px;position:relative;overflow:hidden;animation:fadeIn .4s ease;}
.sit-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.4;}

.stat-cyan  {animation:pulse-cyan  2s ease-in-out infinite;}
.stat-green {animation:pulse-green 2s ease-in-out infinite;}
.stat-amber {animation:pulse-amber 2s ease-in-out infinite;}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────
def api_get(p):
    try: return requests.get(f"{API}{p}", timeout=TIMEOUT).json()
    except: return {}

def api_post(p, b):
    try: return requests.post(f"{API}{p}", json=b, timeout=TIMEOUT).json()
    except Exception as e: return {"ok":False,"error":str(e)}

def api_patch(p, b):
    try:
        requests.patch(f"{API}{p}", json=b, timeout=TIMEOUT)
        st.cache_data.clear()
    except: pass

def api_delete(p, b=None):
    try: return requests.delete(f"{API}{p}", json=b or {}, timeout=TIMEOUT).json()
    except Exception as e: return {"ok":False,"error":str(e)}

@st.cache_data(ttl=2)
def fetch_stats():      return api_get("/turns/stats").get("data", {})
@st.cache_data(ttl=2)
def fetch_turns():      return api_get("/turns").get("data", [])
@st.cache_data(ttl=2)
def fetch_detections(): return api_get("/detect/recent").get("data", [])
@st.cache_data(ttl=3)
def fetch_vehicles():   return api_get("/vehicles").get("data", [])

def check_api():
    try: return requests.get(f"{API}/health", timeout=2).json().get("ok", False)
    except: return False

STATUS = {
    "waiting":   ("var(--amber)", "⬡ EN ESPERA"),
    "attending": ("var(--green)", "▶ ATENDIENDO"),
    "done":      ("#3a6080",      "✓ FINALIZADO"),
    "cancelled": ("var(--red)",   "✕ CANCELADO"),
}

# ── DATA ───────────────────────────────────────────────────────────────────────
api_ok    = check_api()
stats     = fetch_stats() or {}
total     = int(stats.get("total",0) or 0)
waiting   = int(stats.get("waiting",0) or 0)
attending = int(stats.get("attending",0) or 0)
done      = int(stats.get("done",0) or 0)
sc        = "var(--green)" if api_ok else "var(--red)"
sl        = "SISTEMA EN LÍNEA" if api_ok else "SISTEMA FUERA DE LÍNEA"

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:var(--bg1);border-bottom:1px solid var(--border);
            padding:0 32px;display:flex;align-items:center;
            justify-content:space-between;height:68px;
            box-shadow:0 4px 40px rgba(0,0,0,.6);">
  <div style="display:flex;align-items:center;gap:24px;">
    <div style="position:relative;width:48px;height:48px;
                border:1px solid rgba(0,212,255,.3);border-radius:6px;
                display:flex;align-items:center;justify-content:center;
                background:rgba(0,212,255,.05);">
      <span style="font-size:24px;">🛰</span>
      <div style="position:absolute;top:-1px;left:-1px;right:-1px;bottom:-1px;
                  border-radius:6px;border:1px solid var(--cyan);
                  animation:pulse-cyan 3s ease-in-out infinite;"></div>
    </div>
    <div>
      <div style="font-family:'Orbitron',monospace;font-size:22px;font-weight:900;
                  color:#fff;letter-spacing:6px;text-shadow:0 0 20px rgba(0,212,255,.5);">
        SIT<span style="color:var(--cyan);">·</span>RFID</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:11px;
                  color:var(--muted);letter-spacing:4px;margin-top:1px;">
        SISTEMA INTELIGENTE DE TURNOS</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:40px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:8px;height:8px;border-radius:50%;background:{sc};
                  animation:pulse-dot 1.5s ease-in-out infinite;"></div>
      <span style="font-family:'Orbitron',monospace;font-size:9px;
                   color:{sc};letter-spacing:2px;">{sl}</span>
    </div>
    <div style="border-left:1px solid var(--border);padding-left:32px;text-align:right;">
      <div id="sit-clock"
           style="font-family:'Orbitron',monospace;font-size:28px;font-weight:700;
                  color:var(--amber);letter-spacing:4px;
                  text-shadow:0 0 16px rgba(255,184,0,.4);">--:--:--</div>
      <div id="sit-date"
           style="font-family:'Rajdhani',sans-serif;font-size:10px;
                  color:var(--muted);letter-spacing:3px;margin-top:2px;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STATS ──────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:20px 32px 0;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;'>",
            unsafe_allow_html=True)

def stat(val, label, color, glow, icon):
    bar = min(val * 10, 100) if val else 0
    return f"""
    <div class="sit-card {glow}"
         style="border-color:{color}22;border-left:3px solid {color};padding:22px 26px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-family:'Orbitron',monospace;font-size:9px;color:var(--muted);
                      letter-spacing:3px;margin-bottom:14px;">{label}</div>
          <div style="font-family:'Orbitron',monospace;font-size:52px;font-weight:900;
                      color:{color};line-height:1;
                      text-shadow:0 0 20px {color}66;">{str(val).zfill(2)}</div>
        </div>
        <div style="font-size:28px;opacity:.4;margin-top:4px;">{icon}</div>
      </div>
      <div style="margin-top:14px;height:2px;background:var(--bg3);border-radius:1px;">
        <div style="height:100%;width:{bar}%;background:{color};
                    border-radius:1px;opacity:.7;"></div>
      </div>
    </div>"""

st.markdown(
    stat(total,     "TOTAL HOY",   "var(--text)",  "",             "") +
    stat(waiting,   "EN ESPERA",   "var(--amber)", "stat-amber",   "") +
    stat(attending, "ATENDIENDO",  "var(--green)", "stat-green",   "") +
    stat(done,      "FINALIZADOS", "var(--cyan)",  "stat-cyan",    ""),
    unsafe_allow_html=True
)
st.markdown("</div><div style='height:20px'></div>", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🚦  Cola de Turnos",
    "📡  Detecciones en Vivo",
    "🚗  Vehículos",
    "＋  Registrar",
])

# ── TAB 1 ──────────────────────────────────────────────────────────────────────
with tab1:
    turns = fetch_turns()
    if not turns:
        st.markdown("""
        <div style="text-align:center;padding:100px 20px;">
          <div style="font-family:'Orbitron',monospace;font-size:72px;font-weight:900;
                      color:var(--border);letter-spacing:-2px;margin-bottom:16px;">00</div>
          <div style="font-family:'Orbitron',monospace;font-size:10px;
                      color:var(--muted);letter-spacing:5px;">SIN TURNOS ACTIVOS</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:grid;grid-template-columns:64px 180px 120px 90px 70px 160px 1fr;
                    gap:8px;padding:10px 20px;margin-bottom:6px;
                    font-family:'Orbitron',monospace;font-size:8px;
                    letter-spacing:3px;color:var(--muted);
                    border-bottom:1px solid var(--border);">
          <div>#</div><div>PLACA</div><div>TIPO</div>
          <div>OCR</div><div>HORA</div><div>ESTADO</div><div>ACCIÓN</div>
        </div>""", unsafe_allow_html=True)

        for t in turns:
            color, lbl = STATUS.get(t["status"], ("#fff","—"))
            hora  = str(t["created_at"])[11:16]
            score = f"{t['score']:.0f}%" if t.get("score") else "—"
            ptype = (t.get("plate_type") or "—").upper()
            num   = str(t["turn_number"]).zfill(2)
            is_active = t["status"] in ("waiting","attending")

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:64px 180px 120px 90px 70px 160px 1fr;
                        gap:8px;padding:16px 20px;margin-bottom:4px;
                        background:var(--bg1);border-radius:5px;
                        border:1px solid {'rgba(0,212,255,.12)' if is_active else 'var(--border)'};
                        border-left:3px solid {color};align-items:center;
                        animation:fadeIn .3s ease;">
              <div style="font-family:'Orbitron',monospace;font-size:24px;font-weight:900;
                          color:{color};text-shadow:0 0 12px {color}88;">{num}</div>
              <div style="font-family:'Orbitron',monospace;font-size:17px;font-weight:700;
                          letter-spacing:3px;color:#fff;">{t['plate']}</div>
              <div style="font-family:'Rajdhani',sans-serif;font-size:12px;
                          color:var(--muted);letter-spacing:2px;">{ptype}</div>
              <div style="font-family:'Orbitron',monospace;font-size:13px;
                          color:var(--cyan);">{score}</div>
              <div style="font-family:'Orbitron',monospace;font-size:11px;
                          color:var(--muted);">{hora}</div>
              <div><span style="padding:5px 14px;border-radius:3px;font-size:8px;
                                font-family:'Orbitron',monospace;letter-spacing:2px;
                                color:{color};border:1px solid {color}44;
                                background:{color}11;">{lbl}</span></div>
            </div>""", unsafe_allow_html=True)

            _, ca, cd, cc, __ = st.columns([.3,1,1,1,2.5])
            if t["status"] == "waiting":
                with ca:
                    if st.button("▶ ATENDER", key=f"a{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"attending"})
                        st.rerun()
            if t["status"] == "attending":
                with cd:
                    if st.button("✓ FINALIZAR", key=f"d{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"done"})
                        st.rerun()
            if is_active:
                with cc:
                    if st.button("✕ CANCELAR", key=f"c{t['id']}"):
                        api_patch(f"/turns/{t['id']}/status", {"status":"cancelled"})
                        st.rerun()

# ── TAB 2 ──────────────────────────────────────────────────────────────────────
with tab2:
    detections = fetch_detections()
    col_l, col_r = st.columns([1, 1.5])

    with col_l:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
          <div style="width:8px;height:8px;border-radius:50%;background:var(--red);
                      animation:pulse-dot 1s ease-in-out infinite;"></div>
          <span style="font-family:'Orbitron',monospace;font-size:9px;
                       color:var(--muted);letter-spacing:3px;">LIVE — ÚLTIMA DETECCIÓN</span>
        </div>""", unsafe_allow_html=True)

        if not detections:
            st.markdown("""
            <div class="sit-card" style="padding:60px 20px;text-align:center;">
              <div style="font-size:48px;margin-bottom:16px;opacity:.3;">📡</div>
              <div style="font-family:'Orbitron',monospace;font-size:9px;
                          color:var(--muted);letter-spacing:4px;">ESPERANDO SEÑAL...</div>
            </div>""", unsafe_allow_html=True)
        else:
            d        = detections[0]
            is_known = bool(d.get("is_known"))
            accent   = "var(--red)" if is_known else "var(--green)"
            hex_ac   = "#ff3355" if is_known else "#00ff88"
            msg      = "⚠ VEHÍCULO REGISTRADO" if is_known else "✓ TURNO ASIGNADO"
            conf     = d.get("confidence", 0)
            hora     = str(d.get("detected_at",""))[11:19]

            st.markdown(f"""
            <div class="sit-card" style="border-color:{hex_ac}44;
                        border-left:3px solid {accent};padding:28px;">
              <div style="position:relative;background:#fff;border-radius:8px;
                          padding:20px 32px;text-align:center;margin-bottom:24px;
                          box-shadow:0 0 40px {hex_ac}33,0 0 80px {hex_ac}11;">
                <div style="font-size:8px;font-weight:700;letter-spacing:5px;
                            color:#1a3a6a;margin-bottom:6px;">🇨🇴  C O L O M B I A</div>
                <div style="font-family:'Orbitron',monospace;font-size:48px;
                            font-weight:900;color:#0a0a1a;letter-spacing:8px;
                            line-height:1;">{d['plate']}</div>
              </div>
              <div style="text-align:center;margin-bottom:24px;">
                <span style="display:inline-block;padding:8px 22px;border-radius:3px;
                             font-family:'Orbitron',monospace;font-size:10px;letter-spacing:2px;
                             color:{accent};border:1px solid {accent};
                             background:{hex_ac}11;font-weight:700;">{msg}</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div style="background:var(--bg0);border-radius:4px;padding:14px 16px;
                            border:1px solid var(--border);">
                  <div style="font-family:'Orbitron',monospace;font-size:8px;
                              color:var(--muted);letter-spacing:2px;margin-bottom:6px;">CONFIANZA OCR</div>
                  <div style="font-family:'Orbitron',monospace;font-size:30px;
                              font-weight:700;color:var(--cyan);">{conf:.0f}%</div>
                  <div style="margin-top:8px;height:3px;background:var(--bg3);border-radius:2px;">
                    <div style="height:100%;width:{conf:.0f}%;background:var(--cyan);border-radius:2px;"></div>
                  </div>
                </div>
                <div style="background:var(--bg0);border-radius:4px;padding:14px 16px;
                            border:1px solid var(--border);">
                  <div style="font-family:'Orbitron',monospace;font-size:8px;
                              color:var(--muted);letter-spacing:2px;margin-bottom:6px;">HORA DETECCIÓN</div>
                  <div style="font-family:'Orbitron',monospace;font-size:24px;
                              font-weight:700;color:var(--amber);">{hora[:5]}</div>
                  <div style="font-family:'Rajdhani',sans-serif;font-size:11px;
                              color:var(--muted);margin-top:6px;">{hora}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:8px;
                        color:var(--muted);letter-spacing:3px;margin-bottom:8px;">
                        ▸ BORRAR DETECCIÓN (REQUIERE PIN)</div>""",
                        unsafe_allow_html=True)
            pin_d = st.text_input("PIN", type="password", key="pin_det",
                                   placeholder="· · · ·", label_visibility="collapsed")
            if st.button("✕ ELIMINAR DETECCIÓN", key="del_det"):
                if pin_d == PIN:
                    res = api_delete(f"/detect/{d['id']}", {"pin": pin_d})
                    if res.get("ok"):
                        st.success("Detección eliminada.")
                        st.cache_data.clear(); st.rerun()
                    else:
                        st.error(f"Error: {res.get('error')}")
                else:
                    st.error("PIN incorrecto.")

    with col_r:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;
                    color:var(--muted);letter-spacing:3px;margin-bottom:16px;">
                    HISTORIAL RECIENTE</div>""", unsafe_allow_html=True)

        if not detections:
            st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;
                            color:var(--muted);letter-spacing:2px;">Sin registros</div>""",
                        unsafe_allow_html=True)
        else:
            for i, d in enumerate(detections):
                is_k  = bool(d.get("is_known"))
                col   = "#ff3355" if is_k else "#00ff88"
                badge = "REGISTRADA" if is_k else "NUEVA"
                hora  = str(d.get("detected_at",""))[11:16]
                conf  = d.get("confidence", 0)
                alpha = max(1 - i*0.08, 0.3)

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:14px;padding:13px 18px;
                            border-radius:4px;margin-bottom:4px;
                            background:rgba(4,20,40,{alpha});
                            border:1px solid rgba(13,51,85,{alpha});
                            border-left:2px solid {col}66;
                            animation:fadeIn .3s ease {i*0.05}s both;">
                  <div style="width:7px;height:7px;border-radius:50%;
                              background:{col};flex-shrink:0;
                              box-shadow:0 0 8px {col}88;"></div>
                  <span style="font-family:'Orbitron',monospace;font-size:16px;
                               font-weight:700;letter-spacing:4px;flex:1;color:#e0f0ff;">
                    {d['plate']}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:11px;
                               color:var(--cyan);">{conf:.0f}%</span>
                  <span style="padding:3px 10px;border-radius:2px;font-size:7px;
                               font-family:'Orbitron',monospace;letter-spacing:1px;
                               color:{col};border:1px solid {col}44;background:{col}11;">
                    {badge}</span>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;
                               color:var(--muted);min-width:42px;">{hora}</span>
                </div>""", unsafe_allow_html=True)

# ── TAB 3 ──────────────────────────────────────────────────────────────────────
with tab3:
    vehicles = fetch_vehicles()
    search   = st.text_input("Buscar placa", placeholder="Ej: ABC123",
                              label_visibility="collapsed")
    filtered = [v for v in vehicles if not search or search.upper() in v["plate"]]

    st.markdown(f"""<div style="font-family:'Orbitron',monospace;font-size:8px;
                letter-spacing:3px;color:var(--muted);margin:8px 0 20px;">
                {len(filtered)} UNIDADES REGISTRADAS</div>""",
                unsafe_allow_html=True)

    if not filtered:
        st.markdown("""<div style="text-align:center;padding:60px;
                    font-family:'Orbitron',monospace;font-size:9px;
                    color:var(--muted);letter-spacing:4px;">SIN VEHÍCULOS</div>""",
                    unsafe_allow_html=True)
    else:
        for v in filtered:
            active = bool(v.get("active", 1))
            accent = "var(--green)" if active else "var(--muted)"
            hex_ac = "#00ff88" if active else "#2a4a6a"
            estado = "ACTIVO" if active else "INACTIVO"
            turns  = v.get("total_turns", 0)
            owner  = v.get("owner_name") or "Sin propietario"
            doc    = v.get("owner_doc")  or "—"
            fecha  = str(v.get("created_at",""))[:10]
            ptype  = (v.get("plate_type") or "—").upper()

            st.markdown(f"""
            <div class="sit-card" style="border-left:3px solid {hex_ac};
                        margin-bottom:6px;padding:18px 24px;">
              <div style="display:flex;justify-content:space-between;
                          align-items:center;margin-bottom:12px;">
                <div style="display:flex;align-items:baseline;gap:20px;">
                  <span style="font-family:'Orbitron',monospace;font-size:24px;
                               font-weight:900;letter-spacing:5px;color:#fff;
                               text-shadow:0 0 16px rgba(255,255,255,.2);">{v['plate']}</span>
                  <span style="font-family:'Rajdhani',sans-serif;font-size:12px;
                               color:var(--muted);letter-spacing:3px;">{ptype}</span>
                </div>
                <div style="display:flex;align-items:center;gap:24px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:6px;height:6px;border-radius:50%;background:{hex_ac};
                                {'animation:pulse-dot 2s ease-in-out infinite;' if active else ''}"></div>
                    <span style="font-family:'Orbitron',monospace;font-size:8px;
                                 color:{accent};letter-spacing:2px;">{estado}</span>
                  </div>
                  <span style="font-family:'Orbitron',monospace;font-size:10px;
                               color:var(--cyan);">◈ {turns} turno{'s' if turns!=1 else ''}</span>
                  <span style="font-family:'Rajdhani',sans-serif;font-size:11px;
                               color:var(--muted);">{fecha}</span>
                </div>
              </div>
              <div style="display:flex;gap:28px;font-family:'Rajdhani',sans-serif;
                          font-size:13px;color:var(--muted);">
                <span>👤 {owner}</span>
                <span>🪪 {doc}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            cp, cb, _ = st.columns([1, 1, 4])
            with cp:
                pin_v = st.text_input("PIN", type="password",
                                      key=f"pin_{v['plate']}",
                                      placeholder="PIN admin",
                                      label_visibility="collapsed")
            with cb:
                if st.button("✕ ELIMINAR", key=f"del_{v['plate']}"):
                    if pin_v == PIN:
                        res = api_delete(f"/vehicles/{v['plate']}/force", {"pin": pin_v})
                        if res.get("ok"):
                            st.success(f"✓ {v['plate']} eliminado.")
                            st.cache_data.clear(); st.rerun()
                        else:
                            st.error(f"Error: {res.get('error','desconocido')}")
                    else:
                        st.error("PIN incorrecto.")

# ── TAB 4 ──────────────────────────────────────────────────────────────────────
with tab4:
    col_f, col_p = st.columns([1, 1])

    with col_f:
        st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;
                    color:var(--muted);letter-spacing:3px;margin-bottom:24px;">
                    ▸ REGISTRO MANUAL DE UNIDAD</div>""", unsafe_allow_html=True)

        plate_in = st.text_input("Matrícula *", placeholder="Ej: ABC123",
                                  max_chars=7).upper().replace(" ","")
        ptype_in = st.selectbox("Clasificación", ["particular","moto","diplomatica"])
        oname_in = st.text_input("Propietario", placeholder="Opcional")
        odoc_in  = st.text_input("Documento", placeholder="Opcional")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("＋  REGISTRAR UNIDAD", use_container_width=True):
            if not plate_in:
                st.error("La matrícula es obligatoria.")
            else:
                res = api_post("/vehicles", {
                    "plate": plate_in, "plate_type": ptype_in,
                    "owner_name": oname_in or None,
                    "owner_doc":  odoc_in  or None
                })
                if res.get("ok"):
                    st.success(f"✓ {res.get('message','Unidad registrada.')}")
                    st.cache_data.clear()
                elif res.get("error") == "PLATE_EXISTS":
                    st.warning(f"La matrícula {plate_in} ya existe en el sistema.")
                else:
                    st.error(f"Error: {res.get('error','desconocido')}")

    with col_p:
        preview = plate_in if plate_in else "ABC·123"
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    padding:40px 20px;gap:24px;">
          <div style="font-family:'Orbitron',monospace;font-size:8px;
                      color:var(--muted);letter-spacing:4px;">PREVISUALIZACIÓN</div>
          <div style="position:relative;">
            <div style="background:#fff;border-radius:10px;padding:20px 40px;
                        text-align:center;min-width:260px;
                        box-shadow:0 0 60px rgba(0,255,136,.2),0 0 120px rgba(0,255,136,.08);
                        border:2px solid rgba(0,255,136,.3);">
              <div style="font-size:8px;font-weight:700;letter-spacing:5px;
                          color:#1a3a6a;margin-bottom:6px;">🇨🇴  C O L O M B I A</div>
              <div style="font-family:'Orbitron',monospace;font-size:46px;
                          font-weight:900;color:#0a0a1a;letter-spacing:8px;
                          line-height:1;">{preview}</div>
            </div>
            <div style="position:absolute;inset:-2px;border-radius:12px;
                        border:1px solid rgba(0,255,136,.15);
                        animation:pulse-green 3s ease-in-out infinite;
                        pointer-events:none;"></div>
          </div>
          <div style="font-family:'Orbitron',monospace;font-size:8px;
                      color:var(--muted);letter-spacing:3px;">{ptype_in.upper()}</div>
        </div>""", unsafe_allow_html=True)

# ── RELOJ EN TIEMPO REAL + AUTO-REFRESH cada 30s ──────────────────────────────
st.markdown("""
<script>
const DAYS   = ['DOMINGO','LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO'];
const MONTHS = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO',
                'JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'];

function updateClock() {
  const now = new Date(new Date().toLocaleString("en-US", {timeZone: "America/Bogota"}));
  const h   = String(now.getHours()).padStart(2,'0');
  const m   = String(now.getMinutes()).padStart(2,'0');
  const s   = String(now.getSeconds()).padStart(2,'0');
  const day = DAYS[now.getDay()];
  const d   = String(now.getDate()).padStart(2,'0');
  const mo  = MONTHS[now.getMonth()];
  const yr  = now.getFullYear();

  const clock  = document.getElementById('sit-clock');
  const dateEl = document.getElementById('sit-date');
  if (clock)  clock.textContent  = h + ':' + m + ':' + s;
  if (dateEl) dateEl.textContent = day + ' ' + d + ' ' + mo + ' ' + yr;
}

updateClock();
setInterval(updateClock, 1000);
setTimeout(() => location.reload(), 30000);
</script>
""", unsafe_allow_html=True)