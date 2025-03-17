import streamlit as st
import requests
import xml.etree.ElementTree as ET

def fetch_arxiv_data(author_id):
    # Function to fetch data from arXiv API using author identifier
    url = f'http://export.arxiv.org/api/query?search_query=au:{author_id}'
    response = requests.get(url)
    return response.text

def parse_arxiv_data(xml_data):
    # Function to parse XML data and extract relevant information
    root = ET.fromstring(xml_data)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
    papers = []
    for entry in entries:
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        papers.append({'title': title, 'summary': summary})
    return papers

def main():
    st.title("Arxiv Research Profile Builder")
    author_id = st.text_input("Enter your arXiv Author ID:")
    
    if author_id:
        xml_data = fetch_arxiv_data(author_id)
        papers = parse_arxiv_data(xml_data)
        st.write("Research Profile for arXiv Author ID:", author_id)
        for paper in papers:
            st.write("Title:", paper['title'])
            st.write("Summary:", paper['summary'])

if __name__ == "__main__":
    main()