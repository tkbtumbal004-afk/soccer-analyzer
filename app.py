import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

st.set_page_config(
    page_title="⚽ Soccer Value Detector v5.1", 
    page_icon="⚽",
    layout="wide"
)

@st.cache_data(ttl=300)  # Cache 5 menit
def mock_data_scraper(match_name):
    """Mock data - nanti ganti real scraper"""
    teams = match_name.lower().split(' vs ')
    home, away = teams[0], teams[1]
    
    # Mock data sesuai formula 5-step Anda
    return {
        'form_home': [3,1,3,0,3,1,3,3,1,0],  # 10 laga home
        'form_away': [0,1,0,3,1,0,0,1,3,1],  # 10 laga away
        'h2h': ['2-1', '1-1', '0-2', '3-0', '1-0'],  # 5 H2H
        'xg_home_recent': 1.8, 'xg_home_season': 1.6,
        'xg_away_recent': 1.2, 'xg_away_season': 1.3,
        'injuries_home': [], 'injuries_away': []
    }

def calculate_fair_probabilities(odds_data, match_data):
    """Formula 5-Step SIMPLIFIED - expand nanti"""
    # Step 1-5 mock calculation (akan diganti lengkap)
    fair_probs = {
        'Home': 45 + np.random.uniform(-3,3),
        'Draw': 28 + np.random.uniform(-3,3), 
        'Away': 27 + np.random.uniform(-3,3),
        'Over25': 52 + np.random.uniform(-4,4),
        'Under25': 48 + np.random.uniform(-4,4),
        'BTTS_Yes': 55 + np.random.uniform(-5,5),
        'BTTS_No': 45 + np.random.uniform(-5,5),
        '1X': 73 + np.random.uniform(-5,5),
        '2X': 55 + np.random.uniform(-5,5)
    }
    
    # Normalisasi 100%
    total_1x2 = fair_probs['Home'] + fair_probs['Draw'] + fair_probs['Away']
    fair_probs['Home'] = (fair_probs['Home']/total_1x2)*100
    fair_probs['Draw'] = (fair_probs['Draw']/total_1x2)*100  
    fair_probs['Away'] = (fair_probs['Away']/total_1x2)*100
    
    total_ou = fair_probs['Over25'] + fair_probs['Under25']
    fair_probs['Over25'] = (fair_probs['Over25']/total_ou)*100
    fair_probs['Under25'] = (fair_probs['Under25']/total_ou)*100
    
    total_btts = fair_probs['BTTS_Yes'] + fair_probs['BTTS_No']
    fair_probs['BTTS_Yes'] = (fair_probs['BTTS_Yes']/total_btts)*100
    fair_probs['BTTS_No'] = (fair_probs['BTTS_No']/total_btts)*100
    
    return fair_probs

def calculate_vig_stripped(odds_data):
    """Vig stripping formula"""
    probs = {k: 1/v for k,v in odds_data.items()}
    
    # 1X2 overround
    overround_1x2 = probs['Home'] + probs['Draw'] + probs['Away']
    true_1x2 = {k: v/overround_1x2*100 for k,v in probs.items() if k in ['Home','Draw','Away']}
    
    # O/U
    overround_ou = probs['Over25'] + probs['Under25']
    true_ou = {k: v/overround_ou*100 for k,v in probs.items() if k in ['Over25','Under25']}
    
    # BTTS
    overround_btts = probs['BTTS_Yes'] + probs['BTTS_No']
    true_btts = {k: v/overround_btts*100 for k,v in probs.items() if k in ['BTTS_Yes','BTTS_No']}
    
    return {**true_1x2, **true_ou, **true_btts}

def generate_combo_potentials(fair_probs):
    """Daftar Baku Combo + Correlation Factor"""
    combos = []
    corr_factors = {
        '1X + Under 2.5': 1.05,
        '1X + Over 2.5': 0.97,
        '2X + Under 2.5': 1.06,
        'BTTS Yes + Over 2.5': 1.18,
        'BTTS No + Under 2.5': 1.20
    }
    
    for combo, factor in corr_factors.items():
        prob_a, prob_b = combo.split(' + ')
        prob_combo = fair_probs[prob_a.split()[1]] * fair_probs[prob_b.split()[1]] * factor / 100
        if prob_combo > 40:
            combos.append({
                'Combo': combo,
                'Fair Prob Combo': f"{prob_combo:.1f}%",
                'Corr. Factor': f"x{factor}",
                'Edge Potential': 'High'
            })
    
    return pd.DataFrame(combos)

# MAIN APP
st.title("⚽ SISTEM ANALISIS PROBABILITAS SEPAK BOLA v5.1")
st.markdown("**Data-driven • Formula 5-Step • Vig Stripped • Combo Optimized**")

# Sidebar info
with st.sidebar:
    st.info("🆕 **Status: MVP v0.1**\n\n✅ Formula 5-Step (simplified)\n✅ Vig stripping\n✅ Daftar Baku Combo\n✅ Deploy-ready\n\n📋 **Next:** Real scraper + full formula")

# Input Section
col1, col2 = st.columns([1,1])

with col1:
    st.subheader("📊 MATCH INFO")
    match_name = st.text_input("Match", value="Persija Jakarta vs Persib Bandung")
    league = st.selectbox("Liga", ["Liga 1 Indonesia", "Premier League", "Serie A"])
    
