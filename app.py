import streamlit as st
import requests
import json
from datetime import datetime
import os
from pathlib import Path

# Constants
API_URL = "http://localhost:8000"  # FastAPI backend URL
SEARCH_HISTORY_FILE = Path("data/user_data/search_history.json")
CATEGORIES_FILE = Path("data/user_data/categories.json")

# Create directory if it doesn't exist
SEARCH_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# Function to load search history from file
def load_search_history():
    if SEARCH_HISTORY_FILE.exists():
        try:
            with open(SEARCH_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading search history: {e}")
    return []

# Function to save search history to file
def save_search_history(history):
    try:
        with open(SEARCH_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving search history: {e}")

# Function to load categories from file
def load_categories():
    if CATEGORIES_FILE.exists():
        try:
            with open(CATEGORIES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading categories: {e}")
            return {"default_categories": [], "custom_categories": []}
    else:
        # Create default categories file if it doesn't exist
        default_data = {
            "default_categories": [
                {"code": "cs.AI", "name": "Artificial Intelligence"},
                {"code": "cs.CL", "name": "Computation and Language"},
                {"code": "cs.CV", "name": "Computer Vision"},
                {"code": "cs.LG", "name": "Machine Learning"}
            ],
            "custom_categories": []
        }
        save_categories(default_data)
        return default_data

# Function to save categories to file
def save_categories(categories_data):
    try:
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(categories_data, f, indent=2)
    except Exception as e:
        print(f"Error saving categories: {e}")

# Initialize session state variables if they don't exist
if 'papers' not in st.session_state:
    st.session_state.papers = []
    
if 'search_history' not in st.session_state:
    # Load search history from file
    st.session_state.search_history = load_search_history()
    
if 'last_search' not in st.session_state:
    st.session_state.last_search = None
    
if 'enter_pressed' not in st.session_state:
    st.session_state.enter_pressed = False
    
if 'categories' not in st.session_state:
    # Load categories from file
    st.session_state.categories = load_categories()

# Configure page
st.set_page_config(
    page_title="arXiv Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions for state management
def reset_search_results():
    """Reset the search results"""
    st.session_state.papers = []
    st.session_state.last_search = None

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
        user_id = st.text_input(
            "Your Name/ID (for storing preferences):",
            key="user_id_input"
        )
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio("Go to", ["Author Search", "Daily Papers", "My Profile"])
        
        # Add search history management in sidebar
        if page == "Author Search" and st.session_state.search_history:
            st.subheader("Search History")
            
            # Display current history
            history_str = "\n".join([f"• {h}" for h in st.session_state.search_history])
            st.text_area("Recent searches:", history_str, height=100, disabled=True)
            
            # Clear history button
            if st.button("Clear Search History"):
                st.session_state.search_history = []
                # Clear the file too
                save_search_history([])
                st.rerun()
                
            # Clear current results
            if st.session_state.papers and st.button("Clear Current Results"):
                reset_search_results()
                st.rerun()
        
        # Categories manager in sidebar
        st.subheader("arXiv Categories")
        
        # Create tabs for viewing and managing categories
        cat_tab1, cat_tab2 = st.tabs(["View Categories", "Manage Categories"])
        
        with cat_tab1:
            # Get all categories but filter out hidden ones
            hidden_categories = getattr(st.session_state, "hidden_categories", set())
            visible_categories = []
            
            # Combine and filter categories
            for cat_list in ["default_categories", "custom_categories"]:
                for cat in st.session_state.categories.get(cat_list, []):
                    if cat["code"] not in hidden_categories:
                        visible_categories.append(cat)
            
            # Display visible categories
            if visible_categories:
                st.write("**Visible Categories:**")
                for cat in visible_categories:
                    st.write(f"- {cat['code']}: {cat['name']}")
            else:
                st.write("No visible categories. Enable some categories in the 'Manage Categories' tab.")
            
            # Optionally show hidden categories too
            if hidden_categories:
                with st.expander("Hidden Categories"):
                    for cat_list in ["default_categories", "custom_categories"]:
                        for cat in st.session_state.categories.get(cat_list, []):
                            if cat["code"] in hidden_categories:
                                st.write(f"- {cat['code']}: {cat['name']}")
        
        with cat_tab2:
            # Add new category
            with st.form(key="add_category_form"):
                st.write("**Add New Category**")
                new_cat_code = st.text_input("Category Code (e.g., cs.AI):", key="new_cat_code")
                new_cat_name = st.text_input("Category Name:", key="new_cat_name")
                add_cat_submitted = st.form_submit_button("Add Category")
    
                if add_cat_submitted and new_cat_code and new_cat_name:
                    # Check if category already exists
                    existing_codes = [
                        cat["code"] for cat in 
                        st.session_state.categories.get("default_categories", []) + 
                        st.session_state.categories.get("custom_categories", [])
                    ]
                    
                    if new_cat_code in existing_codes:
                        st.error(f"Category {new_cat_code} already exists")
                    else:
                        # Add new category to custom categories
                        st.session_state.categories.setdefault("custom_categories", []).append({
                            "code": new_cat_code,
                            "name": new_cat_name
                        })
                        
                        # Save updated categories
                        save_categories(st.session_state.categories)
                        st.success(f"Added category: {new_cat_code}")
                        st.rerun()
            
            # Remove categories
            st.write("**Remove Categories**")
            
            # Default categories (can be hidden but not removed)
            st.write("Default Categories:")
            for i, cat in enumerate(st.session_state.categories.get("default_categories", [])):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{cat['code']}: {cat['name']}")
                with col2:
                    # Initialize hidden_categories if not already in session state
                    if "hidden_categories" not in st.session_state:
                        st.session_state.hidden_categories = set()
                        
                    # Check if category is currently hidden
                    is_hidden = cat['code'] in st.session_state.hidden_categories
                    
                    # Create radio button
                    visibility = st.radio(
                        "Visibility",
                        options=["Show", "Hide"],
                        index=1 if is_hidden else 0,  # Default to current state
                        key=f"visibility_{cat['code']}",
                        horizontal=True,
                        label_visibility="collapsed"  # Hide the label
                    )
                    
                    # Update hidden categories based on selection
                    if visibility == "Hide" and not is_hidden:
                        st.session_state.hidden_categories.add(cat['code'])
                    elif visibility == "Show" and is_hidden:
                        st.session_state.hidden_categories.discard(cat['code'])
            
            # Custom categories (can be completely removed)
            if st.session_state.categories.get("custom_categories", []):
                st.write("Custom Categories:")
                for i, cat in enumerate(st.session_state.categories.get("custom_categories", [])):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{cat['code']}: {cat['name']}")
                    with col2:
                        if st.button("Remove", key=f"remove_{i}"):
                            # Remove category
                            st.session_state.categories["custom_categories"].pop(i)
                            # Save updated categories
                            save_categories(st.session_state.categories)
                            st.success(f"Removed category: {cat['code']}")
                            st.rerun()
            else:
                st.write("No custom categories added yet.")
                
            # Reset to defaults button
            if st.button("Reset to Default Categories"):
                # Reset categories
                st.session_state.categories = {
                    "default_categories": st.session_state.categories.get("default_categories", []),
                    "custom_categories": []
                }
                st.session_state.hidden_categories = set()
                # Save updated categories
                save_categories(st.session_state.categories)
                st.success("Reset to default categories")
                st.rerun()
        
    # Main content
    if page == "Author Search":
        st.title("Search by Author")
        
        # Handle form submission (this properly captures Enter key presses)
        with st.form(key="search_form"):
            # Create search history dropdown inside the form
            history_options = [""] + st.session_state.search_history
            history_index = 0
            
            if st.session_state.last_search in history_options:
                history_index = history_options.index(st.session_state.last_search)
                
            selected_history = st.selectbox(
                "Recent searches:",
                history_options,
                index=history_index,
                key="history_dropdown"
            )
            
            # Create a row with text input and max results
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Use the selected history item as default for the text input
                author_id = st.text_input(
                    "Enter arXiv Author ID or Name:",
                    value=selected_history,
                    key="author_input"
                )
            
            with col2:
                # Set max results with a number input instead of slider for space efficiency
                max_results = st.number_input(
                    "Max results", 
                    min_value=5, 
                    max_value=100, 
                    value=25,
                    step=5,
                    key="max_results"
                )
            
            # Search button (within form)
            search_pressed = st.form_submit_button("Search", use_container_width=True)
        
        # Check if form was submitted or history selection changed
        search_triggered = search_pressed or (selected_history != "" and selected_history != st.session_state.last_search)
        
        if search_triggered and author_id:
            # Update session state
            st.session_state.last_search = author_id
            
            # Add to search history if not already there
            if author_id not in st.session_state.search_history:
                st.session_state.search_history.append(author_id)
                # Keep most recent 10 searches
                st.session_state.search_history = st.session_state.search_history[-10:]
                # Save updated history to file
                save_search_history(st.session_state.search_history)
            
            # Fetch papers
            with st.spinner("Fetching papers..."):
                result = fetch_papers_by_author(author_id, max_results)
                
                if result.get("success", False):
                    # Store papers in session state
                    st.session_state.papers = result.get("papers", [])
                    st.success(f"Found {len(st.session_state.papers)} papers by {author_id}")
                else:
                    st.error("Failed to fetch papers. Please try again.")
        
        # If we have papers, show sorting and display options
        if st.session_state.papers:
            # Add sorting options
            st.subheader("Sort Results")
            col1, col2 = st.columns(2)
            
            with col1:
                sort_by = st.selectbox(
                    "Sort by:",
                    ["Published Date", "Updated Date", "Title"],
                    index=0,
                    key="sort_by"
                )
            
            with col2:
                sort_order = st.radio(
                    "Order:",
                    ["Newest First", "Oldest First"] if "Date" in sort_by else ["A-Z", "Z-A"],
                    horizontal=True,
                    key="sort_order"
                )
                    
            # Future enhancement for citation count sorting
            citation_sorting = st.checkbox(
                "Show citation count sorting (future enhancement)", 
                value=False,
                key="citation_checkbox"
            )
            
            if citation_sorting:
                st.info("""
                Citation count sorting will be available in a future update. This requires:
                1. Integration with a citation database (Semantic Scholar, CrossRef, Google Scholar, etc.)
                2. API key setup and rate limiting
                3. Cache for citation data to avoid excessive API calls
                """)
            
            # Get papers from session state
            papers_to_display = st.session_state.papers.copy()
            
            # Sort the papers based on selection
            if sort_by == "Published Date":
                # Convert date strings to datetime for proper sorting
                try:
                    papers_to_display = sorted(
                        papers_to_display,
                        key=lambda x: datetime.strptime(x.get("published", "1900-01-01"), "%Y-%m-%dT%H:%M:%SZ"),
                        reverse=(sort_order == "Newest First")
                    )
                except Exception as e:
                    st.warning(f"Some papers may have invalid date formats. Basic sorting applied.")
                    # Fallback sorting if date parsing fails
                    papers_to_display = sorted(
                        papers_to_display,
                        key=lambda x: x.get("published", ""),
                        reverse=(sort_order == "Newest First")
                    )
                    
            elif sort_by == "Updated Date":
                try:
                    papers_to_display = sorted(
                        papers_to_display,
                        key=lambda x: datetime.strptime(x.get("updated", "1900-01-01"), "%Y-%m-%dT%H:%M:%SZ"),
                        reverse=(sort_order == "Newest First")
                    )
                except Exception as e:
                    # Fallback sorting
                    papers_to_display = sorted(
                        papers_to_display,
                        key=lambda x: x.get("updated", ""),
                        reverse=(sort_order == "Newest First")
                    )
            
            elif sort_by == "Title":
                papers_to_display = sorted(
                    papers_to_display,
                    key=lambda x: x.get("title", "").lower(),
                    reverse=(sort_order == "Z-A")
                )
            
            # Refresh button
            if st.button("Refresh Results", key="refresh_button"):
                st.rerun()
            
            # Display count of papers
            st.write(f"**Displaying {len(papers_to_display)} papers**")
            
            # Display papers with a counter
            for i, paper in enumerate(papers_to_display, 1):
                st.write(f"**Paper {i} of {len(papers_to_display)}**")
                render_paper_card(paper)
                st.markdown("---")
                    
    elif page == "Daily Papers":
        st.title("Daily arXiv Submissions")
        
        # Category selection
        st.subheader("Filter by Categories")
        categories = []
        
        # Get all available categories (excluding hidden ones)
        available_categories = []
        hidden_categories = getattr(st.session_state, "hidden_categories", set())
        
        for cat_list in ["default_categories", "custom_categories"]:
            for cat in st.session_state.categories.get(cat_list, []):
                if cat["code"] not in hidden_categories:
                    available_categories.append(cat)
        
        # Display categories in a grid of checkboxes
        if available_categories:
            # Create columns based on number of categories (2-4 columns)
            num_cols = min(4, max(2, len(available_categories) // 3 + 1))
            cols = st.columns(num_cols)
            
            for i, cat in enumerate(available_categories):
                col_idx = i % num_cols
                with cols[col_idx]:
                    if st.checkbox(f"{cat['name']} ({cat['code']})"):
                        categories.append(cat['code'])
        else:
            st.warning("No categories available. Please add some in the sidebar 'Manage Categories' tab.")
        
        # Option to add a custom category for this search only
        with st.expander("Add temporary category"):
            custom_category = st.text_input("Add category for this search only (e.g., stat.ML):")
            if custom_category:
                categories.append(custom_category)
                st.info(f"Added temporary category: {custom_category}. To save this category permanently, use the sidebar 'Manage Categories' tab.")
            
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