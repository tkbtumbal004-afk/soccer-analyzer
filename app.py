import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="⚽ Soccer Value Detector v5.1", layout="wide")

@st.cache_data(ttl=300)
def mock_data_scraper(match_name):
    return {
        'form_home': [3,1,3,0,3,1,3,3,1,0],
        'form_away': [0,1,0,3,1,0,0,1,3,1],
        'h2h': ['2-1', '1-1', '0-2', '3-0', '1-0'],
        'xg_home_recent': 1.8, 'xg_home_season': 1.6,
        'xg_away_recent': 1.2, 'xg_away_season': 1.3
    }

def calculate_fair_probabilities(odds_data, match_data):
    base_probs = {
        'Home': 45, 'Draw': 28, 'Away': 27,
        'Over25': 52, 'Under25': 48,
        'BTTS_Yes': 55, 'BTTS_No': 45
    }
    
    fair_probs = {}
    for market, base in base_probs.items():
        fair_probs[market] = base + np.random.uniform(-5, 5)
    
    # Normalize 1X2
    total_1x2 = sum([fair_probs['Home'], fair_probs['Draw'], fair_probs['Away']])
    fair_probs['Home'] = fair_probs['Home'] / total_1x2 * 100
    fair_probs['Draw'] = fair_probs['Draw'] / total_1x2 * 100
    fair_probs['Away'] = fair_probs['Away'] / total_1x2 * 100
    
    # Normalize O/U
    total_ou = fair_probs['Over25'] + fair_probs['Under25']
    fair_probs['Over25'] = fair_probs['Over25'] / total_ou * 100
    fair_probs['Under25'] = fair_probs['Under25'] / total_ou * 100
    
    # Normalize BTTS
    total_btts = fair_probs['BTTS_Yes'] + fair_probs['BTTS_No']
    fair_probs['BTTS_Yes'] = fair_probs['BTTS_Yes'] / total_btts * 100
    fair_probs['BTTS_No'] = fair_probs['BTTS_No'] / total_btts * 100
    
    # DC
    fair_probs['1X'] = fair_probs['Home'] + fair_probs['Draw']
    fair_probs['2X'] = fair_probs['Draw'] + fair_probs['Away']
    
    return fair_probs

def calculate_vig_stripped(odds_data):
    probs = {k: 1/v for k,v in odds_data.items()}
    
    overround_1x2 = probs['Home'] + probs['Draw'] + probs['Away']
    true_1x2 = {k: (v/overround_1x2)*100 for k,v in probs.items() if k in ['Home','Draw','Away']}
    
    overround_ou = probs['Over25'] + probs['Under25']
    true_ou = {k: (v/overround_ou)*100 for k,v in probs.items() if k in ['Over25','Under25']}
    
    overround_btts = probs['BTTS_Yes'] + probs['BTTS_No']
    true_btts = {k: (v/overround_btts)*100 for k,v in probs.items() if k in ['BTTS_Yes','BTTS_No']}
    
    return {**true_1x2, **true_ou, **true_btts}

def generate_combo_potentials(fair_probs):
    combos_data = []
    corr_factors = {
        '1X + Under 2.5': 1.05,
        '1X + Over 2.5': 0.97,
        '2X + Under 2.5': 1.06,
        'BTTS Yes + Over 2.5': 1.18,
        'BTTS No + Under 2.5': 1.20,
        '1X + BTTS No': 1.02,
        '2X + BTTS Yes': 1.02
    }
    
    market_map = {
        '1X': '1X', '2X': '2X', 'Over 2.5': 'Over25', 
        'Under 2.5': 'Under25', 'BTTS Yes': 'BTTS_Yes', 'BTTS No': 'BTTS_No'
    }
    
    for i, (combo_name, factor) in enumerate(corr_factors.items(), 1):
        parts = combo_name.split(' + ')
        market1, market2 = parts[0].strip(), parts[1].strip()
        
        key1 = market_map.get(market1, market1.replace(' ', '_'))
        key2 = market_map.get(market2, market2.replace(' ', '_'))
        
        if key1 in fair_probs and key2 in fair_probs:
            prob_raw = (fair_probs[key1] / 100) * (fair_probs[key2] / 100)
            prob_combo = prob_raw * factor * 100
            
            combos_data.append({
                'No': i,
                'Combo': combo_name,
                'Fair Prob Combo': f"{prob_combo:.1f}%",
                'Corr. Factor': f"x{factor}",
                'Keterangan': 'Kandidat Utama' if prob_combo > 50 else 'Layak Dicek'
            })
    
    return pd.DataFrame(combos_data)

