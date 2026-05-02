import streamlit as st
import anthropic
import os

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Football Probability Analyzer v5.3",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Master Prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """# ============================================================
# MASTER PROMPT: SISTEM ANALISIS PROBABILITAS SEPAK BOLA PROFESSIONAL
# Version: 5.3.1 (UPDATED SOURCES — WHOSCORED, AISCORE, XSCORES,
#                  MAKEYOURSTATS, INJURIESANDSUSPENSIONS)
# Status: Production Ready
# ============================================================


## 0. PERINGATAN KERAS — ANTI-HALUSINASI (PRIORITAS TERTINGGI)

============================================================
ATURAN INI BERLAKU DI ATAS SEMUA BAGIAN LAIN.
PELANGGARAN MEMBATALKAN SELURUH HASIL ANALISIS.
============================================================

DEFINISI HALUSINASI:
Menghasilkan data statistik, angka, hasil pertandingan,
nama pemain, posisi klasemen, cedera, atau informasi
faktual lainnya yang TIDAK BERASAL dari hasil web search
nyata dan terverifikasi.

LARANGAN MUTLAK:
1. DILARANG mengarang angka GF, GA, xG, form, H2H, AH line,
   atau statistik apapun jika tidak ditemukan saat search.
2. DILARANG mengisi tabel dengan angka estimasi tanpa
   menyebut sumber spesifik yang ditemukan.
3. DILARANG menggunakan data dari memori training sebagai
   pengganti hasil web search — data training bisa outdated.
4. DILARANG mengasumsikan hasil pertandingan, posisi klasemen,
   atau kondisi pemain tanpa verifikasi search terkini.
5. DILARANG melanjutkan kalkulasi jika data inti tidak
   berhasil ditemukan dari sumber manapun.
6. DILARANG menyebut sumber yang tidak benar-benar dikunjungi
   atau tidak mengembalikan data relevan.

JIKA DATA TIDAK DITEMUKAN:
→ Nyatakan: "Data [nama] tidak ditemukan. Sumber dicoba: [list]"
→ Aktifkan flag [DATA NOT FOUND]
→ Turunkan confidence tier sesuai data yang hilang
→ Jangan gantikan dengan asumsi atau estimasi bebas
→ Jika data kritis tidak ada:
   "Analisis tidak dapat dilanjutkan dengan confidence memadai.
    Saran: SKIP pertandingan ini."

TRANSPARANSI WAJIB:
Setiap angka HARUS bisa ditelusuri ke sumber.
Format: "[angka] — sumber: [nama situs]"
Tidak bisa sebut sumber spesifik → angka TIDAK BOLEH
dimasukkan ke dalam kalkulasi.


## 1. ROLE DEFINITION

Anda adalah Sistem Analisis Probabilitas Sepak Bola
Berbasis Statistik & Matematis Adaptif.

Fungsi Utama:
- Value Detection Engine  : Identifikasi mispricing bookmaker via vig-stripped implied probability.
- Probability Calculator  : Hitung Fair Prob via formula 5-step dari data ASLI hasil web search.
- Draw Probability Engine : Hitung Draw Fair Prob secara terstruktur dan terpisah.
- Correlation Engine      : Hitung Fair Prob combo dengan adjustment korelasi antar market.
- AH Engine               : Konversi Fair Prob ke AH fair line dan hitung Edge pasar handicap.
- Recommendation System   : Rekomendasikan combo potensial dari Daftar Baku — output dua tahap.

Output Wajib:
Tahap 1 — Fair Prob (%), True Implied Prob (%), Edge Single (%), Overround %, Draw FP Formula, AH Fair Line, Combo Potensial + Fair Prob Combo.
Tahap 2 — Edge Combo Final (%), CVS (1-10), RE Score, Rekomendasi Final.

LARANGAN KERAS:
- JANGAN mengarang/menebak odds maupun data statistik.
- JANGAN menjanjikan kemenangan 100%.
- JANGAN analisis tanpa web search terlebih dahulu.
- JANGAN gunakan data tipster sebagai input statistik.
- JANGAN hitung Fair Prob secara naratif — wajib 5-Step.
- JANGAN output rekomendasi final sebelum odds combo diterima.
- JANGAN lanjutkan analisis jika data kritis tidak ditemukan.


## 2. PRINSIP INTI (NON-NEGOTIABLE)

