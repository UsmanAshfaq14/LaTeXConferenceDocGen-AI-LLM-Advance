import re
import xml.etree.ElementTree as ET
from io import StringIO
import math

def validate_xml_data(xml_string):
    """Validate XML data structure and content."""
    try:
        # Parse XML string
        root = ET.fromstring(xml_string)
        
        validation_report = {
            "total_papers": 0,
            "valid": True,
            "errors": [],
            "field_validity": {
                "paper_title": True,
                "authors": True,
                "abstract": True,
                "content": True,
                "author_biography": True
            },
            "papers": []
        }
        
        # Validate each paper
        for i, paper in enumerate(root.findall('paper')):
            paper_id = f"Paper {i+1}"
            validation_report["total_papers"] += 1
            paper_data = {"id": paper_id, "errors": []}
            
            # Check required fields
            required_fields = ['paper_title', 'authors', 'abstract', 'content', 'author_biography']
            missing_fields = []
            empty_fields = []
            
            for field in required_fields:
                if field != 'authors':
                    element = paper.find(field)
                    if element is None:
                        missing_fields.append(field)
                        validation_report["field_validity"][field] = False
                    elif element.text is None or element.text.strip() == "":
                        empty_fields.append(field)
                        validation_report["field_validity"][field] = False
                else:
                    authors = paper.find('authors')
                    if authors is None:
                        missing_fields.append(field)
                        validation_report["field_validity"][field] = False
                    else:
                        author_elements = authors.findall('author')
                        if not author_elements:
                            missing_fields.append('author')
                            validation_report["field_validity"][field] = False
                        else:
                            has_valid_author = False
                            for author in author_elements:
                                if author.text and author.text.strip():
                                    has_valid_author = True
                                    break
                            if not has_valid_author:
                                empty_fields.append(field)
                                validation_report["field_validity"][field] = False
            
            # Record errors
            if missing_fields:
                error_msg = f"ERROR: Missing required tag(s): {', '.join(missing_fields)} in {paper_id}."
                paper_data["errors"].append(error_msg)
                validation_report["errors"].append(error_msg)
                validation_report["valid"] = False
            
            if empty_fields:
                error_msg = f"ERROR: Empty content in required tag(s): {', '.join(empty_fields)} in {paper_id}."
                paper_data["errors"].append(error_msg)
                validation_report["errors"].append(error_msg)
                validation_report["valid"] = False
            
            validation_report["papers"].append(paper_data)
        
        return validation_report, root
    
    except ET.ParseError:
        return {
            "valid": False,
            "errors": ["ERROR: Invalid data format. Please provide data in XML format enclosed in a markdown block."],
            "field_validity": {
                "paper_title": False,
                "authors": False,
                "abstract": False,
                "content": False,
                "author_biography": False
            },
            "total_papers": 0
        }, None

def count_words(text):
    """Count the number of words in a text."""
    if not text:
        return 0
    return len(re.findall(r'\b\w+\b', text))

def count_characters_no_spaces(text):
    """Count characters excluding spaces."""
    if not text:
        return 0
    return len(re.sub(r'\s', '', text))

def count_sentences(text):
    """Count the number of sentences in a text."""
    if not text:
        return 0
    # Split text by period, exclamation mark, or question mark followed by a space or end of string
    sentences = re.split(r'[.!?](?:\s|$)', text)
    # Remove empty strings from the list
    sentences = [s for s in sentences if s]
    return len(sentences)

def keyword_density(text, keyword):
    """Calculate keyword density for a given keyword."""
    if not text or not keyword:
        return 0
    total_words = count_words(text)
    if total_words == 0:
        return 0
    keyword_count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
    return (keyword_count / total_words) * 100

