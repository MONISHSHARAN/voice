#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - HTML Documentation Generator
Creates professional HTML documentation that can be converted to PDF
"""

import os
from datetime import datetime

def create_html_documentation():
    """Create professional HTML documentation"""
    
    # Read the enhanced documentation
    with open('MedAgg_Voice_Agent_Documentation_Enhanced.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML manually (simple conversion)
    html_content = markdown_content
    
    # Replace markdown syntax with HTML
    html_content = html_content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
    html_content = html_content.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
    html_content = html_content.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
    html_content = html_content.replace('#### ', '<h4>').replace('\n#### ', '</h4>\n<h4>')
    
    # Fix the last heading
    html_content = html_content.replace('</h1>', '</h1>', html_content.count('</h1>') - 1)
    html_content = html_content.replace('</h2>', '</h2>', html_content.count('</h2>') - 1)
    html_content = html_content.replace('</h3>', '</h3>', html_content.count('</h3>') - 1)
    html_content = html_content.replace('</h4>', '</h4>', html_content.count('</h4>') - 1)
    
    # Add closing tags for the last headings
    if html_content.count('<h1>') > html_content.count('</h1>'):
        html_content += '</h1>'
    if html_content.count('<h2>') > html_content.count('</h2>'):
        html_content += '</h2>'
    if html_content.count('<h3>') > html_content.count('</h3>'):
        html_content += '</h3>'
    if html_content.count('<h4>') > html_content.count('</h4>'):
        html_content += '</h4>'
    
    # Replace bold text
    html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
    
    # Replace italic text
    html_content = html_content.replace('*', '<em>').replace('*', '</em>')
    
    # Replace code blocks
    html_content = html_content.replace('```', '<pre><code>').replace('```', '</code></pre>')
    
    # Replace inline code
    html_content = html_content.replace('`', '<code>').replace('`', '</code>')
    
    # Replace line breaks
    html_content = html_content.replace('\n', '<br>\n')
    
    # Create complete HTML document with professional styling
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedAgg Healthcare Voice Agent - Technical Documentation</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
                background: #fff;
            }}
            
            h1 {{
                color: #2c5aa0;
                font-size: 2.5em;
                margin-bottom: 0.5em;
                border-bottom: 3px solid #4a90e2;
                padding-bottom: 0.3em;
                text-align: center;
            }}
            
            h2 {{
                color: #4a90e2;
                font-size: 1.8em;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
                border-left: 4px solid #4a90e2;
                padding-left: 0.5em;
            }}
            
            h3 {{
                color: #2c5aa0;
                font-size: 1.4em;
                margin-top: 1.2em;
                margin-bottom: 0.6em;
            }}
            
            h4 {{
                color: #666;
                font-size: 1.2em;
                margin-top: 1em;
                margin-bottom: 0.4em;
            }}
            
            .executive-summary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2em;
                border-radius: 10px;
                margin: 2em 0;
            }}
            
            .key-achievements {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 1.5em;
                margin: 1em 0;
            }}
            
            .key-achievements ul {{
                list-style: none;
                padding: 0;
            }}
            
            .key-achievements li {{
                padding: 0.5em 0;
                border-bottom: 1px solid #dee2e6;
            }}
            
            .key-achievements li:last-child {{
                border-bottom: none;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
                font-size: 0.9em;
            }}
            
            th {{
                background: #4a90e2;
                color: white;
                padding: 0.8em;
                text-align: left;
                font-weight: bold;
            }}
            
            td {{
                padding: 0.8em;
                border: 1px solid #dee2e6;
            }}
            
            tr:nth-child(even) {{
                background: #f8f9fa;
            }}
            
            .status-success {{
                color: #28a745;
                font-weight: bold;
            }}
            
            .status-warning {{
                color: #ffc107;
                font-weight: bold;
            }}
            
            .status-danger {{
                color: #dc3545;
                font-weight: bold;
            }}
            
            .code-block {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 1em;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                overflow-x: auto;
                margin: 1em 0;
            }}
            
            .highlight {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 1em;
                margin: 1em 0;
            }}
            
            .architecture-diagram {{
                text-align: center;
                margin: 2em 0;
                padding: 1em;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                background: #f8f9fa;
            }}
            
            .performance-metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1em;
                margin: 1em 0;
            }}
            
            .metric-card {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 1em;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #4a90e2;
            }}
            
            .metric-label {{
                color: #666;
                font-size: 0.9em;
                margin-top: 0.5em;
            }}
            
            .roadmap-phase {{
                background: white;
                border-left: 4px solid #4a90e2;
                padding: 1em;
                margin: 1em 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .competency-section {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 1.5em;
                margin: 1em 0;
            }}
            
            .competency-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1em;
                margin: 1em 0;
            }}
            
            .competency-item {{
                background: white;
                padding: 1em;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }}
            
            .footer {{
                margin-top: 3em;
                padding: 2em;
                background: #f8f9fa;
                border-radius: 8px;
                text-align: center;
                color: #666;
            }}
            
            .toc {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 1.5em;
                margin: 2em 0;
            }}
            
            .toc ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .toc li {{
                padding: 0.3em 0;
            }}
            
            .toc a {{
                text-decoration: none;
                color: #4a90e2;
            }}
            
            .toc a:hover {{
                text-decoration: underline;
            }}
            
            pre {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 1em;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            code {{
                background: #f8f9fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            strong {{
                font-weight: bold;
                color: #2c5aa0;
            }}
            
            em {{
                font-style: italic;
                color: #666;
            }}
            
            .print-instructions {{
                background: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 8px;
                padding: 1em;
                margin: 2em 0;
                text-align: center;
            }}
            
            .print-instructions h3 {{
                color: #1976d2;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <div class="print-instructions">
            <h3>📄 PDF Generation Instructions</h3>
            <p><strong>To convert this HTML to PDF:</strong></p>
            <p>1. Open this file in your web browser</p>
            <p>2. Press <strong>Ctrl+P</strong> (or Cmd+P on Mac)</p>
            <p>3. Select "Save as PDF" as the destination</p>
            <p>4. Choose "More settings" and select "A4" paper size</p>
            <p>5. Click "Save" to generate the PDF</p>
        </div>
        
        {html_content}
        
        <div class="footer">
            <h3>📄 Document Information</h3>
            <p><strong>Document Version:</strong> 1.0 | <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')} | <strong>Classification:</strong> Technical Architecture</p>
            <p><strong>Prepared By:</strong> MedAgg Healthcare Technology Team | <strong>Status:</strong> Production Ready</p>
            <p><em>This document represents the complete technical architecture and implementation details of the MedAgg Healthcare Voice Agent platform, demonstrating advanced technical competencies and innovative healthcare technology solutions.</em></p>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open('MedAgg_Voice_Agent_Documentation.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print("✅ Professional HTML documentation created successfully!")
    print("📄 File: MedAgg_Voice_Agent_Documentation.html")
    print("🎨 Features: Professional styling, tables, and technical specifications")
    print("📊 Instructions: Open in browser and use Ctrl+P to save as PDF")
    print("🔧 Alternative: Use any HTML-to-PDF converter for professional PDF generation")
    
    return True

if __name__ == "__main__":
    create_html_documentation()