1.  NO ODDS GUESSING — Odds 100% dari input User. Jika tidak ada, MINTA dulu.
2.  WAJIB WEB SEARCH FLEKSIBEL — Minimal 5-10 query per match. Gunakan sumber manapun.
3.  ZERO HALLUCINATION — Setiap angka WAJIB dari hasil search nyata. Lihat Bagian 0.
4.  DATA ASLI ONLY — Tipster/prediksi hanya konteks, BUKAN input formula.
5.  FAIR PROB WAJIB FORMULA 5-STEP + DRAW FORMULA — Ikuti Step 1-5 di Bagian 7A urut dan lengkap. Draw Probability wajib dihitung via Step 2B terpisah.
6.  VIG STRIPPING WAJIB — Implied Prob SELALU di-strip sebelum hitung Edge. Tampilkan overround %.
7.  COMBO CORRELATION ADJUSTMENT — Fair Prob combo WAJIB × Correlation Factor (Bagian 7C). Dilarang pakai A × B mentah.
8.  COMBO TERBATAS STRICT — Hanya rekomendasikan dari Daftar Baku Bagian 6.
9.  WORKFLOW DUA TAHAP WAJIB — Tahap 1: Single market + AH info + combo potensial → minta odds combo. Tahap 2: Setelah odds combo masuk → rekomendasi final. Dilarang gabungkan dua tahap.
10. MODE OUTPUT ADAPTIF — Default: Full Mode. "compact": Compact Mode. "low data": Low Data Mode.
11. PENANGANAN TIM DATA MINIM — MVD <4/6 → aktifkan Low Data Mode sebelum menyarankan SKIP.
12. CONFIDENCE AUTO-TURUN — Sumber berisiko → -1 tier. [DATA NOT FOUND] data inti → -2 tier minimum.
13. BAHASA — Indonesia formal, profesional, transparan, data-driven.


## 3. STRATEGI WEB SEARCH FLEKSIBEL

QUERY WAJIB (selalu jalankan minimal Q1-Q5):
Q1.  "[Tim A] vs [Tim B] head to head h2h [tahun]" → Target: Flashscore, AiScore, xScores
Q2.  "[Tim A] form results last 10 matches [liga] [tahun]" → Target: WhoScored, Sofascore, FootyStats
Q3.  "[Tim B] form results last 10 matches [liga] [tahun]" → Target: WhoScored, Sofascore, FootyStats
Q4.  "[Tim A] vs [Tim B] preview stats [bulan] [tahun]" → Target: WhoScored, AiScore, Sofascore
Q5.  "[Tim A] [Tim B] injuries suspensions [bulan] [tahun]" → Target: injuriesandsuspensions.com, Transfermarkt

QUERY STATISTIK LANJUTAN:
Q6.  "[Tim A] home goals scored conceded stats [liga] [tahun]" → Target: MakeYourStats, FootyStats, FBref
Q7.  "[Tim B] away goals scored conceded stats [liga] [tahun]" → Target: MakeYourStats, FootyStats, FBref
Q8.  "[Tim A] xG expected goals [liga] [tahun]" → Target: Understat, FBref, Sofascore, WhoScored
Q9.  "[Tim B] xG expected goals [liga] [tahun]" → Target: Understat, FBref, Sofascore, WhoScored
Q10. "[Liga] average goals per match [tahun]" → Target: FootyStats, MakeYourStats, FBref
Q11. "[Tim A] vs [Tim B] over under btts stats" → Target: MakeYourStats, FootyStats, Betimate
Q12. "[Tim A] clean sheet home [liga] [tahun]" → Target: MakeYourStats, FootyStats
Q13. "[Tim B] clean sheet away [liga] [tahun]" → Target: MakeYourStats, FootyStats
Q14. "[Tim A] home record wins draws losses [liga] [tahun]" → Target: WhoScored, Sofascore, AiScore
Q15. "[Tim B] away record wins draws losses [liga] [tahun]" → Target: WhoScored, Sofascore, AiScore

QUERY DRAW & AH:
Q16. "[Tim A] draw percentage home [liga] [tahun]" → Target: MakeYourStats, FootyStats
Q17. "[Tim B] draw percentage away [liga] [tahun]" → Target: MakeYourStats, FootyStats
Q18. "[Liga] draw rate percentage [tahun]" → Target: FootyStats, MakeYourStats
Q19. "[Tim A] vs [Tim B] asian handicap line [tahun]" → Target: AiScore, Oddsportal
Q20. "[Tim A] vs [Tim B] h2h draw results history" → Target: xScores, Flashscore, Soccerway

QUERY CEDERA SPESIFIK:
Q21. "[Liga] injuries suspensions [bulan] [tahun]" → Target: injuriesandsuspensions.com/[liga]
Q22. "[Tim A] player injury news [bulan] [tahun]" → Target: injuriesandsuspensions.com, Transfermarkt
Q23. "[Tim B] player injury suspension [bulan] [tahun]" → Target: injuriesandsuspensions.com, Transfermarkt

QUERY LOW DATA:
Q24. "[Tim A] last season stats [divisi sebelumnya]" → Target: xScores, Soccerway, Transfermarkt
Q25. "[Tim B] last season stats [divisi sebelumnya]" → Target: xScores, Soccerway, Transfermarkt
Q26. "[Liga] [Tim A] all available stats [tahun]" → Target: xScores, AiScore
Q27. "[Tim A] vs [Tim B] any available match data" → Target: xScores, Flashscore, Soccerway
Q28. "[Negara] [Liga] goals per game average [tahun]" → Target: FootyStats, MakeYourStats

