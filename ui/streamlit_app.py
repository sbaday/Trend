"""
Streamlit Dashboard — POD Trend Engine
"""

import sys
import os
import json
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.database import init_db, get_top_trends, get_outputs_for_trend, insert_output, DB_PATH

# ── Sayfa ayarları ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="POD Trend Engine",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .score-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }
    .high   { background: #d1fae5; color: #065f46; }
    .medium { background: #fef3c7; color: #92400e; }
    .low    { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔥 Trend Engine")
    st.caption("POD Trend Intelligence")

    st.divider()

    min_score = st.slider("Min. Trend Skoru", 0.0, 10.0, 0.0, 0.5)
    niche_filter = st.multiselect(
        "Niş Filtresi",
        ["funny", "gaming", "fitness", "outdoor", "cats", "dogs", "programmer", "eid", "general"],
        default=[]
    )
    
    if st.button("🔄 Önbelleği Temizle"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption(f"📂 DB: `{DB_PATH}`")
    try:
        conn = sqlite3.connect(DB_PATH)
        counts = conn.execute("SELECT (SELECT COUNT(*) FROM signals), (SELECT COUNT(*) FROM trends WHERE analyzed=1)").fetchone()
        st.caption(f"📊 Sinyal: {counts[0]} | Analiz: {counts[1]}")
        conn.close()
    except:
        st.caption("⚠️ DB Bağlantı Hatası")

    st.divider()

    st.subheader("Pipeline Çalıştır")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Topla", use_container_width=True):
            with st.spinner("Reddit + Google Trends..."):
                try:
                    from collectors.reddit_rss import collect as collect_reddit
                    from collectors.hackernews import collect as collect_hn
                    n1 = collect_reddit(verbose=False)
                    nh = collect_hn(verbose=False)
                    st.success(f"✓ {n1+nh} trend")
                except Exception as e:
                    st.error(str(e))
    with col2:
        if st.button("🤖 Analiz", use_container_width=True):
            with st.spinner("Gemini analiz ediyor..."):
                try:
                    from analyzer.gemini_scoring import analyze_batch
                    n = analyze_batch(verbose=False)
                    st.success(f"✓ {n} analiz")
                except Exception as e:
                    st.error(str(e))

    if st.button("🎨 İçerik Üret", use_container_width=True):
        with st.spinner("Listing + prompt üretiliyor..."):
            try:
                from generator.generators import run_output_pipeline
                n = run_output_pipeline(verbose=False)
                st.success(f"✓ {n} içerik")
            except Exception as e:
                st.error(str(e))


# ── Veri yükle ────────────────────────────────────────────────────────────────
init_db()


@st.cache_data(ttl=60)
def load_data(min_s, niches):
    rows = get_top_trends(limit=200, min_score=min_s)
    cols = ["id", "phrase", "source", "subreddit", "trend_score", "niche",
            "humor", "identity", "giftability", "design", "created_at"]
    df = pd.DataFrame(rows, columns=cols)
    if niches:
        df = df[df["niche"].isin(niches)]
    return df


df = load_data(min_score, niche_filter)

# ── Üst metrikler ─────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Toplam Trend", len(df))
m2.metric("Ort. Skor",    f"{df['trend_score'].mean():.1f}" if not df.empty else "–")
m3.metric("🔥 Üstün (8+)", int((df["trend_score"] >= 8).sum()))
m4.metric("Nişler",        df["niche"].nunique() if not df.empty else 0)

st.divider()

# ── Sekmeler ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Trend Feed", "🎨 Ürün Üretici", "📈 Haftalık Rapor"])


# ── TAB 1: Trend Feed ─────────────────────────────────────────────────────────
with tab1:
    if df.empty:
        st.info("Henüz analiz edilmiş trend yok. Sidebar'dan pipeline başlat.")
    else:
        # Arama
        search = st.text_input("🔍 Phrase ara", "")
        display_df = df[df["phrase"].str.contains(search, case=False)] if search else df

        for _, row in display_df.head(40).iterrows():
            score = row["trend_score"]
            badge_class = "high" if score >= 8 else ("medium" if score >= 7 else "low")

            with st.container():
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    st.markdown(f"**{row['phrase']}**")
                    st.caption(f"📍 {row['source']} / {row['subreddit'] or '–'} · {row['niche']}")
                with c2:
                    st.markdown(
                        f"<span class='score-badge {badge_class}'>{score:.1f}</span>",
                        unsafe_allow_html=True
                    )
                with c3:
                    if st.button("Üret", key=f"gen_{row['id']}"):
                        st.session_state["selected_trend"] = row.to_dict()
                        st.session_state["active_tab"] = "generator"
                st.divider()


# ── TAB 2: Ürün Üretici ───────────────────────────────────────────────────────
with tab2:
    st.subheader("Ürün İçeriği Üretici")

    if not df.empty:
        selected_phrase = st.selectbox(
            "Trend seç",
            df["phrase"].tolist(),
            index=0
        )
        selected_row = df[df["phrase"] == selected_phrase].iloc[0]
        trend_id = int(selected_row["id"])

        col_info, col_scores = st.columns([3, 2])
        with col_info:
            st.info(f"**Niş:** {selected_row['niche']}  |  **Kaynak:** {selected_row['source']}")
        with col_scores:
            st.write(f"😂 Mizah: `{selected_row['humor']:.0f}`  "
                     f"👥 Kimlik: `{selected_row['identity']:.0f}`  "
                     f"🎁 Hediye: `{selected_row['giftability']:.0f}`  "
                     f"✏️ Tasarım: `{selected_row['design']:.0f}`")

        # Mevcut çıktıları göster
        outputs = get_outputs_for_trend(trend_id)
        if outputs:
            for output_type, content, created_at in outputs:
                st.subheader({
                    "design_prompt":  "🎨 Tasarım Promptu",
                    "etsy_listing":   "🛒 Etsy Listing",
                    "social_content": "📱 Sosyal İçerik",
                }.get(output_type, output_type))

                if output_type == "design_prompt":
                    st.code(content, language=None)
                else:
                    try:
                        data = json.loads(content)
                        if output_type == "etsy_listing":
                            st.write(f"**Başlık:** {data.get('title','')}")
                            st.write(f"**Açıklama:** {data.get('description','')}")
                            tags = data.get("tags", [])
                            st.write("**Taglar:** " + " · ".join([f"`{t}`" for t in tags]))
                        elif output_type == "social_content":
                            st.write(f"**TikTok:** {data.get('tiktok_hook','')}")
                            st.write(f"**Pinterest:** {data.get('pinterest_title','')}")
                            st.write(f"**Instagram:** {data.get('instagram_caption','')}")
                    except Exception:
                        st.text(content)
        else:
            st.warning("Bu trend için henüz içerik üretilmemiş.")
            if st.button("🚀 Şimdi Üret"):
                with st.spinner("Gemini içerik üretiyor..."):
                    try:
                        from generator.generators import (
                            generate_design_prompt,
                            generate_etsy_listing,
                            generate_social_content,
                        )
                        from google import genai
                        from dotenv import load_dotenv
                        load_dotenv()
                        import os
                        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                        niche = selected_row["niche"]
                        
                        dp = generate_design_prompt(selected_phrase, niche, client)
                        insert_output(trend_id, "design_prompt", dp)

                        listing = generate_etsy_listing(selected_phrase, niche, client)
                        insert_output(trend_id, "etsy_listing", json.dumps(listing, ensure_ascii=False))

                        social = generate_social_content(selected_phrase, niche, client)
                        insert_output(trend_id, "social_content", json.dumps(social, ensure_ascii=False))

                        st.success("✓ İçerik üretildi!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    else:
        st.info("Önce pipeline'ı çalıştırıp trend topla.")


# ── TAB 3: Haftalık Rapor ─────────────────────────────────────────────────────
with tab3:
    if df.empty:
        st.info("Veri yok.")
    else:
        col_l, col_r = st.columns(2)

        with col_l:
            st.subheader("Niş Dağılımı")
            niche_counts = df.groupby("niche").size().reset_index(name="count")
            fig1 = px.bar(niche_counts, x="niche", y="count",
                          color="count", color_continuous_scale="Viridis")
            fig1.update_layout(showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)

        with col_r:
            st.subheader("Skor Dağılımı")
            fig2 = px.histogram(df, x="trend_score", nbins=20,
                                color_discrete_sequence=["#6366f1"])
            fig2.update_layout(margin=dict(t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Top 10 Trend Bu Hafta")
        top10 = df.nlargest(10, "trend_score")[["phrase", "niche", "trend_score", "humor", "identity"]]
        st.dataframe(top10, use_container_width=True, hide_index=True)

        # CSV export
        st.subheader("Etsy Bulk Upload CSV")
        conn = sqlite3.connect(DB_PATH)
        export_rows = []
        for _, row in df[df["trend_score"] >= 7.5].head(50).iterrows():
            outputs = get_outputs_for_trend(int(row["id"]))
            listing = next((o for o in outputs if o[0] == "etsy_listing"), None)
            if listing:
                try:
                    data = json.loads(listing[1])
                    export_rows.append({
                        "title":       data.get("title", ""),
                        "description": data.get("description", ""),
                        "tags":        ",".join(data.get("tags", [])),
                        "price":       "19.99",
                        "sku":         f"POD-{row['id']}",
                    })
                except Exception:
                    pass
        conn.close()

        if export_rows:
            export_df = pd.DataFrame(export_rows)
            csv = export_df.to_csv(index=False)
            st.download_button(
                "⬇️ CSV İndir (Etsy Upload)",
                data=csv,
                file_name="etsy_listings.csv",
                mime="text/csv",
            )
        else:
            st.caption("Export için önce içerik üret (skor >= 7.5).")
