import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
import re

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_paragraph_runs(p, text, is_italic=False, default_color=None):
    # Parses bold **text** and italic *text* or _text_ inside the text
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_[^_]+?_)', text)
    for part in parts:
        if not part:
            continue
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        if default_color:
            run.font.color.rgb = default_color
            
        if part.startswith('**') and part.endswith('**'):
            run.text = part[2:-2]
            run.font.bold = True
            if is_italic:
                run.font.italic = True
        elif part.startswith('__') and part.endswith('__'):
            run.text = part[2:-2]
            run.font.bold = True
            if is_italic:
                run.font.italic = True
        elif part.startswith('*') and part.endswith('*'):
            run.text = part[1:-1]
            run.font.italic = True
        elif part.startswith('_') and part.endswith('_'):
            run.text = part[1:-1]
            run.font.italic = True
        else:
            run.text = part
            if is_italic:
                run.font.italic = True

def clean_latex_math(text):
    # Replacements of formulas
    text = text.replace(r'\[ z = \frac{x - \mu}{\sigma} \]', 'z = (x - μ) / σ')
    text = text.replace(r'z = \frac{x - \mu}{\sigma}', 'z = (x - μ) / σ')
    text = text.replace(r'\[z = \frac{x - \mu}{\sigma}\]', 'z = (x - μ) / σ')
    text = text.replace(r'\[ \sigma_{RSSI} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - RSSI\_avg)^2} \]', 'σ_RSSI = √[ 1/(N - 1) * Σ (RSSI_i - RSSI_avg)² ]')
    text = text.replace(r'\[ \sigma_{RSSI} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - RSSI_mean)^2} \]', 'σ_RSSI = √[ 1/(N - 1) * Σ (RSSI_i - RSSI_avg)² ]')
    
    # RSSI std dev formula
    text = text.replace(
        r'\sigma_{RSSI} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - \overline{RSSI})^2}', 
        'σ_RSSI = √[ 1/(N - 1) * Σ (RSSI_i - RSSI_avg)² ]'
    )
    text = text.replace(
        r'\(\sigma_{RSSI} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - \overline{RSSI})^2}\)',
        'σ_RSSI = √[ 1/(N - 1) * Σ (RSSI_i - RSSI_avg)² ]'
    )
    text = text.replace(
        r'\sigma_{RSSI} = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (RSSI_i - RSSI\_avg)^2}',
        'σ_RSSI = √[ 1/(N - 1) * Σ (RSSI_i - RSSI_avg)² ]'
    )
    text = text.replace(
        r'\sigma_{RSSI}', 'σ_RSSI'
    )
    
    # Inline symbols
    text = text.replace(r'\(\sigma_{RSSI}\)', 'σ_RSSI')
    text = text.replace(r'\(\mu\)', 'μ')
    text = text.replace(r'\mu', 'μ')
    text = text.replace(r'\(\sigma\)', 'σ')
    text = text.replace(r'\sigma', 'σ')
    text = text.replace(r'\(P_{rx}\)', 'P_rx')
    text = text.replace(r'P_{rx}', 'P_rx')
    text = text.replace(r'\(\pm\)', '±')
    text = text.replace(r'\pm', '±')
    text = text.replace(r'\(RSSI_i\)', 'RSSI_i')
    text = text.replace(r'\(\overline{RSSI}\)', 'RSSI_avg')
    text = text.replace(r'\overline{RSSI}', 'RSSI_avg')
    text = text.replace(r'\(N\)', 'N')
    text = text.replace(r'\(i\)', 'i')
    text = text.replace(r'\(x\)', 'x')
    text = text.replace(r'\(z\)', 'z')
    
    return text

