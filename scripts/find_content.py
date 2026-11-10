#!/usr/bin/env python3
"""Check if document_service.py has the fix applied."""

path = "backend/src/services/document_service.py"

with open(path, "r") as f:
    content = f.read()

has_lower = "content_type_lower" in content
has_application_pdf = "application/pdf" in content
has_pdf_blob = "pdf" in content

print(f"content_type_lower found: {has_lower}")
print(f"application/pdf found: {has_application_pdf}")
print(f"pdf blob check found: {has_pdf_blob}")

if has_lower and has_application_pdf:
    print("SUCCESS: The fix appears to be applied")
else:
    print("MISSING: The fix may not be fully applied")
