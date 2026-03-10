# vietnam_food_app.py
import streamlit as st
import pandas as pd

# Load the database
@st.cache_data
def load_data():
    return pd.read_csv('vietnamese_foods.csv')

df = load_data()

# App title
st.title("🍜 Vietnam Food Identifier")
st.caption("See a dish? Type the Vietnamese name from the menu")

# ============================================
# TAB 1: IDENTIFY BY NAME (what you actually need)
# ============================================
tab1, tab2, tab3 = st.tabs(["🔍 Find by Name", "📝 Describe It", "📚 Browse All"])

with tab1:
    st.subheader("What's the Vietnamese name on the menu?")
    
    # Search box
    search = st.text_input("Type the name:", placeholder="e.g., Phở, Bún Chả, Cao Lầu")
    
    if search:
        # Search in Vietnamese name column
        results = df[df['vietnamese_name'].str.contains(search, case=False, na=False)]
        
        if not results.empty:
            for _, dish in results.iterrows():
                with st.container():
                    st.markdown(f"### {dish['vietnamese_name']}")
                    st.markdown(f"*{dish['english_name']}*")
                    st.markdown(f"**Type:** {dish['type']} | **Region:** {dish['region']}")
                    
                    st.markdown("**What it is:**")
                    st.write(dish['description'])
                    
                    st.markdown("**🥢 How to eat it:**")
                    st.info(dish['how_to_eat'])
                    
                    with st.expander("📝 Ingredients"):
                        st.write(dish['ingredients'])
                    
                    with st.expander("💡 Fun fact"):
                        st.caption(dish['fun_fact'])
                    
                    st.divider()
        else:
            st.warning(f"No dish found with '{search}'. Try another name or browse below.")

with tab2:
    st.subheader("Describe what you see")
    desc = st.text_area("What does it look like?", placeholder="e.g., 'noodle soup with beef, clear broth'")
    
    if st.button("Find matching dishes"):
        if desc:
            # Simple keyword search in description
            matches = df[df['description'].str.contains(desc[:20], case=False, na=False)]
            if not matches.empty:
                st.success(f"Found {len(matches)} possible dishes")
                for _, dish in matches.head(5).iterrows():
                    st.markdown(f"**{dish['vietnamese_name']}** - {dish['english_name']}")
                    st.write(dish['description'][:150] + "...")
                    st.caption(f"🥢 {dish['how_to_eat'][:100]}...")
                    st.divider()
            else:
                st.info("No matches. Try different words or browse all dishes.")

with tab3:
    st.subheader("Browse all dishes")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        regions = ['All'] + sorted(df['region'].unique().tolist())
        region = st.selectbox("Filter by region", regions)
    with col2:
        types = ['All'] + sorted(df['type'].unique().tolist())
        dish_type = st.selectbox("Filter by type", types)
    
    # Apply filters
    filtered = df.copy()
    if region != 'All':
        filtered = filtered[filtered['region'] == region]
    if dish_type != 'All':
        filtered = filtered[filtered['type'] == dish_type]
    
    st.write(f"Showing {len(filtered)} dishes")
    
    # Show in expanders
    for _, dish in filtered.iterrows():
        with st.expander(f"{dish['vietnamese_name']} - {dish['english_name']}"):
            st.write(dish['description'])
            st.caption(f"🥢 {dish['how_to_eat']}")
