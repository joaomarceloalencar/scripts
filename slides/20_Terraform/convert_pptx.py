import os
import pptx
from pptx.enum.shapes import MSO_SHAPE_TYPE
import re
import cairosvg
from io import BytesIO

# Configuration
files = [
    {"path": "01_IaaC.pptx", "prefix": "iaac", "start_slide": 1, "end_slide": 14}, # 0-indexed: start_slide 1 means slide 2
    {"path": "02_TerraForm.pptx", "prefix": "terraform", "start_slide": 1, "end_slide": 15}
]
output_file = "IaaC_Terraform.tex"
image_dir = "images"

# Ensure image directory exists
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

def escape_latex(text):
    if not text:
        return ""
    
    # Remove vertical tabs and other control characters that might cause issues
    text = text.replace('\x0b', ' ').replace('\x0c', ' ')
    
    replacements = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '%': r'\%',
        '$': r'\$',
        '&': r'\&',
        '#': r'\#',
        '_': r'\_',
        '^': r'\^{}',
        '~': r'\~{}'
    }
    # Simple way to escape, avoiding double escaping if possible, but safe approach
    # We iterate character by character or use regex
    # But for simplicity and robustness:
    result = ""
    for char in text:
        if char in replacements:
            result += replacements[char]
        else:
            result += char
    return result

def is_code_font(font_name):
    if not font_name:
        return False
    mono_fonts = ['Courier', 'Courier New', 'Consolas', 'Menlo', 'Monaco', 'Lucida Console', 'Inconsolata']
    return any(f.lower() in font_name.lower() for f in mono_fonts)

