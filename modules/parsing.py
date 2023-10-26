import hashlib
import sqlite3
import time
from pathlib import Path
from io import BytesIO
from ole_extractor import OLEExtractor
from hwp_extractor import HWPExtractor
from docx_extractor import DOCXExtractor
from pptx_extractor import PPTXExtractor
from xlsx_extractor import XLSXExtractor

def read_file_with_different_encodings(file_data):
    encodings = ['utf-8', 'iso-8859-1', 'cp949']  
    for encoding in encodings:
        try:
            return file_data.decode(encoding).strip()
        except Exception:
            continue
    raise Exception("Unable to decode the file data with the provided encodings.")

def extract_text(file_data, ext):
    text = ""
    try:
        if ext in [".doc", ".ppt", ".xls"]:
            extractor = OLEExtractor(file_data)  # modified line
            text = extractor.get_text()
        elif ext == ".docx":
            extractor = DOCXExtractor(file_data)  # modified line
            text = extractor.get_text()
        elif ext == ".pptx":
            extractor = PPTXExtractor(file_data)  # modified line
            text = extractor.get_text()
        elif ext == ".xlsx":
            extractor = XLSXExtractor(file_data)  # modified line
            text = extractor.get_text()
        elif ext == ".hwp":
            extractor = HWPExtractor(file_data)  # modified line
            text = extractor.get_text()
        elif ext in [".txt", ".csv"]:
            text = read_file_with_different_encodings(file_data)
        else:
            print(f"지원하지 않는 파일 형식: {ext}")
    except Exception as e:
        logging.error(f"Error occurred during text extraction: {e}, File Extension: {ext}")
        user_input = input("An error occurred. Do you want to continue? (y/n): ")
        if user_input.lower() != 'y':
            sys.exit("Exiting the program.")
    return text.strip()



def calculate_hash(file_data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_data)
    return sha256_hash.hexdigest()

def save_metadata_and_blob_to_db(conn, metadata, blob_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (file_path, hash_value, plain_text, m_time, a_time, c_time, blob_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', metadata + (blob_data,))
    conn.commit()

def process_byte_data(byte_data, file_extension, conn):
    if file_extension.lower() in whitelist_extensions:
        try:
            blob_data = sqlite3.Binary(byte_data)
            hash_value = calculate_hash(byte_data)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files (hash_value, blob_data)
                VALUES (?, ?)
            ''', (hash_value, blob_data))
            conn.commit()

        except Exception as e:
            print(f"데이터 처리 중 오류 발생: {e}")
                    
# DB 연결 및 테이블 생성 부분에서 blob_data 컬럼 추가
conn = sqlite3.connect('parsing.sqlite')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value TEXT NOT NULL,
    plain_text TEXT,
    m_time TEXT NOT NULL,
    a_time TEXT NOT NULL,
    c_time TEXT NOT NULL,
    blob_data BLOB
)
''')

# 화이트리스트 확장자
whitelist_extensions = ('.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt')

# DB 연결 종료
conn.close()