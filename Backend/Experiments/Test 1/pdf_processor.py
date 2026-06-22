#library used to open PDFs read page text and pull out embedded images
import fitz
import os
import re

OUTPUT = "static/output"


def clean(text):
    return " ".join(text.split())

# this function detects the chapter in the text using regex pattern matching. It looks for the pattern "CHAPTER" followed by a number and returns it in uppercase. If no match is found, it returns None.
def detect_chapter(text):
    match = re.search(r"(CHAPTER\s*\d+)", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

# this function detects the topic in the text using regex pattern matching it looks for a pattern of digits separated by a dot (e.g., "1.1") and returns it. If no match is found, it returns None.
def detect_topic(text):
    match = re.search(r"\b(\d+\.\d+)\b", text) #it looks for standalone textbook style section numbers like 1.1, 4.12, or 10.5
    return match.group(1) if match else None

#Checks the Chapter and checks the Topic
def safe_init(data, chapter, topic):

    if chapter not in data:
        data[chapter] = {}

    if topic not in data[chapter]:
        data[chapter][topic] = {
            "text": "",
            "images": []
        }


def process_pdf(pdf_path):
    # open the PDF file using PyMuPDF (fitz)
    doc = fitz.open(pdf_path)
# extract file name  and combine the main output directory
    book_name = os.path.splitext(os.path.basename(pdf_path))[0]
    book_folder = os.path.join(OUTPUT, book_name)
# Physically create the folder on your computer if it doesn't already exist
    os.makedirs(book_folder, exist_ok=True)

    data = {} # int. completely empty dictionary
# for fallback tracking variables in case if the page has no heading
    current_chapter = "UNKNOWN_CHAPTER"
    current_topic = "GENERAL"
# runs through every page
    for page_num in range(len(doc)):

        page = doc.load_page(page_num)
        text = clean(page.get_text())
# Check the text for patterns like "Chapter 2" or section "2.1"
        chapter = detect_chapter(text)
        topic = detect_topic(text)

        if chapter:
            current_chapter = chapter

        if topic:
            current_topic = topic

        safe_init(data, current_chapter, current_topic)

        # TEXT STORAGE: drop the pages text into the correct dictionary folder

        data[current_chapter][current_topic]["text"] += text + "\n"

        # IMAGE EXTRACTION
        images = page.get_images(full=True)
# loop through the pages pictures one by one
        for i, img in enumerate(images):

            try:
                xref = img[0]
                base = doc.extract_image(xref)

                img_bytes = base["image"]
                ext = base["ext"]
# Construct a nested folder path Output / BookName / ChapterName / Topic Name
                folder = os.path.join(
                    book_folder,
                    current_chapter,
                    current_topic
                )

                os.makedirs(folder, exist_ok=True)

                img_path = os.path.join(
                    folder,
                    f"p{page_num}_{i}.{ext}"
                )

                with open(img_path, "wb") as f:
                    f.write(img_bytes)

                data[current_chapter][current_topic]["images"].append(img_path)

            except:
                pass

    doc.close()

    return data, book_name