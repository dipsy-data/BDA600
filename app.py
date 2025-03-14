# Works Mar 10 
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Function to fetch papers from arXiv
def fetch_arxiv_papers(query, sort_by, sort_order, start_date=None, end_date=None, max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    
    # Construct search query
    search_query = f"all:{query}"
    
    # Add date filters only if provided
    if start_date and end_date:
        search_query += f" AND submittedDate:[{start_date}0000 TO {end_date}2359]"
    
    # Construct query parameters
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    
    # Make request to ArXiv API
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return None
    
    # Parse XML response
    root = ET.fromstring(response.text)
    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        pdf_link = link.replace("abs", "pdf")
        published = entry.find("{http://www.w3.org/2005/Atom}published").text[:10]
        updated = entry.find("{http://www.w3.org/2005/Atom}updated").text[:10]
        
        authors = [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")]
        
        papers.append({
            "title": title,
            "summary": summary,
            "link": link,
            "pdf_link": pdf_link,
            "published": published,
            "updated": updated,
            "authors": ", ".join(authors),
        })
    
    return papers

# Streamlit UI
st.title("🔍 StudyBuddy - Search ArXiv Papers")

# Input field for search query
query = st.text_input("Enter keyword or topic:", "")

# Sorting options
sort_by = st.selectbox("Sort by:", ["relevance", "lastUpdatedDate", "submittedDate"])
sort_order = st.selectbox("Sort order:", ["descending", "ascending"])

# Date filters
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date (optional)", None)
with col2:
    end_date = st.date_input("End Date (optional)", None)

# Convert dates to arXiv format
start_date_str = start_date.strftime("%Y%m%d") if start_date else None
end_date_str = end_date.strftime("%Y%m%d") if end_date else None

# Search button
if st.button("Search Papers"):
    if not query:
        st.warning("Please enter a keyword or topic.")
    else:
        st.write("Fetching papers from ArXiv...")
        papers = fetch_arxiv_papers(query, sort_by, sort_order, start_date_str, end_date_str)

        if not papers:
            st.error("No results found. Try a different keyword or date range.")
        else:
            st.success(f"Found {len(papers)} papers")
            
            # Loop through the fetched papers
            for paper in papers:
                title_cleaned = paper['title'].replace("\n", " ").strip()

                st.markdown(f"### {title_cleaned}") 
                st.write(f"📅 **Published:** {paper['published']} | 🔄 **Updated:** {paper['updated']}")
                st.write(f"👨‍🔬 **Authors:** {paper['authors']}")
                st.write(f"📄 **Summary:** {paper['summary'][:300]}...")  # Truncate summary
                st.markdown(f"[📥 Download PDF]({paper['pdf_link']}) | [🔗 Read More on arXiv]({paper['link']})")
                st.write("---")  # Separator for readability