def convert_md_to_docx(md_path, docx_path):
    if not os.path.exists(md_path):
        print(f"File not found: {md_path}")
        return
    
    doc = docx.Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_abstract = False
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = clean_latex_math(lines[i].strip())
        
        # Parse horizontal line
        if line == '---' or line == '***':
            i += 1
            continue
            
        # Parse title
        if line.startswith('# '):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(24)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(title_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
            i += 1
            continue
            
        # Parse Headings
        if line.startswith('## '):
            h_text = line[3:].strip()
            if 'ABSTRACT' in h_text.upper() or 'TÓM TẮT' in h_text.upper():
                in_abstract = True
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(h_text)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
            else:
                in_abstract = False
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(h_text)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
            i += 1
            continue
            
        if line.startswith('### '):
            h_text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(h_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x00, 0x55, 0x99)
            i += 1
            continue
            
        # Parse Bullet points
        if line.startswith('* ') or line.startswith('- '):
            bullet_text = line[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(4)
            add_paragraph_runs(p, bullet_text, is_italic=in_abstract)
            i += 1
            continue
            
        # Parse Blockquotes
        if line.startswith('> '):
            quote_text = line[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            pPr = p._p.get_or_add_pPr()
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F6F9" w:val="clear"/>')
            pPr.append(shading)
            add_paragraph_runs(p, quote_text, is_italic=True, default_color=RGBColor(0x33, 0x33, 0x33))
            i += 1
            continue
            
        # Parse Images
        if line.startswith('![') and ']' in line and '(' in line:
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if img_match:
                caption = img_match.group(1)
                img_path = img_match.group(2)
                if img_path.startswith('file:///'):
                    img_path = img_path.replace('file:///', '').replace('/', os.sep)
                
                # Check if exists in artifact dir or relative to it
                if not os.path.exists(img_path):
                    alt_path = os.path.join(os.path.dirname(md_path), os.path.basename(img_path))
                    if os.path.exists(alt_path):
                        img_path = alt_path
                    else:
                        print(f"Warning: Image file not found: {img_path}")
                        img_path = None
                
                if img_path and os.path.exists(img_path):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(12)
                    p_img.paragraph_format.space_after = Pt(4)
                    p_img.add_run().add_picture(img_path, width=Inches(5.5))
                    
                    p_cap = doc.add_paragraph()
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_cap.paragraph_format.space_after = Pt(12)
                    run_cap = p_cap.add_run(caption)
                    run_cap.font.name = 'Times New Roman'
                    run_cap.font.size = Pt(9.5)
                    run_cap.font.italic = True
                    run_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            i += 1
            continue
            
        # Parse Tables
        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(clean_latex_math(lines[i].strip()))
                i += 1
            
            if len(table_lines) >= 3:
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                data_rows = []
                for row_line in table_lines[2:]:
                    cells = [c.strip() for c in row_line.split('|')[1:-1]]
                    data_rows.append(cells)
                
                n_cols = len(headers)
                t = doc.add_table(rows=1 + len(data_rows), cols=n_cols)
                t.style = 'Table Grid'
                
                # Header
                hdr_cells = t.rows[0].cells
                for ci, val in enumerate(headers):
                    hdr_cells[ci].text = ""
                    p = hdr_cells[ci].paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run(val)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(9.5)
                    set_cell_background(hdr_cells[ci], "003366")
                    set_cell_margins(hdr_cells[ci])
                    
                # Data
                for ri, row_cells in enumerate(data_rows):
                    row = t.rows[ri + 1]
                    for ci, val in enumerate(row_cells):
                        row.cells[ci].text = ""
                        p = row.cells[ci].paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT
                        add_paragraph_runs(p, val)
                        p.runs[0].font.size = Pt(9.5)
                        set_cell_margins(row.cells[ci])
                        if ri % 2 == 1:
                            set_cell_background(row.cells[ci], "F2F5FA")
                            
                p_spacer = doc.add_paragraph()
                p_spacer.paragraph_format.space_before = Pt(6)
                p_spacer.paragraph_format.space_after = Pt(6)
            continue
            
        # Parse regular paragraphs
        if line:
            is_author = any(x in line for x in ["Tác giả:", "Đơn vị:", "Email:", "GitHub:"])
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            
            if is_author:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_paragraph_runs(p, line, is_italic=True)
                for r in p.runs:
                    r.font.size = Pt(10)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_paragraph_runs(p, line, is_italic=in_abstract)
                
            i += 1
            continue
            
        i += 1

    try:
        doc.save(docx_path)
        print(f"Successfully generated {docx_path}")
    except PermissionError:
        alt_path = docx_path.replace(".docx", "_temp.docx")
        try:
            doc.save(alt_path)
            print(f"Warning: Original file {docx_path} is open in Word. Saved to {alt_path} instead.")
        except Exception as e:
            print(f"Error: Could not save file. Details: {e}")

if __name__ == "__main__":
    workspace = r"c:\Users\LOQ\Downloads\PROJ-NWC"
    artifact_dir = r"C:\Users\LOQ\.gemini\antigravity\brain\6a0c6879-62b7-4136-91ea-1a69c47df162"
    
    convert_md_to_docx(
        os.path.join(artifact_dir, "huong_dan_du_an.md"),
        os.path.join(workspace, "Huong_Dan_Chi_Tiet_Du_An_RogueAP.docx")
    )