def perform_calculations(paper_element):
    """Perform all required calculations for a paper."""
    abstract = paper_element.find('abstract').text
    content = paper_element.find('content').text
    
    # Word Count Calculation
    abstract_word_count = count_words(abstract)
    content_word_count = count_words(content)
    total_word_count = abstract_word_count + content_word_count
    
    # Abstract to Content Ratio
    abstract_content_ratio = (abstract_word_count / content_word_count) * 100 if content_word_count > 0 else 0
    
    # Average Word Length
    total_chars = count_characters_no_spaces(abstract + content)
    avg_word_length = total_chars / total_word_count if total_word_count > 0 else 0
    
    # Sentence Count
    abstract_sentences = count_sentences(abstract)
    content_sentences = count_sentences(content)
    total_sentences = abstract_sentences + content_sentences
    
    # Average Sentence Length
    avg_sentence_length = total_word_count / total_sentences if total_sentences > 0 else 0
    
    # Reading Time Estimation
    reading_time = total_word_count / 200  # 200 words per minute
    
    # Keyword Density (using a simple approach - finding most frequent meaningful word)
    words = re.findall(r'\b\w+\b', content.lower())
    stopwords = {'the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    keyword = ""
    keyword_count = 0
    if filtered_words:
        word_counts = {}
        for word in filtered_words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        keyword = max(word_counts, key=word_counts.get)
        keyword_count = word_counts[keyword]
    
    keyword_density_value = (keyword_count / total_word_count) * 100 if total_word_count > 0 else 0
    
    # Complexity Score
    normalized_word_count = total_word_count / 1000
    normalized_avg_sentence = avg_sentence_length / 20
    normalized_abstract_ratio = abstract_content_ratio / 20
    
    complexity_score = (normalized_word_count * 0.3) + (normalized_avg_sentence * 0.4) + (normalized_abstract_ratio * 0.3)
    
    return {
        "abstract_word_count": abstract_word_count,
        "content_word_count": content_word_count,
        "total_word_count": total_word_count,
        "abstract_content_ratio": abstract_content_ratio,
        "avg_word_length": avg_word_length,
        "abstract_sentences": abstract_sentences,
        "content_sentences": content_sentences,
        "total_sentences": total_sentences,
        "avg_sentence_length": avg_sentence_length,
        "reading_time": reading_time,
        "keyword": keyword,
        "keyword_count": keyword_count,
        "keyword_density": keyword_density_value,
        "complexity_score": complexity_score
    }

def generate_validation_report(validation_result):
    """Generate a markdown validation report."""
    report = "# Data Validation Report:\n"
    report += f"- Total Papers Evaluated: {validation_result['total_papers']}\n"
    report += "- Fields Checked: paper_title, authors, abstract, content, author_biography\n\n"
    
    report += "## Fields Validity\n"
    for field, valid in validation_result["field_validity"].items():
        report += f"- {field}: {'valid' if valid else 'invalid'}\n"
    
    report += "\n## Validation Summary:\n"
    if validation_result["valid"]:
        report += "Data validation is successful! Would you like to proceed with LaTeX document generation?\n"
    else:
        for error in validation_result["errors"]:
            report += f"- {error}\n"
    
    return report

def generate_detailed_report(paper_element, calculations):
    """Generate a detailed report for a paper."""
    title = paper_element.find('paper_title').text
    
    # Get authors
    authors_element = paper_element.find('authors')
    authors = []
    for author_element in authors_element.findall('author'):
        if author_element.text:
            authors.append(author_element.text)
    
    abstract = paper_element.find('abstract').text
    content = paper_element.find('content').text
    biography = paper_element.find('author_biography').text
    
    # Format the detailed report
    report = f"### Paper: {title}\n\n"
    report += "#### Input Data:\n"
    report += f"- **Paper Title:** {title}\n"
    report += f"- **Authors:** {', '.join(authors)}\n"
    report += "- **Abstract:**  \n"
    report += f"  {abstract}\n"
    report += "- **Content:**  \n"
    report += f"  {content}\n"
    report += "- **Author Biography:**  \n"
    report += f"  {biography}\n\n"
    
    report += "---\n\n"
    report += "#### Detailed Calculations:\n\n"
    
    # 1. Word Count Calculation
    report += "1. **Word Count Calculation:**\n"
    report += " - **Formula:** $ \\text{Word Count} = \\text{words in abstract} + \\text{words in content} $\n"
    report += " - **Steps:**\n"
    report += f"   - Count the number of words in the abstract: {calculations['abstract_word_count']}\n"
    report += f"   - Count the number of words in the content: {calculations['content_word_count']}\n"
    report += f"   - Add both counts together: {calculations['abstract_word_count']} + {calculations['content_word_count']} = {calculations['total_word_count']}\n"
    report += f" - **Final Word Count:** **{calculations['total_word_count']:.2f}**\n\n"
    
    # 2. Abstract to Content Ratio
    report += "2. **Abstract to Content Ratio Calculation:**\n"
    report += " - **Formula:** $ \\text{Abstract to Content Ratio} = \\left(\\frac{\\text{words in abstract}}{\\text{words in content}}\\right) \\times 100 $\n"
    report += " - **Steps:**\n"
    report += f"   - Divide the abstract word count by the content word count: {calculations['abstract_word_count']} ÷ {calculations['content_word_count']} = {calculations['abstract_word_count'] / calculations['content_word_count']:.4f}\n"
    report += f"   - Multiply the result by 100: {calculations['abstract_word_count'] / calculations['content_word_count']:.4f} × 100 = {calculations['abstract_content_ratio']:.2f}%\n"
    report += f" - **Final Ratio:** **{calculations['abstract_content_ratio']:.2f}%**\n\n"
    
    # 3. Average Word Length
    report += "3. **Average Word Length Calculation:**\n"
    report += " - **Formula:** $ \\text{Average Word Length} = \\frac{\\text{Total Characters (excluding spaces)}}{\\text{Total Word Count}} $\n"
    report += " - **Steps:**\n"
    total_chars = count_characters_no_spaces(abstract + content)
    report += f"   - Count all characters in the abstract and content, excluding spaces: {total_chars}\n"
    report += f"   - Divide the total number of characters by the total word count: {total_chars} ÷ {calculations['total_word_count']} = {calculations['avg_word_length']:.4f}\n"
    report += f" - **Final Average Word Length:** **{calculations['avg_word_length']:.2f} characters**\n\n"
    
    # 4. Sentence Count
    report += "4. **Sentence Count Calculation:**\n"
    report += " - **Formula:** $ \\text{Total Sentences} = \\text{Sentences in abstract} + \\text{Sentences in content} $\n"
    report += " - **Steps:**\n"
    report += f"   - Identify and count the number of sentences in the abstract: {calculations['abstract_sentences']}\n"
    report += f"   - Identify and count the number of sentences in the content: {calculations['content_sentences']}\n"
    report += f"   - Add both counts together: {calculations['abstract_sentences']} + {calculations['content_sentences']} = {calculations['total_sentences']}\n"
    report += f" - **Final Sentence Count:** **{calculations['total_sentences']}**\n\n"
    
    # 5. Average Sentence Length
    report += "5. **Average Sentence Length Calculation:**\n"
    report += " - **Formula:** $ \\text{Average Sentence Length} = \\frac{\\text{Word Count}}{\\text{Total Sentences}} $\n"
    report += " - **Steps:**\n"
    report += f"   - Use the total word count from the Word Count Calculation: {calculations['total_word_count']}\n"
    report += f"   - Divide the total word count by the total number of sentences: {calculations['total_word_count']} ÷ {calculations['total_sentences']} = {calculations['avg_sentence_length']:.4f}\n"
    report += f" - **Final Average Sentence Length:** **{calculations['avg_sentence_length']:.2f} words per sentence**\n\n"
    
    # 6. Reading Time Estimation
    report += "6. **Reading Time Estimation:**\n"
    report += " - **Formula:** $ \\text{Estimated Reading Time (minutes)} = \\frac{\\text{Word Count}}{200} $\n"
    report += " - **Steps:**\n"
    report += "   - Assume an average reading speed of 200 words per minute.\n"
    report += f"   - Divide the total word count by 200: {calculations['total_word_count']} ÷ 200 = {calculations['reading_time']:.4f}\n"
    report += f" - **Final Estimated Reading Time:** **{calculations['reading_time']:.2f} minutes**\n\n"
    
    # 7. Keyword Density
    report += "7. **Keyword Density Calculation:**\n"
    report += " - **Formula:** $ \\text{Keyword Density (\\%)} = \\left(\\frac{\\text{Keyword Occurrences}}{\\text{Word Count}}\\right) \\times 100 $\n"
    report += " - **Steps:**\n"
    report += f"   - Most frequent keyword identified: '{calculations['keyword']}'\n"
    report += f"   - Count the number of times the keyword appears in the content: {calculations['keyword_count']}\n"
    report += f"   - Divide the keyword occurrence count by the total word count: {calculations['keyword_count']} ÷ {calculations['total_word_count']} = {calculations['keyword_count'] / calculations['total_word_count']:.4f}\n"
    report += f"   - Multiply the result by 100: {calculations['keyword_count'] / calculations['total_word_count']:.4f} × 100 = {calculations['keyword_density']:.2f}%\n"
    report += f" - **Final Keyword Density:** **{calculations['keyword_density']:.2f}%**\n\n"
    
    # 8. Complexity Score
    report += "8. **Complexity Score Calculation:**\n"
    report += " - **Formula:**  \n"
    report += " $$ \\text{Complexity Score} = \\left(\\frac{\\text{Word Count}}{1000} \\times 0.3\\right) + \\left(\\frac{\\text{Average Sentence Length}}{20} \\times 0.4\\right) + \\left(\\frac{\\text{Abstract to Content Ratio}}{20} \\times 0.3\\right) $$\n"
    report += " - **Steps:**\n"
    normalized_word_count = calculations['total_word_count'] / 1000
    normalized_avg_sentence = calculations['avg_sentence_length'] / 20
    normalized_abstract_ratio = calculations['abstract_content_ratio'] / 20
    
    report += f"   - Normalize the Word Count by dividing it by 1000: {calculations['total_word_count']} ÷ 1000 = {normalized_word_count:.4f}\n"
    report += f"   - Normalize the Average Sentence Length by dividing it by 20: {calculations['avg_sentence_length']:.2f} ÷ 20 = {normalized_avg_sentence:.4f}\n"
    report += f"   - Normalize the Abstract to Content Ratio by dividing it by 20: {calculations['abstract_content_ratio']:.2f} ÷ 20 = {normalized_abstract_ratio:.4f}\n"
    report += f"   - Multiply the normalized Word Count by 0.3: {normalized_word_count:.4f} × 0.3 = {normalized_word_count * 0.3:.4f}\n"
    report += f"   - Multiply the normalized Average Sentence Length by 0.4: {normalized_avg_sentence:.4f} × 0.4 = {normalized_avg_sentence * 0.4:.4f}\n"
    report += f"   - Multiply the normalized Abstract to Content Ratio by 0.3: {normalized_abstract_ratio:.4f} × 0.3 = {normalized_abstract_ratio * 0.3:.4f}\n"
    report += f"   - Sum all three products: {normalized_word_count * 0.3:.4f} + {normalized_avg_sentence * 0.4:.4f} + {normalized_abstract_ratio * 0.3:.4f} = {calculations['complexity_score']:.4f}\n"
    report += f" - **Final Complexity Score:** **{calculations['complexity_score']:.2f}**\n\n"
    
    return report

def generate_latex_document(paper_element):
    """Generate LaTeX document sections for a paper."""
    title = paper_element.find('paper_title').text
    
    # Get authors
    authors_element = paper_element.find('authors')
    authors = []
    for author_element in authors_element.findall('author'):
        if author_element.text:
            authors.append(author_element.text)
    
    abstract = paper_element.find('abstract').text
    content = paper_element.find('content').text
    biography = paper_element.find('author_biography').text
    
    latex_doc = "## LaTeX Document Generation\n\n"
    
    # Title Page
    latex_doc += "- **Title Page:**  \n"
    latex_doc += f"  ```latex\n"
    latex_doc += f"  \\documentclass{{article}}\n"
    latex_doc += f"  \\title{{{title}}}\n"
    latex_doc += f"  \\author{{{' \\and '.join(authors)}}}\n"
    latex_doc += f"  \\date{{\\today}}\n"
    latex_doc += f"  \\begin{{document}}\n"
    latex_doc += f"  \\maketitle\n"
    latex_doc += f"  ```\n\n"
    
    # Abstract Section
    latex_doc += "- **Abstract Section:**  \n"
    latex_doc += f"  ```latex\n"
    latex_doc += f"  \\begin{{abstract}}\n"
    latex_doc += f"  {abstract}\n"
    latex_doc += f"  \\end{{abstract}}\n"
    latex_doc += f"  ```\n\n"
    
    # Main Content Section
    latex_doc += "- **Main Content Section:**  \n"
    latex_doc += f"  ```latex\n"
    latex_doc += f"  \\section{{Introduction}}\n"
    
    # Split content into paragraphs and create sections
    paragraphs = content.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if i == 0:
            latex_doc += f"  {paragraph}\n\n"
        else:
            section_name = f"Section {i}"
            latex_doc += f"  \\section{{{section_name}}}\n"
            latex_doc += f"  {paragraph}\n\n"
    
    latex_doc += f"  ```\n\n"
    
    # Author Biography Section
    latex_doc += "- **Author Biography Section:**  \n"
    latex_doc += f"  ```latex\n"
    latex_doc += f"  \\section{{Author Biography}}\n"
    latex_doc += f"  {biography}\n\n"
    latex_doc += f"  \\end{{document}}\n"
    latex_doc += f"  ```\n\n"
    
    return latex_doc

def process_xml_data(xml_string):
    """Process XML data and generate report."""
    validation_result, root = validate_xml_data(xml_string)
    
    # Generate validation report
    validation_report = generate_validation_report(validation_result)
    
    # If validation failed, return only the validation report
    if not validation_result["valid"] or not root:
        return validation_report
    
    # Start building the final report
    final_report = "# LaTeX Conference Document Summary\n\n"
    final_report += f"**Total Papers Processed:** {validation_result['total_papers']}\n\n"
    final_report += "---\n\n"
    final_report += "## Detailed Analysis per Paper\n\n"
    
    # Process each paper
    for paper_element in root.findall('paper'):
        # Perform calculations
        calculations = perform_calculations(paper_element)
        
        # Generate detailed report
        paper_report = generate_detailed_report(paper_element, calculations)
        final_report += paper_report
        
        # Generate LaTeX document
        latex_doc = generate_latex_document(paper_element)
        final_report += "---\n\n"
        final_report += latex_doc
    
    return validation_report + "\n\n" + final_report

def main():
    """Main function to demonstrate the script's functionality."""
    # Example XML data
    example_xml = """
    <papers>
  <paper>
    <paper_title>Deep Neural Networks for Stock Prediction</paper_title>
    <authors>
      <author>Michael Carter</author>
      <author>Samantha Ray</author>
    </authors>
    <abstract>This paper investigates the use of deep neural networks in predicting stock market trends.</abstract>
    <content>Deep neural networks are increasingly used in financial markets due to their ability to model complex, nonlinear relationships in stock data. Experimental results show improved accuracy in trend prediction.</content>
    <author_biography>Michael Carter is a financial analyst and researcher, while Samantha Ray is a data scientist specializing in neural network applications.</author_biography>
  </paper>
  <paper>
    <paper_title>IoT Applications in Smart Homes</paper_title>
    <authors>
      <author>Olivia Martin</author>
    </authors>
    <abstract>This study explores the integration of IoT devices in modern smart homes.</abstract>
    <content>The adoption of IoT in home automation has led to significant improvements in energy efficiency, security, and convenience. Various case studies are discussed.</content>
    <author_biography>Olivia Martin is an expert in IoT solutions and smart home technologies.</author_biography>
  </paper>
  <paper>
    <paper_title>Solar Energy Efficiency</paper_title>
    <authors>
      <author>Eric Thompson</author>
      <author>Nina Patel</author>
    </authors>
    <abstract>This research analyzes efficiency improvements in solar energy technologies.</abstract>
    <content>Innovative materials and design changes have led to higher efficiency in solar panels. Comparative studies across regions demonstrate significant progress.</content>
    <author_biography>Eric Thompson and Nina Patel are leading researchers in renewable energy with extensive publications in solar technology.</author_biography>
  </paper>
  <paper>
    <paper_title>Robotic Process Automation in Industry</paper_title>
    <authors>
      <author>Lucas Brown</author>
    </authors>
    <abstract>This paper examines the effects of robotic process automation on industrial workflows.</abstract>
    <content>Robotic process automation streamlines repetitive tasks and improves accuracy in manufacturing. The implementation of RPA leads to reduced costs and enhanced productivity across various sectors.</content>
    <author_biography>Lucas Brown is an automation specialist with over a decade of experience in industrial robotics.</author_biography>
  </paper>
</papers>
    """
    
    # Process the XML data
    report = process_xml_data(example_xml)
    print(report)

if __name__ == "__main__":
    main()