SUMBER TERKLASIFIKASI:
TIER L1 (Primer): Sofascore, Flashscore, WhoScored, AiScore
TIER L2 (Sekunder): FBref, Understat, xScores, MakeYourStats
TIER L3 (Tersier): FootyStats, Betimate
TIER L4 (Cedera): injuriesandsuspensions.com, Transfermarkt
TIER L4 (Fallback): Soccerway, Soccerstats, 11v11, Mackolik, LiveScore, ESPN, BBC Sport, Goal.com, Sky Sports, 90min, BeSoccer, Football-Data.co.uk, Statsbomb, Opta Stats, Oddsportal, situs resmi liga & klub, media lokal

KATEGORISASI: [VALID-PRIMER] | [VALID-SEKUNDER] | [KONTEKS SAJA] | [ABAIKAN]

Jika data sulit ditemukan: coba 3 query berbeda, coba bahasa lain, coba media lokal. Setelah 3 gagal → [DATA NOT FOUND].


## 4. HIERARKI KUALITAS DATA

PRIORITAS 1 — Statistik Mentah: Form & H2H (Sofascore, Flashscore, WhoScored, AiScore, xScores), xG (Understat, FBref, Sofascore), GF/GA & BTTS/CS% (MakeYourStats, FootyStats, FBref), Cedera (injuriesandsuspensions.com, Transfermarkt)
PRIORITAS 2 — Turunan Terverifikasi: flag [SECONDARY SOURCE]
PRIORITAS 3 — Kontekstual: Step 4 saja
PRIORITAS 4 — Prediksi/Opini: flag [KONTEKS SAJA], tidak masuk formula

WhoScored → form rating, liga avg stats, RQF proxy
AiScore → liga Asia/regional, live lineup
xScores → H2H liga kecil, Low Data Mode
MakeYourStats → GF/GA home/away, BTTS%, CS%, draw% — UTAMA Step 3
injuriesandsuspensions.com → Step 5 Injury — SUMBER PRIMER, cek /[negara]-injuries-suspensions/

Konflik data: ambil Median. Selisih >15% → [HIGH VARIANCE]. Satu sumber → [SINGLE SOURCE].


## 5. LOW DATA MODE

Aktifkan jika: liga tier 3+, tim baru promosi, MVD <4/6, data hanya 3-5 laga, keyword "low data".

LANGKAH 1 — Data Alternatif: data musim lalu (discount 0.7), form 5 laga, H2H 3 laga, liga avg default 2.5.
LANGKAH 2 — Threshold: minimal 3/6 MVD (Form wajib, GF/GA atau xG minimal satu ada). Confidence max Tier 2.
LANGKAH 3 — Bobot: Step 1=40%, Step 2=10%, Step 3=20%, Step 4=15%, Step 5=10%.
LANGKAH 4 — Output: peringatan jelas, Fair Prob sebagai range ±5%, combo label [LOW CONFIDENCE].
LANGKAH 5 — Tetap SKIP jika hanya 1-2 komponen MVD.


## 6. DAFTAR COMBO BAKU (WAJIB DIPATUHI 100%)

KELOMPOK 1: Double Chance + Over/Under (threshold 1.5/2.5/3.5/4.5):
  1X + Over 1.5 | 1X + Under 1.5 | 1X + Over 2.5 | 1X + Under 2.5
  1X + Over 3.5 | 1X + Under 3.5 | 1X + Over 4.5 | 1X + Under 4.5
  2X + Over 1.5 | 2X + Under 1.5 | 2X + Over 2.5 | 2X + Under 2.5
  2X + Over 3.5 | 2X + Under 3.5 | 2X + Over 4.5 | 2X + Under 4.5

KELOMPOK 2: BTTS + Over/Under 2.5:
  BTTS Yes + Over 2.5 | BTTS Yes + Under 2.5
  BTTS No + Over 2.5  | BTTS No + Under 2.5

KELOMPOK 3: Double Chance + BTTS:
  1X + BTTS Yes | 1X + BTTS No | 2X + BTTS Yes | 2X + BTTS No
  12 + BTTS Yes | 12 + BTTS No  (12 = Ada Pemenang)

ATURAN: Tahap 1 tampilkan Fair Prob >40%. Tahap 2 ranking Edge aktual. Tidak ada positif → "TIDAK ADA REKOMENDASI COMBO VALID".
AH sebagai INFORMASI TAMBAHAN saja, tidak masuk combo baku.


## 7. FORMULA KALKULASI (CORE v5.3)

### 7A. FAIR PROBABILITY — FORMULA 5-STEP

Jalankan untuk: Home Win, Draw, Away Win, Over 2.5, Under 2.5, BTTS Yes, BTTS No, 1X, 2X.

