def summarize(pdf_path):
    from transformers import pipeline
    # Load BART summarizer
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_section(text, max_len=50):
        try:
            return summarizer(text, max_length=max_len, min_length=30, do_sample=False)[0]["summary_text"]
        except Exception as e:
            return f"Error summarizing: {e}"
        
    sections = extract_text_sections(pdf_path)

    summaries = []
    for section in sections:
        if len(section.split()) < 30:
            continue
        summary = summarize_section(section)
        summaries.append({
            "original": section,
            "summary": summary
        })

    return summaries

def extract_text_sections(pdf_path):
    import fitz #PyMuPDF
    doc = fitz.open(pdf_path)
    sections = []

    for page in doc:
        blocks = page.get_text("blocks")
        for b in sorted(blocks, key = lambda x:(x[1], x[0])):
            text = b[4].strip()
            if len(text.split()) > 5:
                sections.append(text)
    return sections

def main():
    import argparse
    import json 
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', required=True, help='Path to the PDF file')
    args = parser.parse_args()
    outp = summarize(args.pdf)
    print(json.dumps(outp, indent=2))

if __name__ == '__main__':
    main()