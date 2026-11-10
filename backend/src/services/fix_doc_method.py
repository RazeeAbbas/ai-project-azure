#!/usr/bin/env python3
"""Fix the document_service.py _extract_text_from_bytes method."""

path = "backend/src/services/document_service.py"

with open(path, "r") as f:
    lines = f.readlines()

# Find the _extract_text_from_bytes method
new_lines = []
in_method = False
method_found = False
replacement_done = False

for i, line in enumerate(lines):
    if "_extract_text_from_bytes" in line:
        in_method = True
        method_found = True
        new_lines.append(line)
        continue
    
    if in_method:
        new_lines.append(line)
        
        # Check if we've reached the end of the method (next method or end of class)
        if line.strip().startswith("def _split_text") or (line.strip() == "class DocumentService" and i > 0):
            in_method = False
            # Insert the fixed method
            new_lines.append("        # Normalize content type for matching\n")
            new_lines.append("        content_type_lower = (content_type or \"\").lower().replace(\" \", \"\")\n")
            new_lines.append("\n")
            new_lines.append("        if \"pdf\" in content_type_lower or content_type_lower == \"application/pdf\":\n")
            new_lines.append("            return f\"[PDF Document] {content_str[:2000]}\\n\\n[Extracted content simulation]\"\n")
            new_lines.append("        elif \"docx\" in content_type_lower or \"doc\" in content_type_lower or \"application/vnd\" in content_type_lower:\n")
            new_lines.append("            return f\"[Word Document] {content_str[:2000]}\\n\\n[Extracted content simulation]\"\n")
            new_lines.append("        elif \"pptx\" in content_type_lower or \"ppt\" in content_type_lower or \"application/vnd\" in content_type_lower:\n")
            new_lines.append("            return f\"[PowerPoint] {content_str[:2000]}\\n\\n[Extracted content simulation]\"\n")
            new_lines.append("        elif \"json\" in content_type_lower or content_type_lower == \"application/json\":\n")
            new_lines.append("            return f\"[JSON File] {content_str[:2000]}\"\n")
            new_lines.append("        else:\n")
            new_lines.append("            return content_str[:2000]\n")
            replacement_done = True

if replacement_done:
    # Write the fixed file
    with open(path, "w") as f:
        f.writelines(new_lines)
    print("SUCCESS: Fixed _extract_text_from_bytes method")
else:
    print("ERROR: Could not find method to fix")
