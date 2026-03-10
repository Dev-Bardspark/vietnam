# vietnam_food_app.py
import streamlit as st
import pandas as pd
from PIL import Image
import openai
import io
import base64

# Page config
st.set_page_config(
    page_title="Vietnam Food Identifier",
    page_icon="🍜",
    layout="centered"
)

# Load the database
@st.cache_data
def load_data():
    df = pd.read_csv('vietnamese_foods.csv')
    df = df.fillna('')
    return df

df = load_data()

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    # New client initialization (no proxies argument)
    client = openai.OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )
    return client

# App title
st.title("🍜 Vietnam Food Identifier")
st.caption("Take a photo or type the Vietnamese name from the menu")

# ============================================
# TAB 1: CAMERA IDENTIFICATION (with GPT-4o mini)
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["📸 Camera ID", "🔍 Find by Name", "📝 Describe It", "📚 Browse All"])

with tab1:
    st.subheader("📸 Take a photo of the dish")
    st.caption("GPT-4o mini will identify it instantly")
    
    # Camera input
    img_file = st.camera_input("Point and shoot", key="camera")
    
    if img_file is not None:
        # Display the image
        image = Image.open(img_file)
        st.image(image, caption="Your mystery dish", use_column_width=True)
        
        if st.button("🔍 What is this dish?", type="primary"):
            with st.spinner("AI is analyzing your photo..."):
                try:
                    # Convert image to base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Get OpenAI client
                    client = get_openai_client()
                    
                    # Call GPT-4o mini vision
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text", 
                                        "text": "What Vietnamese dish is this? Reply with ONLY the Vietnamese name. Examples: Phở, Bún Chả, Cao Lầu, Bánh Xèo, etc."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=50
                    )
                    
                    # Get the Vietnamese name from AI
                    vietnamese_name = response.choices[0].message.content.strip()
                    
                    # Look it up in our database
                    dish_match = df[df['vietnamese_name'].str.contains(vietnamese_name, case=False, na=False)]
                    
                    if not dish_match.empty:
                        dish = dish_match.iloc[0]
                        
                        # Show success
                        st.success(f"✅ Identified: {dish['vietnamese_name']}")
                        
                        # Display dish info
                        with st.container():
                            st.markdown(f"### {dish['vietnamese_name']}")
                            st.markdown(f"*{dish['english_name']}*")
                            st.markdown(f"**Type:** {dish['type']} | **Region:** {dish['region']}")
                            
                            st.markdown("**What it is:**")
                            st.write(dish['description'])
                            
                            # THE IMPORTANT PART - How to eat it
                            st.markdown("**🥢 How to eat it:**")
                            st.info(dish['how_to_eat'])
                            
                            with st.expander("📝 Ingredients"):
                                st.write(dish['ingredients'])
                            
                            with st.expander("💡 Fun fact"):
                                st.caption(dish['fun_fact'])
                    else:
                        st.warning(f"AI identified '{vietnamese_name}' but it's not in our database. Add it?")
                        st.write("AI response:", vietnamese_name)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Make sure your OpenAI API key is set correctly in secrets")

# ============================================
# TAB 2: FIND BY NAME
# ============================================
with tab2:
    st.subheader("🔍 Find by Vietnamese name")
    st.caption("Type what's on the menu")
    
    search = st.text_input("Search:", placeholder="e.g., Phở, Bún Chả, Cao Lầu")
    
    if search:
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
            st.warning(f"No dish found with '{search}'")

# ============================================
# TAB 3: DESCRIBE IT
# ============================================
with tab3:
    st.subheader("📝 Describe what you see")
    desc = st.text_area("What does it look like?", 
                       placeholder="e.g., 'noodle soup with beef, clear broth, green onions'",
                       height=100)
    
    if st.button("Find matching dishes"):
        if desc:
            # Search in description and name
            matches = df[df['description'].str.contains(desc[:30], case=False, na=False) | 
                        df['english_name'].str.contains(desc[:30], case=False, na=False)]
            
            if not matches.empty:
                st.success(f"Found {len(matches)} possible dishes")
                for _, dish in matches.head(5).iterrows():
                    st.markdown(f"**{dish['vietnamese_name']}** - {dish['english_name']}")
                    st.write(dish['description'][:150] + "...")
                    st.caption(f"🥢 {dish['how_to_eat'][:100]}...")
                    st.divider()
            else:
                st.info("No matches found")

# ============================================
# TAB 4: BROWSE ALL
# ============================================
with tab4:
    st.subheader("📚 Browse all dishes")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        regions = ['All'] + sorted([r for r in df['region'].unique().tolist() if r])
        region = st.selectbox("Filter by region", regions)
    with col2:
        types = ['All'] + sorted([t for t in df['type'].unique().tolist() if t])
        dish_type = st.selectbox("Filter by type", types)
    
    # Search
    search_all = st.text_input("Search all dishes:", placeholder="Type any keyword...")
    
    # Apply filters
    filtered = df.copy()
    if region != 'All':
        filtered = filtered[filtered['region'] == region]
    if dish_type != 'All':
        filtered = filtered[filtered['type'] == dish_type]
    if search_all:
        filtered = filtered[filtered['vietnamese_name'].str.contains(search_all, case=False, na=False) | 
                           filtered['english_name'].str.contains(search_all, case=False, na=False) |
                           filtered['description'].str.contains(search_all, case=False, na=False)]
    
    st.write(f"Showing {len(filtered)} dishes")
    
    # Display in expanders
    for _, dish in filtered.iterrows():
        with st.expander(f"{dish['vietnamese_name']} - {dish['english_name']}"):
            st.write(dish['description'][:200] + "...")
            st.caption(f"🥢 {dish['how_to_eat'][:100]}...")