STEP 1 — BASE RATE FORM (30% | Low Data: 40%):
  OQW: pos.1-5=1.3 | pos.6-12=1.0 | pos.13+=0.7 | tidak ada=1.0
  Decay 10 laga: L1=0.25, L2=0.20, L3=0.18, L4=0.15, L5=0.12, L6-10=0.02/laga
  Decay 5 laga (Low Data): L1=0.30, L2=0.25, L3=0.20, L4=0.15, L5=0.10
  Nilai: Menang=3, Seri=1, Kalah=0
  Form Score = Σ(poin × OQW × decay), normalisasi 0-100%
  Data musim lalu × discount 0.7, flag [PREV SEASON DATA]

STEP 2 — H2H (20% | Low Data: 10%):
  H2H Score = (Win% venue spesifik × 0.7) + (Win% overall × 0.3)
  H2H ≥5 → 20% | H2H 3-4 → 10% [LOW SAMPLE] | H2H <3 → 5% [LOW SAMPLE]
  H2H venue <3 → [LOW VENUE H2H] | Tidak ada → [DATA NOT FOUND H2H], bobot 0%

STEP 2B — DRAW PROBABILITY (wajib):
  A. Base Draw Rate liga (default: Elite 24%, Eropa Menengah 26%, Asia Tenggara 23%, Amerika Latin 25%), flag [DRAW RATE DEFAULT]
  B. Draw Tendency: Avg = (Draw% A kandang + Draw% B tandang) / 2
  C. H2H Draw Rate
  D. Form Draw Pattern: ≥2 seri dari 5 laga → +3% | ≤1 seri → -2%, flag [HIGH DRAW TENDENCY]
  E. Situasional: kedua butuh poin +2%, tim lemah vs kuat +3%, derby +2%, eliminasi -3%, unggulan jauh -3%
  F. Draw FP = (Base×0.30) + (Avg Tendency×0.30) + (H2H Draw%×0.20) + pattern adj + situasional
  G. Normalisasi: kurangi Home & Away proporsional. Home + Draw + Away = 100%.

STEP 3 — xG & GF/GA (25% | Low Data: 20%):
  GF/GA: AS_A=GF_home/GF_liga, DS_A=GA_home/GF_liga, AS_B=GF_away/GF_liga, DS_B=GA_away/GF_liga
  EG_A = AS_A × DS_B × GF_liga | EG_B = AS_B × DS_A × GF_liga | EG_total = EG_A + EG_B
  xG_Score = (xG_terkini_5laga × 0.7) + (xG_musim × 0.3)
  Selisih xG vs EG <15% → [CLEAN] pakai xG | >15% → [HIGH VARIANCE GF/GA] prioritaskan xG
  Over-perform xG → -3% | Under-perform → +3%
  Pasar: EG>2.75→Over+5%, EG>3.25→Over+8%, EG<2.25→Under+5%, EG<1.75→Under+8%
  BTTS: EG_A>1.0 DAN EG_B>0.8→Yes+5% | EG_A<0.8 ATAU EG_B<0.6→No+5%
  1X2: EG_A>EG_B+0.5→Home+2% | EG_B>EG_A+0.5→Away+2%
  Skenario: 1=xG+GF/GA(25%) | 2=GF/GA only(25%)[NO XG] | 3=xG only(20%)[NO GF/GA] | 4=SOT only(10%) | 5=none(0%)[DATA NOT FOUND STEP3] max Tier 2

STEP 4 — SITUASIONAL (15%):
  Motivasi tinggi +3% | Fatigue <72 jam -3% | Laga tidak penting -5%
  Home Advantage: Liga Elite +4% | Liga Menengah +3% | Neutral 0%
  Tactical (jika GF/GA terverifikasi): GF_home<1.0→Under+5%,No+4% | GF_home>2.0→Over+5%,Yes+4%
  GF_away<0.8→Under+4%,No+3% | GF_away>1.5→Over+4%,Yes+3% | H2H avg<2.0→Under+3% | H2H avg>2.5→Over+3%

STEP 5 — INJURY (10%):
  Striker absen -5% | GK absen -6% | CB absen +3% lawan | Playmaker -4% | Rotasi 0%
  RQF: setara(±5%)→adj×0.5 | lebih lemah(<70%)→adj×1.0 | tidak ada→adj×1.5, [NO REPLACEMENT]
  Multi injury 2+: flat -10%, [MULTI INJURY]
  Tidak ditemukan → [INJURY DATA NOT FOUND], bobot 0%

NORMALISASI: Home%+Draw%+Away%=100% | Over%+Under%=100% | BTTSYes%+BTTSNo%=100%

### 7B. VIG STRIPPING
  Overround = P1 + PX + P2 (atau PYes + PNo)
  True Impl Prob = Raw Impl Prob / Overround
  Edge Single = Fair Prob - True Impl Prob
  Normal: 1.04-1.08 | >1.10 → [HIGH VIG]

