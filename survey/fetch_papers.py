import requests
import xml.etree.ElementTree as ET
import re
import json
import os
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import io
from urllib.request import urlopen
from io import BytesIO


def get_papers(max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    cat = 'cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.RO'
    query = f"search_query={cat}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

    response = requests.get(base_url + query)

    if response.status_code == 200:
        return response.text
    else:
        print("Error fetching papers:", response.status_code)
        return None


def get_category_names(categories):
    category_labels = {
        'cs.AI': 'Artificial Intelligence',
        'cs.AR': 'Hardware Architecture',
        'cs.CC': 'Computational Complexity',
        'cs.CE': 'Computational Engineering, Finance, and Science',
        'cs.CG': 'Computational Geometry',
        'cs.CL': 'Computation and Language',
        'cs.CR': 'Cryptography and Security',
        'cs.CV': 'Computer Vision and Pattern Recognition',
        'cs.CY': 'Computers and Society',
        'cs.DB': 'Databases',
        'cs.DC': 'Distributed, Parallel, and Cluster Computing',
        'cs.DL': 'Digital Libraries',
        'cs.DM': 'Discrete Mathematics',
        'cs.DS': 'Data Structures and Algorithms',
        'cs.ET': 'Emerging Technologies',
        'cs.FL': 'Formal Languages and Automata Theory',
        'cs.GL': 'General Literature',
        'cs.GR': 'Graphics',
        'cs.GT': 'Computer Science and Game Theory',
        'cs.HC': 'Human-Computer Interaction',
        'cs.IR': 'Information Retrieval',
        'cs.IT': 'Information Theory',
        'cs.LG': 'Machine Learning',
        'cs.LO': 'Logic in Computer Science',
        'cs.MA': 'Multiagent Systems',
        'cs.MM': 'Multimedia',
        'cs.MS': 'Mathematical Software',
        'cs.NA': 'Numerical Analysis',
        'cs.NE': 'Neural and Evolutionary Computing',
        'cs.NI': 'Networking and Internet Architecture',
        'cs.OH': 'Other Computer Science',
        'cs.OS': 'Operating Systems',
        'cs.PF': 'Performance',
        'cs.PL': 'Programming Languages',
        'cs.RO': 'Robotics',
        'cs.SC': 'Symbolic Computation',
        'cs.SD': 'Sound',
        'cs.SE': 'Software Engineering',
        'cs.SI': 'Social and Information Networks',
        'cs.SY': 'Systems and Control'
    }
    
    return [category_labels.get(cat, cat) for cat in categories]




def extract_text_from_pdf(pdf_url):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with urlopen(pdf_url) as fd:
        data = fd.read()
        pdf_file = BytesIO(data)
        
        for page in PDFPage.get_pages(pdf_file, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
    
    text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()

    return text

def parse_papers(xml_data):
    papers = []
    root = ET.fromstring(xml_data)
    
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper = {}
        paper['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text
        paper['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text
        paper['pdf_url'] = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]').attrib['href']
        paper['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text
        paper['authors'] = [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
        paper['cat'] = [category.attrib['term'] for category in entry.findall('{http://www.w3.org/2005/Atom}category')]
        paper['content'] = extract_text_from_pdf(paper['pdf_url'])
        paper['cat_name'] = get_category_names(paper['cat'])

        
        papers.append(paper)
    
    return papers


def clean_filename(filename):
    cleaned_filename = re.sub(r'[/\\:*?"<>|]', '', filename)  # Remove special characters
    cleaned_filename = cleaned_filename.replace('\n', ' ')
    return cleaned_filename.strip()


if __name__ == "__main__":
    xml_data = get_papers(max_results=100)
    save_dir = 'raw_data'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    if xml_data:
        root = ET.fromstring(xml_data)
    
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            try:
                paper = {}
                paper['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text
                paper['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text
                paper['pdf_url'] = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]').attrib['href']
                paper['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text
                paper['authors'] = [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
                paper['cat'] = [category.attrib['term'] for category in entry.findall('{http://www.w3.org/2005/Atom}category')]
                paper['content'] = extract_text_from_pdf(paper['pdf_url'])
                paper['cat_name'] = get_category_names(paper['cat'])
                print("Title:", paper['title'])
                print("Link:", paper['id'])
                print("PDF URL:", paper['pdf_url'])
                print("Summary:", paper['summary'])
                print("Authors:", paper['authors'])
                print("Content:", paper['content'])
                print("cat:", paper['cat'])
                print("cat_name:", paper['cat_name'])
                # Clean the title for a valid filename
                cleaned_title = clean_filename(paper['title'])
                
                # Save paper data as a JSON file
                file_name = f"{cleaned_title}.json"
                if os.path.exists(os.path.join(save_dir, file_name)):
                    print(f"File {file_name} already exists. Skipping...")
                    break
                with open(os.path.join(save_dir, file_name), 'w', encoding='utf-8') as f:
                    json.dump(paper, f, ensure_ascii=False, indent=4)
                    
                print(f"Saved as {file_name}")
                print()
            except:
                continue