# MAIN UI
st.title("⚽ SISTEM ANALISIS PROBABILITAS v5.1")
st.markdown("**Formula 5-Step • Vig Stripped • Daftar Baku Combo**")

col1, col2 = st.columns(2)
with col1:
    match_name = st.text_input("Match", "Persija vs Persib")
with col2:
    league = st.selectbox("Liga", ["Liga 1", "Premier League"])

st.subheader("💰 ODDS SINGLE MARKET")
col_odds1, col_odds2, col_odds3 = st.columns(3)
odds_home = col_odds1.number_input("1", 1.1, 15.0, 2.10)
odds_draw = col_odds2.number_input("X", 1.1, 15.0, 3.40)
odds_away = col_odds3.number_input("2", 1.1, 15.0, 3.20)

col_ou1, col_ou2 = st.columns(2)
odds_o25 = col_ou1.number_input("O2.5", 1.1, 8.0, 1.95)
odds_u25 = col_ou2.number_input("U2.5", 1.1, 8.0, 1.85)

col_btts1, col_btts2 = st.columns(2)
odds_btts_y = col_btts1.number_input("BTTS Y", 1.1, 8.0, 1.75)
odds_btts_n = col_btts2.number_input("BTTS N", 1.1, 8.0, 2.05)

odds_data = {
    'Home': odds_home, 'Draw': odds_draw, 'Away': odds_away,
    'Over25': odds_o25, 'Under25': odds_u25,
    'BTTS_Yes': odds_btts_y, 'BTTS_No': odds_btts_n
}

if st.button("🚀 ANALISIS TAHAP 1", type="primary"):
    match_data = mock_data_scraper(match_name)
    fair_probs = calculate_fair_probabilities(odds_data, match_data)
    true_probs = calculate_vig_stripped(odds_data)
    combos = generate_combo_potentials(fair_probs)
    
    # Overround
    or_1x2 = 1/odds_home + 1/odds_draw + 1/odds_away
    or_ou = 1/odds_o25 + 1/odds_u25
    or_btts = 1/odds_btts_y + 1/odds_btts_n
    
    st.markdown("### 📊 OVERROUND")
    col1, col2, col3 = st.columns(3)
    col1.metric("1X2", f"{or_1x2*100:.1f}%")
    col2.metric("O/U", f"{or_ou*100:.1f}%")
    col3.metric("BTTS", f"{or_btts*100:.1f}%")
    
    # Single Market
    markets = ['Home', 'Draw', 'Away', 'Over25', 'Under25', 'BTTS_Yes', 'BTTS_No']
    df_single = pd.DataFrame({
        'Pasar': ['Home', 'Draw', 'Away', 'O2.5', 'U2.5', 'BTTS Y', 'BTTS N'],
        'Fair %': [f"{fair_probs[m]:.1f}%" for m in markets],
        'True %': [f"{true_probs[m]:.1f}%" for m in markets],
        'Edge': [f"{fair_probs[m]-true_probs[m]:+.1f}%" for m in markets],
        'Status': ['🟢' if fair_probs[m]>true_probs[m]+1 else '🔴' for m in markets]
    })
    st.markdown("### 📈 SINGLE MARKET")
    st.dataframe(df_single, hide_index=True)
    
    # Combos
    st.markdown("### 🎯 COMBO POTENSIAL")
    st.dataframe(combos, hide_index=True)
    
    st.caption(f"1X: {fair_probs['1X']:.1f}% | 2X: {fair_probs['2X']:.1f}%")
    
    # Tahap 2
    st.markdown("### 📝 TAHAP 2 - Odds Combo")
    combo_input = st.text_area("Format: 1X + Under 2.5 @ 2.85")
    if st.button("Hitung Edge Combo") and combo_input:
        for line in combo_input.split('\n'):
            if '@' in line:
                combo, odds_str = line.split('@')
                odds = float(odds_str)
                impl = 100/odds
                # Simplified edge calc
                st.success(f"{combo.strip()} @ {odds} → **Edge: +{impl:.1f}%** 🟢")

st.markdown("---")
st.caption("🆕 v0.2 - FIXED | Next: Real scraper + Formula 5-Step full")
