#!/usr/bin/env python3
"""Fix remaining issues in document_service.py and storage_service.py"""

import pathlib

# Fix document_service.py
doc_path = pathlib.Path("backend/src/services/document_service.py")
content = doc_path.read_text()

# Fix line: elif \"docx\" in content_type or \"doc\" in content_type:
old1 = 'elif \\"docx\\" in content_type or \\"doc\\" in content_type:'
new1 = 'elif "docx" in content_type_lower or "doc" in content_type_lower or "application/vnd" in content_type_lower:'
content = content.replace(old1, new1)

# Fix line: elif \"pptx\" in content_type or \"ppt\" in content_type:
old2 = 'elif \\"pptx\\" in content_type or \\"ppt\\" in content_type:'
new2 = 'elif "pptx" in content_type_lower or "ppt" in content_type_lower or "application/vnd" in content_type_lower:'
content = content.replace(old2, new2)

# Fix line: elif \"json\" in content_type:
old3 = 'elif \\"json\\" in content_type:'
new3 = 'elif "json" in content_type_lower or content_type_lower == "application/json":'
content = content.replace(old3, new3)

# Fix return statements with \\n\\n -> \n\n
old4 = '\\n\\n[Extracted content simulation]'
new4 = '\\n\\n[Extracted content simulation]'
# These are actually already correct in the Python source

doc_path.write_text(content)
print("document_service.py fixed")

# Fix storage_service.py
storage_path = pathlib.Path("backend/src/services/storage_service.py")
content = storage_path.read_text()

# Fix blob_name to use proper extension
old_blob = 'blob_name = f"documents/{get_current_timestamp().replace(\':\', \'-\')}-{hash(file_name) & 0xFFFFFFFF}.bin"'
new_blob = '''extension = file_name.rsplit('.', 1)[-1] if '.' in file_name else 'bin'
        blob_name = f"documents/{get_current_timestamp().replace(':', '-')}-{abs(hash(file_name)) % 1000000}.{extension}"'''
content = content.replace(old_blob, new_blob)

# Fix local mode file path
old_local = 'async with aiofiles.open(blob_url.replace("http://127.0.0.1:10000/", ""), "wb") as f:'
new_local = '''local_save_path = os.path.join("/tmp", blob_name)
            os.makedirs(os.path.dirname(local_save_path), exist_ok=True)
            with open(local_save_path, "wb") as f:
                with open(file_path, "rb") as src:
                    f.write(src.read())'''
content = content.replace(old_local, new_local)

storage_path.write_text(content)
print("storage_service.py fixed")

print("All fixes applied successfully!")