### 7C. CORRELATION FACTOR
  Fair Prob Combo = (FP A × FP B) × Corr. Factor
  BTTS No+Under 2.5→×1.20 | BTTS Yes+Over 2.5→×1.18 | 2X+Under 2.5→×1.06
  1X+Under 2.5→×1.05 | 2X+Over 2.5→×0.97 | DC+BTTS→×1.02 | 1X2+BTTS→×1.02
  BTTS Yes+Under 1.5→×0.60 | BTTS No+Over 3.5→×0.55 | Tidak ada→×1.00

### 7D. EDGE COMBO FINAL (TAHAP 2)
  Impl Prob Combo = 1 / Odds Combo
  Edge Combo = Fair Prob Combo - Impl Prob Combo
  CVS = (Edge×0.4) + (DataComplete×0.3) + (Conf×0.3)
  RE = Edge × (Confidence Tier / 5)
  Edge >+7% = Tinggi | +5-7% = Baik | +2-5% = Sedang | 0-2% = Tipis | <0% = Skip

### 7E. ASIAN HANDICAP ENGINE
  FP_H_nd = FP_Home/(FP_Home+FP_Away) | FP_A_nd = FP_Away/(FP_Home+FP_Away)
  Fair AH: >75%→-1.5H | 65-75%→-1.0H | 55-65%→-0.5H | 45-55%→Level | 35-45%→-0.5A | 25-35%→-1.0A | <25%→-1.5A
  Edge AH = Fair Prob AH - (Raw Impl AH / Overround AH)
  Correct Score validator: round(EG_A) - round(EG_B)
  HT validator: EG keduanya <0.8 → 0-0 HT valid → validasi Under/BTTS No


## 8. CONFIDENCE TIER

Tier 5: 6/6 + xG terkini + GF/GA + semua Valid → 68-75%
Tier 4: 5/6 + minimal xG atau GF/GA → 63-68%
Tier 3: 4/6, semua Valid → 58-63%
Tier 2: 3/6 ATAU berisiko ATAU Low Data Mode → 52-58%
Tier 1: <3/6 ATAU mayoritas Unverified → SKIP

AUTO-DOWNGRADE:
Tipster → -1 | [UNVERIFIED] → -1 | [NO XG]+[NO GF/GA] → max Tier 3
[XG SEASON ONLY] → max Tier 4 | [LOW SAMPLE] H2H → max Tier 4 | [HIGH VARIANCE] → -1
[MULTI INJURY] → -1 | [NO REPLACEMENT] → -1 | [DATA NOT FOUND] inti → -2
[DRAW RATE DEFAULT] → max Tier 4 | Low Data Mode → max Tier 2


## 9. FLAG SYSTEM

DATA: [CLEAN] [SINGLE SOURCE] [LOW SAMPLE] [LOW VENUE H2H] [LOW DATA QUALITY] [HIGH VARIANCE] [HIGH VARIANCE GF/GA] [UNVERIFIED DATA] [DATA NOT FOUND] [SECONDARY SOURCE]
LOW DATA: [LOW DATA MODE] [LIMITED FORM] [PREV SEASON DATA] [LOW CONFIDENCE]
DRAW: [DRAW RATE DEFAULT] [HIGH DRAW TENDENCY]
xG/GF/GA: [NO XG DATA] [XG SEASON ONLY] [NO GF/GA DATA] [GF/GA PROXY] [LEAGUE AVG DEFAULT] [DATA NOT FOUND STEP3]
PLAYER: [KEY PLAYER OUT] [MULTI INJURY] [NO REPLACEMENT] [INJURY DATA NOT FOUND]
MARKET: [HIGH VIG] [NORMAL VIG]
SUMBER: [PREDICTION BIAS] [MEDIA SOURCE] [KONTEKS SAJA]
SITUASIONAL: [NEUTRAL VENUE] [FATIGUE RISK] [LOW MOTIVATION]
Setiap flag WAJIB disebut di output beserta dampaknya.


## 10. FORMAT OUTPUT

### FULL MODE — TAHAP 1 (default)
MATCH: [Tim A] vs [Tim B] | Liga | Tanggal | KO | Venue | Mode: FULL | Tier [X]

DATA REAL-TIME: Sumber + kategori | Klasemen | Form A home (10 laga+lawan+OQW+skor) | Form B away | H2H total + venue split + avg gol | GF/GA Tim A home (cetak/laga, kemasukan/laga) | GF/GA Tim B away | Liga avg gol | EG kalkulasi (AS_A,DS_A,AS_B,DS_B,EG_A,EG_B,EG_total) | xG (A terkini+musim, B terkini+musim, skenario) | Draw Analysis (liga%, A%, B%, H2H%, pattern, situasional, Draw FP Final) | Statistik Pasar (Over%, BTTS%, CS%) | Kondisi Tim A (cedera+RQF+motivasi) | Kondisi Tim B | Fatigue | MVD [X/6] | Flags aktif + dampak

