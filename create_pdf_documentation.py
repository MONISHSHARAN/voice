#!/usr/bin/env python3
"""
MedAgg Healthcare Voice Agent - PDF Documentation Generator
Creates professional PDF documentation with enhanced formatting
"""

import os
import sys
from datetime import datetime

def create_pdf_documentation():
    """Create professional PDF documentation"""
    
    try:
        # Try to import required libraries
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        print("❌ Required libraries not found. Installing...")
        os.system("pip install markdown weasyprint")
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    
    # Read the enhanced documentation
    with open('MedAgg_Voice_Agent_Documentation_Enhanced.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_content = md.convert(markdown_content)
    
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
                @top-center {{
                    content: "MedAgg Healthcare Voice Agent - Technical Documentation";
                    font-size: 10pt;
                    color: #666;
                }}
                @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }}
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            
            h1 {{
                color: #2c5aa0;
                font-size: 2.5em;
                margin-bottom: 0.5em;
                border-bottom: 3px solid #4a90e2;
                padding-bottom: 0.3em;
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
        </style>
    </head>
    <body>
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
    
    # Create PDF
    font_config = FontConfiguration()
    html_doc = HTML(string=full_html)
    
    print("🔄 Generating PDF documentation...")
    html_doc.write_pdf('MedAgg_Voice_Agent_Documentation.pdf', font_config=font_config)
    
    print("✅ Professional PDF documentation created successfully!")
    print("📄 File: MedAgg_Voice_Agent_Documentation.pdf")
    print("🎨 Features: Professional styling, tables, diagrams, and technical specifications")
    print("📊 Pages: Comprehensive technical documentation with visual elements")
    
    return True

if __name__ == "__main__":
    create_pdf_documentation()
