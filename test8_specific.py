#!/usr/bin/env python3
"""
Test script specifically for test8.xml to verify CPDOOR2 positioning fixes.
"""

import matplotlib.pyplot as plt
from xml_parser import SPSDocumentParser, SPSDocument
from drawing_engine import create_floor_plan

def test_test8():
    """Test with test8.xml specifically."""
    print("Testing test8.xml with CPDOOR2 fixes...")
    
    try:
        # Parse the XML file
        print("Parsing test8.xml...")
        parser = SPSDocumentParser()
        doc = parser.parse_file("test8.xml")
        
        print(f"Successfully parsed {len(doc.pages)} pages")
        for i, page in enumerate(doc.pages):
            print(f"  [{i}] Title: {page.title}")
        
        # Use first page
        selected_page = doc.pages[0]
        print(f"Using page 0: {selected_page.title}")
        
        # Create a single-page document for rendering
        single_page_doc = SPSDocument(
            version=doc.version,
            pages=[selected_page]
        )
        
        # Create floor plan
        output_filename = "test8_fixed_floor_plan.png"
        fig = create_floor_plan(single_page_doc, output_filename, title=selected_page.title)
        
        print(f"Floor plan saved to {output_filename}")
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"Error processing test8.xml: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_test8() 