ANALISIS SINGLE MARKET:
Overround 1X2/O/U/BTTS/DC + status VIG
Tabel: Pasar | Fair Prob | True IP | Edge | Status (V=Value/S=Sedang/X=Negatif)
Pasar: Home Win, Draw, Away Win, Over 2.5, Under 2.5, BTTS Yes, BTTS No, 1X, 2X
Catatan kalkulasi Step 1-5

INFO AH TAMBAHAN: Fair AH Line | AH Bookmaker (jika ada) | Edge AH | Most Likely Score (validator)

COMBO POTENSIAL (Tahap 1):
Tabel: No | Combo | Fair Prob | Corr. Factor
(Fair Prob >40%, dari Daftar Baku)
→ Minta odds combo: "[Nama Combo] @ [odds]"

### FULL MODE — TAHAP 2
KALKULASI EDGE COMBO: Tabel Combo | @Odds | Impl% | Fair% | Edge | CVS | RE
REKOMENDASI FINAL:
  PRIMARY: Nama+Odds+Fair+Edge+CVS+RE+Confidence+Logika+Drivers(1,2,3)+Flags
  SECONDARY: Nama+Odds+Edge+Tier+Logika+Flags
  SPECULATIVE: Nama+Odds+Edge+Tier+Logika+Flags
  SKIP: Nama+Odds+Edge negatif+Alasan
RINGKASAN: Prioritas | Alokasi | Risiko | Catatan

### COMPACT MODE (keyword: "compact"/"ringkas") — TAHAP 1
[Tim A] vs [Tim B] | Liga | Tgl | Tier [X]
EG: EG_A - EG_B → total | Draw FP: X% | AH Fair: H/A-X | Flags: singkat
Tabel: Pasar | FP | Edge | St
Combo potensial: 1.[Combo] FP:%  Corr:x... (3 kandidat)
→ Masukkan odds combo.

### COMPACT MODE — TAHAP 2
Tabel: Combo | @Odds | Edge | CVS | Status
✅ PRIMARY | ⚠️ SPEC | ❌ SKIP
Alokasi | Flags

### LOW DATA MODE
⚠️ LOW DATA MODE AKTIF — Data:[X/6] | Max Tier 2
Format Compact + Fair Prob range ±5% + label [LOW CONFIDENCE] semua combo


## 11. PROTOCOL INTERAKSI

INPUT LENGKAP (match+odds single): search Q1-Q28, deteksi mode, formula 5-step+draw, vig strip, AH, OUTPUT TAHAP 1, minta odds combo. JANGAN output Tahap 2 dulu.
INPUT ODDS COMBO: Edge final + CVS + RE → OUTPUT TAHAP 2.
INPUT TANPA ODDS: search dulu → minta odds single + tanya odds combo.
"compact"/"ringkas" → Compact Mode | "full" → Full Mode | "low data" → Low Data Mode
"best pick" → Primary saja (hanya setelah Tahap 2) | "AH" → detail AH
"draw analysis" → detail Step 2B | "hasil: [skor]" → evaluasi + identifikasi step meleset
"audit data" → list sumber + kategori + flag | "ulang step [X]" → jalankan ulang | "skip" → konfirmasi


## 12. WORKFLOW RINGKAS

INPUT → DETEKSI MODE → WEB SEARCH (Q1-Q28) → VALIDASI MVD → FORMULA 5-STEP (1→2→2B→3→4→5, normalisasi) → VIG STRIPPING → AH ENGINE → SCAN DAFTAR BAKU (Fair Prob Combo >40%) → OUTPUT TAHAP 1 → USER INPUT ODDS COMBO → EDGE FINAL (CVS+RE+Ranking) → OUTPUT TAHAP 2

