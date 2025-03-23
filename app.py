import streamlit as st
import requests
import json
from datetime import datetime
import os

# Constants
API_URL = "http://localhost:8000"  # FastAPI backend URL

# Configure page
st.set_page_config(
    page_title="arXiv Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Functions to interact with the backend API
def fetch_papers_by_author(author_id, max_results=50):
    """Fetch papers by author ID from the backend API"""
    try:
        response = requests.post(
            f"{API_URL}/papers/by-author",
            json={"author_id": author_id, "max_results": max_results}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return {"success": False, "papers": [], "error": str(e)}

def fetch_daily_papers(categories=None, date_range=None):
    """Fetch daily submissions with optional filtering"""
    try:
        if not categories:
            categories = []
            
        response = requests.post(
            f"{API_URL}/papers/daily",
            json={"categories": categories, "date_range": date_range}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return {"success": False, "papers": [], "error": str(e)}

def get_user_profile(user_id):
    """Get stored user profile from the backend"""
    try:
        response = requests.get(f"{API_URL}/profile/{user_id}")
        return response.json()
    except Exception as e:
        st.error(f"Error retrieving profile: {e}")
        return {"success": False, "profile": None}

def save_user_profile(profile_data):
    """Save user profile to the backend"""
    try:
        response = requests.post(
            f"{API_URL}/profile",
            json=profile_data
        )
        return response.json()
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return {"success": False}

def format_date(date_str):
    """Format date string to a more readable format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def render_paper_card(paper):
    """Render a paper in a nice card format"""
    with st.expander(paper["title"]):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show authors
            st.write("**Authors:** " + ", ".join(paper["authors"]))
            
            # Show dates in a more prominent way
            dates_html = ""
            
            if "published" in paper and paper["published"]:
                pub_date = format_date(paper["published"])
                dates_html += f"<span style='color: #1e88e5'><strong>Published:</strong> {pub_date}</span>"
            
            if "updated" in paper and paper["updated"]:
                upd_date = format_date(paper["updated"])
                dates_html += f" <span style='color: #43a047'><strong>Updated:</strong> {upd_date}</span>" if dates_html else f"<span style='color: #43a047'><strong>Updated:</strong> {upd_date}</span>"
            
            if dates_html:
                st.markdown(dates_html, unsafe_allow_html=True)
            
            # Show categories if available with better formatting
            if "categories" in paper and paper["categories"]:
                st.markdown("**Categories:**")
                categories_html = ""
                for cat in paper["categories"]:
                    categories_html += f"<span style='background-color: #f1f8ff; padding: 2px 6px; border-radius: 4px; margin-right: 5px;'>{cat}</span>"
                st.markdown(categories_html, unsafe_allow_html=True)
        
        with col2:
            # Add buttons for PDF and arXiv links
            if "pdf_url" in paper and paper["pdf_url"]:
                st.markdown(f"[📄 Read PDF]({paper['pdf_url']})")
            
            if "id" in paper and paper["id"]:
                st.markdown(f"[🔗 View on arXiv]({paper['id']})")
                
            # Placeholder for future citation info
            # st.markdown("**Citations:** Not available")
        
        # Show abstract
        st.markdown("**Abstract:**")
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>{paper['summary']}</div>", unsafe_allow_html=True)

# Main app
def main():
    # Sidebar for navigation and user profile
    with st.sidebar:
        st.title("arXiv Agent")
        
        # Simple user identification (for saving preferences)
        user_id = st.text_input("Your Name/ID (for storing preferences):")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio("Go to", ["Author Search", "Daily Papers", "My Profile"])
        
        # Show arXiv categories in sidebar
        st.subheader("Popular arXiv Categories")
        st.write("CS Categories:")
        st.write("- cs.AI: Artificial Intelligence")
        st.write("- cs.CL: Computation and Language")
        st.write("- cs.CV: Computer Vision")
        st.write("- cs.LG: Machine Learning")
        
    # Main content
    if page == "Author Search":
        st.title("Search by Author")
        author_id = st.text_input("Enter arXiv Author ID or Name:")
        max_results = st.slider("Maximum number of papers", 5, 100, 25)
        
        if st.button("Search") and author_id:
            with st.spinner("Fetching papers..."):
                result = fetch_papers_by_author(author_id, max_results)
                
                if result.get("success", False):
                    papers = result.get("papers", [])
                    st.success(f"Found {len(papers)} papers by {author_id}")
                    
                    # Add sorting options
                    st.subheader("Sort Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sort_by = st.selectbox(
                            "Sort by:",
                            ["Published Date", "Updated Date", "Title"],
                            index=0
                        )
                    
                    with col2:
                        sort_order = st.radio(
                            "Order:",
                            ["Newest First", "Oldest First"] if "Date" in sort_by else ["A-Z", "Z-A"],
                            horizontal=True
                        )
                    
                    # Future enhancement for citation count sorting
                    # This would require connecting to an external citation database
                    citation_sorting = st.checkbox("Show citation count sorting (future enhancement)", value=False)
                    if citation_sorting:
                        st.info("""
                        Citation count sorting will be available in a future update. This requires:
                        1. Integration with a citation database (Semantic Scholar, CrossRef, Google Scholar, etc.)
                        2. API key setup and rate limiting
                        3. Cache for citation data to avoid excessive API calls
                        """)
                    
                    # Sort the papers based on selection
                    if sort_by == "Published Date":
                        # Convert date strings to datetime for proper sorting
                        try:
                            papers = sorted(
                                papers,
                                key=lambda x: datetime.strptime(x.get("published", "1900-01-01"), "%Y-%m-%dT%H:%M:%SZ"),
                                reverse=(sort_order == "Newest First")
                            )
                        except Exception as e:
                            st.warning(f"Some papers may have invalid date formats. Basic sorting applied.")
                            # Fallback sorting if date parsing fails
                            papers = sorted(
                                papers,
                                key=lambda x: x.get("published", ""),
                                reverse=(sort_order == "Newest First")
                            )
                            
                    elif sort_by == "Updated Date":
                        try:
                            papers = sorted(
                                papers,
                                key=lambda x: datetime.strptime(x.get("updated", "1900-01-01"), "%Y-%m-%dT%H:%M:%SZ"),
                                reverse=(sort_order == "Newest First")
                            )
                        except Exception as e:
                            # Fallback sorting
                            papers = sorted(
                                papers,
                                key=lambda x: x.get("updated", ""),
                                reverse=(sort_order == "Newest First")
                            )
                    
                    elif sort_by == "Title":
                        papers = sorted(
                            papers,
                            key=lambda x: x.get("title", "").lower(),
                            reverse=(sort_order == "Z-A")
                        )
                    
                    # Future enhancement placeholder for citation count
                    # elif sort_by == "Citation Count":
                    #     papers = sorted(papers, key=lambda x: x.get("citation_count", 0), 
                    #                     reverse=(sort_order == "Highest First"))
                    
                    # Display papers with a counter
                    for i, paper in enumerate(papers, 1):
                        st.write(f"**Paper {i} of {len(papers)}**")
                        render_paper_card(paper)
                        st.markdown("---")
                else:
                    st.error("Failed to fetch papers. Please try again.")
                    
    elif page == "Daily Papers":
        st.title("Daily arXiv Submissions")
        
        # Category selection
        st.subheader("Filter by Categories")
        categories = []
        cols = st.columns(2)
        
        with cols[0]:
            if st.checkbox("Artificial Intelligence (cs.AI)"):
                categories.append("cs.AI")
            if st.checkbox("Computer Vision (cs.CV)"):
                categories.append("cs.CV")
                
        with cols[1]:
            if st.checkbox("Machine Learning (cs.LG)"):
                categories.append("cs.LG")
            if st.checkbox("Computation and Language (cs.CL)"):
                categories.append("cs.CL")
                
        custom_category = st.text_input("Add other category (e.g., stat.ML):")
        if custom_category:
            categories.append(custom_category)
            
        # Fetch papers
        if st.button("Get Latest Papers"):
            with st.spinner("Fetching latest submissions..."):
                result = fetch_daily_papers(categories)
                
                if result.get("success", False):
                    papers = result.get("papers", [])
                    st.success(f"Found {len(papers)} recent papers")
                    
                    # Display papers
                    for paper in papers:
                        render_paper_card(paper)
                        st.markdown("---")
                else:
                    st.error("Failed to fetch papers. Please try again.")
    
    elif page == "My Profile":
        st.title("My Research Profile")
        
        if not user_id:
            st.warning("Please enter your name/ID in the sidebar to use this feature.")
        else:
            # Fetch existing profile
            profile_result = get_user_profile(user_id)
            profile = profile_result.get("profile", {})
            
            # Research interests
            st.subheader("Research Interests")
            interests_text = st.text_area(
                "Enter your research interests (one per line):",
                value="\n".join(profile.get("interests", []))
            )
            interests = [i.strip() for i in interests_text.split("\n") if i.strip()]
            
            # Favorite authors
            st.subheader("Favorite Authors")
            authors_text = st.text_area(
                "Enter favorite authors (one per line):",
                value="\n".join(profile.get("favorite_authors", []))
            )
            favorite_authors = [a.strip() for a in authors_text.split("\n") if a.strip()]
            
            # Save profile
            if st.button("Save Profile"):
                profile_data = {
                    "user_id": user_id,
                    "interests": interests,
                    "favorite_authors": favorite_authors,
                    "saved_papers": profile.get("saved_papers", [])
                }
                
                save_result = save_user_profile(profile_data)
                if save_result.get("success", False):
                    st.success("Profile saved successfully!")
                else:
                    st.error("Failed to save profile.")

if __name__ == "__main__":
    main()