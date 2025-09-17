#!/usr/bin/env python3
"""
Create Professional PDF Documentation for MedAgg Voice Agent
Simple PDF generation without complex dependencies
"""

import os
import markdown
from datetime import datetime

def create_simple_pdf():
    """Create a simple PDF using HTML to PDF conversion"""
    
    # Read the enhanced documentation
    with open("MedAgg_Voice_Agent_Documentation_Enhanced.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'codehilite', 'fenced_code'])
    
    # Create professional HTML with CSS
    professional_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedAgg Healthcare Voice Agent - Professional Documentation</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                margin: -20px -20px 30px -20px;
                border-radius: 10px;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            
            .header .subtitle {{
                font-size: 1.2em;
                margin-top: 10px;
                opacity: 0.9;
            }}
            
            .header .date {{
                font-size: 0.9em;
                margin-top: 15px;
                opacity: 0.8;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #2c3e50;
                margin-top: 30px;
                margin-bottom: 15px;
            }}
            
            h1 {{
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            
            h2 {{
                border-bottom: 2px solid #e74c3c;
                padding-bottom: 8px;
            }}
            
            h3 {{
                color: #8e44ad;
                border-left: 4px solid #8e44ad;
                padding-left: 15px;
            }}
            
            .feature-box {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                border-left: 5px solid #28a745;
            }}
            
            .tech-spec {{
                background: #e3f2fd;
                border: 1px solid #bbdefb;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }}
            
            .architecture-diagram {{
                text-align: center;
                background: #fff3e0;
                border: 2px solid #ff9800;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .code-block {{
                background: #f4f4f4;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                overflow-x: auto;
                margin: 15px 0;
            }}
            
            .highlight {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }}
            
            .warning {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                color: #721c24;
            }}
            
            .success {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                color: #155724;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            
            th {{
                background: #f8f9fa;
                font-weight: bold;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #eee;
                color: #666;
                font-size: 0.9em;
            }}
            
            .toc {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .toc h3 {{
                margin-top: 0;
                color: #495057;
            }}
            
            .toc ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            
            .toc li {{
                margin: 8px 0;
            }}
            
            .toc a {{
                text-decoration: none;
                color: #007bff;
            }}
            
            .toc a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 MedAgg Healthcare Voice Agent</h1>
            <div class="subtitle">Advanced Cardiology AI Voice Agent with Deepgram Agent API</div>
            <div class="date">Professional Documentation - {datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        
        <div class="toc">
            <h3>📋 Table of Contents</h3>
            <ul>
                <li><a href="#overview">1. System Overview</a></li>
                <li><a href="#architecture">2. Technical Architecture</a></li>
                <li><a href="#features">3. Key Features & Capabilities</a></li>
                <li><a href="#workflow">4. Conversation Workflow</a></li>
                <li><a href="#integration">5. Integration Details</a></li>
                <li><a href="#deployment">6. Deployment & Configuration</a></li>
                <li><a href="#performance">7. Performance Metrics</a></li>
                <li><a href="#business">8. Business Impact & ROI</a></li>
                <li><a href="#future">9. Future Roadmap</a></li>
                <li><a href="#technical">10. Technical Competencies</a></li>
            </ul>
        </div>
        
        {html_content}
        
        <div class="footer">
            <p><strong>MedAgg Healthcare Voice Agent</strong> - Professional Documentation</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>© 2024 MedAgg Healthcare. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    html_filename = "MedAgg_Voice_Agent_Documentation_Professional.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(professional_html)
    
    print(f"✅ Professional HTML documentation created: {html_filename}")
    print("📄 You can now:")
    print("   1. Open the HTML file in your browser")
    print("   2. Use 'Print to PDF' to create a professional PDF")
    print("   3. Or use online HTML to PDF converters")
    
    # Create a simple text version for easy reading
    text_filename = "MedAgg_Voice_Agent_Documentation_Simple.txt"
    with open("MedAgg_Voice_Agent_Documentation_Enhanced.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Convert markdown to simple text
    import re
    text_content = re.sub(r'#+ ', '', markdown_content)  # Remove markdown headers
    text_content = re.sub(r'\*\*(.*?)\*\*', r'\1', text_content)  # Remove bold
    text_content = re.sub(r'\*(.*?)\*', r'\1', text_content)  # Remove italic
    text_content = re.sub(r'`(.*?)`', r'\1', text_content)  # Remove code backticks
    text_content = re.sub(r'```.*?\n', '', text_content, flags=re.DOTALL)  # Remove code blocks
    
    with open(text_filename, "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print(f"✅ Simple text documentation created: {text_filename}")
    
    return html_filename, text_filename

if __name__ == "__main__":
    print("🏥 MedAgg Healthcare Voice Agent - Professional Documentation Generator")
    print("=" * 70)
    
    try:
        html_file, text_file = create_simple_pdf()
        print("\n🎉 Documentation generation completed successfully!")
        print(f"📄 Professional HTML: {html_file}")
        print(f"📄 Simple Text: {text_file}")
        print("\n💡 To create PDF:")
        print("   1. Open the HTML file in Chrome/Edge")
        print("   2. Press Ctrl+P (Print)")
        print("   3. Select 'Save as PDF'")
        print("   4. Choose 'More settings' → 'Options' → 'Background graphics'")
        print("   5. Save as 'MedAgg_Voice_Agent_Documentation.pdf'")
        
    except Exception as e:
        print(f"❌ Error creating documentation: {e}")
        print("Please ensure the enhanced markdown file exists.")