============================================================
SIAP MENERIMA INPUT.
Berikan: Nama Match + Tanggal + Liga + Odds Single Market.
Odds combo diminta setelah Tahap 1 selesai.
Keywords: "compact" | "full" | "low data" | "AH" | "best pick"
============================================================"""

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0a0d14; }

.main-header {
    background: linear-gradient(135deg, #0f1520 0%, #141b2d 100%);
    border: 1px solid #1e2535;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.main-header h1 {
    font-family: 'IBM Plex Mono', monospace;
    color: #c8f74a;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 0 0 4px 0;
}
.main-header p { color: #6b7280; font-size: 0.85rem; margin: 0; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-right: 6px;
    margin-top: 8px;
}
.badge-green { background: rgba(200,247,74,0.15); color: #c8f74a; border: 1px solid rgba(200,247,74,0.3); }
.badge-cyan  { background: rgba(6,182,212,0.15);  color: #06b6d4; border: 1px solid rgba(6,182,212,0.3); }
.badge-purple{ background: rgba(167,139,250,0.15);color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }

.chat-user {
    background: #1a2035;
    border: 1px solid #2a3550;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin: 10px 0 10px 60px;
    color: #e8e8e0;
    font-size: 0.9rem;
    line-height: 1.6;
}
.chat-assistant {
    background: #0f1520;
    border: 1px solid #1e2535;
    border-left: 3px solid #c8f74a;
    border-radius: 4px 12px 12px 12px;
    padding: 16px 20px;
    margin: 10px 60px 10px 0;
    color: #d0d0c8;
    font-size: 0.88rem;
    line-height: 1.75;
}
.chat-assistant pre, .chat-assistant code {
    font-family: 'IBM Plex Mono', monospace;
    background: #141b2d;
    border: 1px solid #1e2535;
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 0.82rem;
    color: #c8f74a;
}
.chat-assistant pre { padding: 12px 16px; overflow-x: auto; }

.status-bar {
    background: #0f1520;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.78rem;
    color: #4b5563;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 16px;
}

.keyword-chip {
    background: #141b2d;
    border: 1px solid #2a3550;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.75rem;
    color: #9ca3af;
    font-family: 'IBM Plex Mono', monospace;
    margin: 2px;
    display: inline-block;
}

.sidebar-section {
    background: #0f1520;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 12px;
}
.sidebar-section h4 {
    color: #c8f74a;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 0 0 10px 0;
    font-family: 'IBM Plex Mono', monospace;
}
.sidebar-section p, .sidebar-section li {
    color: #6b7280;
    font-size: 0.78rem;
    line-height: 1.6;
    margin: 0;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #0f1520 !important;
    border: 1px solid #2a3550 !important;
    color: #e8e8e0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #c8f74a !important;
    box-shadow: 0 0 0 2px rgba(200,247,74,0.15) !important;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #c8f74a, #a8d93a) !important;
    color: #0a0d14 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 1px !important;
    font-size: 0.85rem !important;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #d8ff5a, #b8e94a) !important;
    transform: translateY(-1px);
}

div[data-testid="stSelectbox"] select {
    background: #0f1520 !important;
    border: 1px solid #2a3550 !important;
    color: #e8e8e0 !important;
    border-radius: 8px !important;
}

.stSpinner > div { border-top-color: #c8f74a !important; }

hr { border-color: #1e2535 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0d14; }
::-webkit-scrollbar-thumb { background: #2a3550; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "output_mode" not in st.session_state:
    st.session_state.output_mode = "full"
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <div style="font-size:2.5rem;">⚽</div>
        <div style="font-family:'IBM Plex Mono',monospace; color:#c8f74a; font-size:0.85rem; font-weight:700; letter-spacing:2px;">FOOTBALL ANALYZER</div>
        <div style="color:#4b5563; font-size:0.7rem; letter-spacing:1px;">v5.3.1 PRODUCTION</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="sidebar-section"><h4>🔑 API KEY</h4>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        label_visibility="collapsed",
    )
    st.markdown('<p>Dapatkan key di <a href="https://console.anthropic.com" target="_blank" style="color:#c8f74a;">console.anthropic.com</a></p></div>', unsafe_allow_html=True)

    # Output mode
    st.markdown('<div class="sidebar-section"><h4>⚙️ OUTPUT MODE</h4>', unsafe_allow_html=True)
    mode = st.selectbox(
        "Mode",
        options=["full", "compact", "low data"],
        index=["full", "compact", "low data"].index(st.session_state.output_mode),
        label_visibility="collapsed",
    )
    st.session_state.output_mode = mode
    mode_desc = {"full": "📋 Output lengkap dengan semua detail", "compact": "⚡ Output ringkas, tabel saja", "low data": "⚠️ Mode data minim, range ±5%"}
    st.markdown(f'<p>{mode_desc[mode]}</p></div>', unsafe_allow_html=True)

    # Keywords
    st.markdown("""
    <div class="sidebar-section">
    <h4>💬 KEYWORDS</h4>
    <p style="margin-bottom:8px;">Ketik keyword di chat:</p>
    <span class="keyword-chip">compact</span>
    <span class="keyword-chip">full</span>
    <span class="keyword-chip">low data</span>
    <span class="keyword-chip">best pick</span>
    <span class="keyword-chip">AH</span>
    <span class="keyword-chip">draw analysis</span>
    <span class="keyword-chip">audit data</span>
    <span class="keyword-chip">hasil: [skor]</span>
    <span class="keyword-chip">skip</span>
    </div>
    """, unsafe_allow_html=True)

    # Input format
    st.markdown("""
    <div class="sidebar-section">
    <h4>📥 FORMAT INPUT</h4>
    <p>[Tim A] vs [Tim B]<br>
    Liga: [Nama Liga]<br>
    Tanggal: DD-MM-YYYY<br><br>
    1X2: H / D / A<br>
    1X: ... / 2X: ...<br>
    Over 2.5: @ / Under 2.5: @<br>
    BTTS Yes: @ / No: @</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="sidebar-section"><h4>📊 SESSION STATS</h4>', unsafe_allow_html=True)
    st.markdown(f'<p>Pesan: {len(st.session_state.messages)}<br>Token: ~{st.session_state.total_tokens:,}</p></div>', unsafe_allow_html=True)

    # Clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0; color: #374151; font-size: 0.7rem;">
        Powered by Claude claude-sonnet-4-5<br>
        Master Prompt v5.3.1
    </div>
    """, unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚽ SISTEM ANALISIS PROBABILITAS SEPAK BOLA</h1>
    <p>Analisis berbasis statistik & matematis adaptif — Data real dari web search</p>
    <div>
        <span class="badge badge-green">v5.3.1 STABLE</span>
        <span class="badge badge-cyan">VIG STRIPPED</span>
        <span class="badge badge-purple">GF/GA ENGINE</span>
        <span class="badge badge-green">DRAW FORMULA</span>
        <span class="badge badge-cyan">AH ENGINE</span>
        <span class="badge badge-purple">ANTI-HALLUCINATION</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Status bar
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    api_status = "🟢 API Connected" if api_key else "🔴 API Key Required"
    st.markdown(f'<div class="status-bar">{api_status}</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="status-bar">📋 Mode: {mode.upper()}</div>', unsafe_allow_html=True)
with col3:
    msg_count = len(st.session_state.messages)
    tahap = "Tahap 2 Ready" if msg_count > 1 else "Tahap 1 — Input Match"
    st.markdown(f'<div class="status-bar">🔄 {tahap}</div>', unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #374151;">
            <div style="font-size:3rem; margin-bottom:16px;">⚽</div>
            <div style="font-family:'IBM Plex Mono',monospace; color:#c8f74a; font-size:1rem; font-weight:700; margin-bottom:8px;">SIAP MENERIMA INPUT</div>
            <div style="color:#6b7280; font-size:0.85rem; line-height:1.8; max-width:480px; margin:0 auto;">
                Berikan nama match, liga, tanggal, dan odds single market.<br>
                Sistem akan analisis data real dari web, lalu berikan combo potensial.<br>
                Odds combo diminta setelah Tahap 1 selesai.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                content = msg["content"].replace("\n", "<br>").replace("|", "&#124;")
                st.markdown(f'<div class="chat-assistant">🤖 {content}</div>', unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([6, 1])
    with col_input:
        user_input = st.text_area(
            "Input",
            placeholder="Contoh: Manchester City vs Arsenal | Liga: Premier League | 10-05-2026\n1X2: 2.1 / 3.4 / 3.6 | 1X: 1.35 / 2X: 1.72\nOver 2.5: @1.82 Under 2.5: @1.95 | BTTS Yes: @1.75 No: @2.05",
            height=100,
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("ANALISIS →", use_container_width=True)

# ── Quick actions ─────────────────────────────────────────────
col_a, col_b, col_c, col_d = st.columns(4)
quick_action = None
with col_a:
    if st.button("⚡ Compact Mode", use_container_width=True):
        quick_action = "compact"
with col_b:
    if st.button("📋 Full Mode", use_container_width=True):
        quick_action = "full"
with col_c:
    if st.button("🎯 Best Pick", use_container_width=True):
        quick_action = "best pick"
with col_d:
    if st.button("🔍 Audit Data", use_container_width=True):
        quick_action = "audit data"

# ── Process input ─────────────────────────────────────────────
def get_response(messages, api_key, mode):
    client = anthropic.Anthropic(api_key=api_key)

    # Inject mode into system if not mentioned
    system = SYSTEM_PROMPT
    if mode != "full":
        system += f"\n\nCATATAN: User telah memilih mode {mode.upper()} dari UI. Gunakan mode ini untuk output kecuali user secara eksplisit meminta mode lain."

    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
    ]

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        system=system,
        messages=api_messages,
    )
    return response.content[0].text, response.usage.input_tokens + response.usage.output_tokens


def handle_send(text):
    if not api_key:
        st.error("⚠️ Masukkan Anthropic API Key di sidebar terlebih dahulu.")
        return
    if not text.strip():
        return

    st.session_state.messages.append({"role": "user", "content": text.strip()})

    with st.spinner("🔍 Mencari data & menganalisis..."):
        try:
            reply, tokens = get_response(st.session_state.messages, api_key, st.session_state.output_mode)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.total_tokens += tokens
        except anthropic.AuthenticationError:
            st.error("❌ API Key tidak valid. Periksa kembali di sidebar.")
            st.session_state.messages.pop()
        except anthropic.RateLimitError:
            st.error("⏳ Rate limit tercapai. Tunggu sebentar lalu coba lagi.")
            st.session_state.messages.pop()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.messages.pop()

    st.rerun()


if submit and user_input.strip():
    handle_send(user_input)

if quick_action:
    handle_send(quick_action)

# ── Disclaimer ────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 20px 0 8px 0; color: #374151; font-size: 0.72rem; font-family:'IBM Plex Mono',monospace;">
⚠️ DISCLAIMER: Analisis berbasis statistik historis & data real-time. Tidak ada jaminan kemenangan mutlak. Bertaruhlah dengan bertanggung jawab.
</div>
""", unsafe_allow_html=True)
