# ===============================
# 1. IMPORT LIBRARIES
# ===============================
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("🌾 Advanced Crop Yield & Climate Dashboard")

# ===============================
# 2. LOAD DATA
# ===============================
df = pd.read_csv("final_df.csv")
gdf = gpd.read_file("ap_only.shp")

# ===============================
# 3. DISTRICT MAPPING (ENCODED → NAME)
# ===============================
district_map = {
    0: "Anantapur",
    1: "Kurnool",
    2: "Kadapa",
    3: "Chittoor",
    4: "Nellore",
    5: "Prakasam",
    6: "Guntur",
    7: "Krishna",
    8: "West Godavari",
    9: "East Godavari",
    10: "Visakhapatnam",
    11: "Srikakulam"
}

df["District_Name"] = df["District"].map(district_map)

# ===============================
# 4. FIX DISTRICT NAME MISMATCH
# ===============================
df["District_Name"] = df["District_Name"].replace({
    "Kadapa": "Y.S.R.",
    "Nellore": "Sri Potti Sriramulu Nellore"
})

df["District_Name"] = df["District_Name"].str.strip()

# ===============================
# 5. CLIMATE ZONE MAPPING
# ===============================
zone_data = {
    "Srikakulam": "North Coastal Zone",
    "Vizianagaram": "North Coastal Zone",
    "Visakhapatnam": "North Coastal Zone",
    "East Godavari": "Krishna-Godavari Delta Zone",
    "West Godavari": "Krishna-Godavari Delta Zone",
    "Krishna": "Krishna-Godavari Delta Zone",
    "Guntur": "Krishna-Godavari Delta Zone",
    "Prakasam": "Southern Zone",
    "Chittoor": "Southern Zone",
    "Sri Potti Sriramulu Nellore": "Southern Zone",
    "Anantapur": "Scarce Rainfall Zone",
    "Kurnool": "Scarce Rainfall Zone",
    "Y.S.R.": "High Altitude & Tribal Zone"
}

df["Climate_Name"] = df["District_Name"].map(zone_data)

# ✅ FIX: Replace missing with High Altitude & Tribal Zone
df["Climate_Name"] = df["Climate_Name"].fillna("High Altitude & Tribal Zone")

# ===============================
# 6. CLEAN SHAPEFILE
# ===============================
gdf["District_Name"] = gdf["DISTRICT"].str.strip()

# ===============================
# 7. SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

districts = st.sidebar.multiselect(
    "District",
    df["District_Name"].dropna().unique(),
    default=df["District_Name"].dropna().unique()
)

seasons = st.sidebar.multiselect(
    "Season",
    df["SEASON"].unique(),
    default=df["SEASON"].unique()
)

filtered_df = df[
    (df["District_Name"].isin(districts)) &
    (df["SEASON"].isin(seasons))
]

# ===============================
# 8. KPI METRICS
# ===============================
col1, col2, col3 = st.columns(3)

col1.metric("🌾 Avg Yield", round(filtered_df["Crop_Yield_ton_per_hectare"].mean(), 2))
col2.metric("🌧️ Avg Rainfall", round(filtered_df["LOCAL_RAIN_MM"].mean(), 2))
col3.metric("🌡️ Avg Temp", round(filtered_df["LOCAL_TMAX_C"].mean(), 2))

# ===============================
# 9. MAP (INTERACTIVE)
# ===============================
st.subheader("🗺️ Climate Zone Map")

map_df = filtered_df.groupby("District_Name")["Climate_Name"].first().reset_index()
merged = gdf.merge(map_df, on="District_Name", how="left")

# ✅ FIX HERE ALSO
merged["Climate_Name"] = merged["Climate_Name"].fillna("High Altitude & Tribal Zone")

fig_map = px.choropleth(
    merged,
    geojson=merged.geometry,
    locations=merged.index,
    color="Climate_Name",
)

fig_map.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig_map, use_container_width=True)

# ===============================
# 10. ORDER FOR CONSISTENCY
# ===============================
zone_order = [
    "Scarce Rainfall Zone",
    "Southern Zone",
    "North Coastal Zone",
    "Krishna-Godavari Delta Zone",
    "High Altitude & Tribal Zone"
]

# ===============================
# 11. YIELD VS CLIMATE
# ===============================
st.subheader("📊 Yield vs Climate Zone")

fig_box = px.box(
    filtered_df,
    x="Climate_Name",
    y="Crop_Yield_ton_per_hectare",
    color="Climate_Name",
    category_orders={"Climate_Name": zone_order}
)

st.plotly_chart(fig_box, use_container_width=True)

# ===============================
# 12. CORRELATION ANALYSIS
# ===============================
st.subheader("📈 Correlation Analysis")

numeric_cols = filtered_df.select_dtypes(include='number').columns

selected_features = st.multiselect(
    "Select Features",
    numeric_cols,
    default=list(numeric_cols[:6])
)

corr = filtered_df[selected_features].corr()

fig_corr = px.imshow(
    corr,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig_corr, use_container_width=True)

# ===============================
# 13. SEASONAL ANALYSIS
# ===============================
st.subheader("🌾 Season vs Yield")

fig_season = px.bar(
    filtered_df,
    x="SEASON",
    y="Crop_Yield_ton_per_hectare",
    color="SEASON"
)

st.plotly_chart(fig_season, use_container_width=True)

# ===============================
# 14. RAINFALL VS YIELD
# ===============================
st.subheader("🌧️ Rainfall vs Yield")

fig_scatter = px.scatter(
    filtered_df,
    x="LOCAL_RAIN_MM",
    y="Crop_Yield_ton_per_hectare",
    color="Climate_Name",
    hover_data=["District_Name"]
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.success("Dashboard Ready ✅")