def get_slide_content(slide, prefix, slide_idx):
    title_text = ""
    if slide.shapes.title:
        title_text = slide.shapes.title.text_frame.text
    
    content_latex = []
    images_latex = []
    
    # Analyze shapes
    # We want to process text frames and pictures
    # Sorting shapes by position (top-to-bottom, left-to-right) might be good, 
    # but usually the reading order is roughly creation order or grouped.
    # Let's simple iterate.
    
    shapes = sorted(slide.shapes, key=lambda s: (s.top if hasattr(s, 'top') else 0, s.left if hasattr(s, 'left') else 0))
    
    for shape in shapes:
        if shape == slide.shapes.title:
            continue
            
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                image = shape.image
                image_bytes = image.blob
                ext = image.ext
                filename = f"{prefix}_{slide_idx}_{shape.shape_id}.{ext}"
                filepath = os.path.join(image_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                # Convert SVG to PNG if necessary
                if ext == 'svg':
                    png_filename = f"{prefix}_{slide_idx}_{shape.shape_id}.png"
                    png_filepath = os.path.join(image_dir, png_filename)
                    try:
                        cairosvg.svg2png(url=filepath, write_to=png_filepath)
                        filename = png_filename
                    except Exception as e:
                        print(f"Failed to convert SVG {filename}: {e}")
                
                # Check formatting
                # We'll center images and scale them
                # Adjust width based on shape width relative to slide width?
                # pptx units are EMUs (914400 per inch). Slide width is typically 10 inches (9144000).
                # But LaTeX \textwidth is different.
                # A safe bet is width=0.8\textwidth or similar.
                
                images_latex.append(r"\begin{center}\includegraphics[width=0.7\textwidth,height=0.6\textheight,keepaspectratio]{" + f"images/{filename}" + r"}\end{center}")
            except Exception as e:
                print(f"Error extracting image: {e}")

        elif shape.has_text_frame:
            text_frame = shape.text_frame
            # Check if this is likely code block
            # Heuristic: Check if majority of runs are mono font
            all_runs = []
            for p in text_frame.paragraphs:
                all_runs.extend(p.runs)
            
            is_code_block = False
            if all_runs:
                mono_count = sum(1 for r in all_runs if is_code_font(r.font.name))
                if mono_count / len(all_runs) > 0.8:
                    is_code_block = True
            
            if is_code_block:
                # Concatenate all text
                full_text = text_frame.text.replace('\x0b', ' ').replace('\x0c', ' ')
                content_latex.append(r"\begin{minted}{bash}")
                content_latex.append(full_text)
                content_latex.append(r"\end{minted}")
            else:
                # It's a list (bullet points)
                # We need to handle nesting
                current_level = 0
                list_open = False
                
                # Buffer for itemize environment
                list_buffer = []
                
                for p in text_frame.paragraphs:
                    text = p.text.strip()
                    if not text:
                        continue
                        
                    level = p.level + 1 # 1-based level
                    
                    # Handle level changes
                    while current_level < level:
                        list_buffer.append(r"\begin{itemize}")
                        current_level += 1
                    while current_level > level:
                        list_buffer.append(r"\end{itemize}")
                        current_level -= 1
                    
                    # Process text runs for formatting (bold, italic)
                    formatted_text = ""
                    for run in p.runs:
                        run_text = escape_latex(run.text)
                        if run.font.bold:
                            run_text = r"\textbf{" + run_text + "}"
                        if run.font.italic:
                            run_text = r"\textit{" + run_text + "}"
                        if is_code_font(run.font.name):
                            run_text = r"\texttt{" + run_text + "}"
                        formatted_text += run_text
                    
                    list_buffer.append(r"\item " + formatted_text)
                
                # Close remaining levels
                while current_level > 0:
                    list_buffer.append(r"\end{itemize}")
                    current_level -= 1
                    
                if list_buffer:
                    content_latex.extend(list_buffer)

    return title_text, content_latex, images_latex

def main():
    # Preamble from aws.tex
    latex_content = [
        r"\documentclass{beamer}",
        r"",
        r"\usepackage[portuguese]{babel}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{minted}",
        r"\usepackage{graphicx}", # Ensure graphicx is included
        r"\setbeamertemplate{footline}[frame number]",
        r"",
        # Title will be extracted from first presentation
    ]

    # Process first presentation to get main title
    prs1 = pptx.Presentation(files[0]["path"])
    title_slide = prs1.slides[0]
    main_title = "Apresentação"
    if title_slide.shapes.title:
        main_title = escape_latex(title_slide.shapes.title.text_frame.text)
    
    latex_content.append(r"\title{" + main_title + "}")
    latex_content.append(r"\author[João Marcelo Uchôa de Alencar]{João Marcelo Uchôa de Alencar}") # Keeping from template
    latex_content.append(r"\institute{Universidade Federal do Ceará - Quixadá}") # Keeping from template
    latex_content.append(r"")
    latex_content.append(r"\begin{document}")
    latex_content.append(r"   \begin{frame}")
    latex_content.append(r"      \titlepage")
    latex_content.append(r"   \end{frame}")

    # Process files
    for i, file_info in enumerate(files):
        print(f"Processing {file_info['path']}...")
        prs = pptx.Presentation(file_info['path'])
        
        # Add transition slide if it's the second presentation
        if i == 1:
            latex_content.append(r"")
            latex_content.append(r"   \begin{frame}")
            latex_content.append(r"      \centering")
            latex_content.append(r"      \Huge \textbf{Parte 2: Terraform}")
            latex_content.append(r"   \end{frame}")
            latex_content.append(r"")

        start = file_info["start_slide"]
        end = file_info["end_slide"]
        
        # Iterate relevant slides
        # Note: slides are 0-indexed in pptx list, but config used 0-indexed logic in my comments?
        # Let's check logic: "start_slide": 1 (means skip first slide, index 0).
        # "end_slide": 14 (means process up to index 13). 
        # range(1, 14) -> 1, 2... 13.
        
        # Adjust end limit if needed
        limit = min(end, len(prs.slides))
        
        for slide_idx in range(start, limit):
            slide = prs.slides[slide_idx]
            print(f"  Processing slide {slide_idx+1}")
            
            title, content, images = get_slide_content(slide, file_info["prefix"], slide_idx)
            
            # Determine if fragile is needed (for minted)
            is_fragile = any("minted" in line for line in content)
            frame_opts = "[fragile]" if is_fragile else ""
            
            latex_content.append(r"")
            latex_content.append(r"   \begin{frame}" + frame_opts)
            if title:
                latex_content.append(r"      \frametitle{" + escape_latex(title) + "}")
            
            # Add content
            for line in content:
                latex_content.append(r"      " + line)
            
            # Add images
            for img in images:
                latex_content.append(r"      " + img)
                
            latex_content.append(r"   \end{frame}")

    latex_content.append(r"")
    latex_content.append(r"\end{document}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    main()