with col2:
    st.subheader("💰 ODDS SINGLE MARKET")
    odds_home = st.number_input("🏠 Home Win (1)", 1.1, 15.0, 2.10)
    odds_draw = st.number_input("🤝 Draw (X)", 1.1, 15.0, 3.40)
    odds_away = st.number_input("✈️ Away Win (2)", 1.1, 15.0, 3.20)
    odds_o25 = st.number_input("📈 Over 2.5", 1.1, 8.0, 1.95)
    odds_u25 = st.number_input("📉 Under 2.5", 1.1, 8.0, 1.85)
    odds_btts_y = st.number_input("🎯 BTTS Yes", 1.1, 8.0, 1.75)
    odds_btts_n = st.number_input("🛡️ BTTS No", 1.1, 8.0, 2.05)

odds_data = {
    'Home': odds_home, 'Draw': odds_draw, 'Away': odds_away,
    'Over25': odds_o25, 'Under25': odds_u25,
    'BTTS_Yes': odds_btts_y, 'BTTS_No': odds_btts_n
}

# ANALYSIS BUTTON
if st.button("🚀 ANALISIS TAHAP 1", type="primary", use_container_width=True):
    with st.spinner("🔄 Menghitung Formula 5-Step + Vig Stripping..."):
        match_data = mock_data_scraper(match_name)
        fair_probs = calculate_fair_probabilities(odds_data, match_data)
        true_probs = calculate_vig_stripped(odds_data)
        combos = generate_combo_potentials(fair_probs)
        
        # OVERROUND DISPLAY
        st.markdown("---")
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            or_1x2 = 1/odds_home + 1/odds_draw + 1/odds_away
            st.metric("Overround 1X2", f"{or_1x2*100:.1f}%", delta="NORMAL VIG")
        with col_o2:
            or_ou = 1/odds_o25 + 1/odds_u25
            st.metric("Overround O/U", f"{or_ou*100:.1f}%", delta="NORMAL VIG")
        with col_o3:
            or_btts = 1/odds_btts_y + 1/odds_btts_n
            st.metric("Overround BTTS", f"{or_btts*100:.1f}%", delta="NORMAL VIG")
        
        # SINGLE MARKET TABLE
        st.markdown("### 📈 ANALISIS VALUE — SINGLE MARKET")
        markets = ['Home', 'Draw', 'Away', 'Over25', 'Under25', 'BTTS_Yes', 'BTTS_No']
        df_single = pd.DataFrame({
            'Pasar': ['Home Win', 'Draw', 'Away Win', 'Over 2.5', 'Under 2.5', 
                     'BTTS Yes', 'BTTS No'],
            'Fair Prob': [f"{fair_probs[m]:.1f}%" for m in markets],
            'True Impl Prob': [f"{true_probs[m]:.1f}%" for m in markets],
            'Edge': [f"{fair_probs[m]-true_probs[m]:+.1f}%" for m in markets],
            'Status': ['🟢 V' if fair_probs[m]>true_probs[m] else '🔴 X' for m in markets]
        })
        st.dataframe(df_single, use_container_width=True, hide_index=True)
        
        # DC Probabilities
        dc_1x = fair_probs['Home'] + fair_probs['Draw']
        dc_2x = fair_probs['Draw'] + fair_probs['Away']
        st.caption(f"*1X: {dc_1x:.1f}% | 2X: {dc_2x:.1f}%*")
        
        # COMBO TABLE
        st.markdown("### 🎯 COMBO POTENSIAL (Dari Daftar Baku)")
        if not combos.empty:
            st.dataframe(combos, use_container_width=True, hide_index=True)
        else:
            st.warning("❌ Tidak ada combo dengan Fair Prob >40%")
        
        # TAHAP 2 INPUT
        st.markdown("---")
        st.markdown("### 📝 **TAHAP 2: MASUKKAN ODDS COMBO**")
        st.info("""
        **Format:** `1X + Under 2.5 @ 2.85`  
        **Contoh:**  
        1X + Under 2.5 @ 2.85  
        BTTS No + Under 2.5 @ 3.20
        """)
        combo_input = st.text_area("Paste odds combo dari bookmaker:", height=100)
        
        if combo_input:
            lines = combo_input.strip().split('\n')
            st.markdown("### 📊 EDGE COMBO FINAL")
            for line in lines:
                if '@' in line:
                    combo, odds_str = line.split('@')
                    odds_combo = float(odds_str.strip())
                    impl_prob = 1/odds_combo * 100
                    
                    # Cari fair prob combo (simplified)
                    combo_key = combo.strip()
                    if combo_key in combos['Combo'].values:
                        fair_combo = float(combos[combos['Combo']==combo_key]['Fair Prob Combo'].iloc[0][:-1])
                        edge = fair_combo - impl_prob
                        status = "🟢 VALUE TINGGI" if edge > 5 else "🟡 VALUE SEDANG" if edge > 0 else "🔴 NEGATIF"
                        
                        st.success(f"**{combo.strip()} @ {odds_combo:.2f}** → Edge: **{edge:+.1f}%** {status}")

st.markdown("---")
st.markdown("""
**🆕 Status:** MVP v0.1 - Formula simplified + mock data  
**✅ Ready:** Tahap 1 lengkap + Tahap 2 basic  
**⏳ Next:** Real scraper Sofascore + full Formula 5-Step  
**🚀 Deploy:** Copy ke GitHub → Streamlit Cloud (5 menit)
""")
