#!/usr/bin/env python3
"""
Test script for the XML to 2D floor plan converter.
Tests the drawing engine with various XML files and configurations.
"""

import matplotlib.pyplot as plt
from xml_parser import SPSDocumentParser, SPSDocument, Page, Layer, Line, BlockReference
from drawing_engine import DrawingEngine, MatplotlibRenderer, create_floor_plan
import os

def test_simple_floor_plan():
    """Test with a simple floor plan creation."""
    print("Creating simple test floor plan...")
    
    # Create test layers
    layers = [
        Layer(name="CPWALL", color="7", off=False),
        Layer(name="CPDOOR", color="7", off=False)
    ]
    
    # Create test drawing elements
    elements = [
        Line(start_point=(0, 0), end_point=(1000, 0), layer="CPWALL", color="7"),
        Line(start_point=(1000, 0), end_point=(1000, 1000), layer="CPWALL", color="7"),
        Line(start_point=(1000, 1000), end_point=(0, 1000), layer="CPWALL", color="7"),
        Line(start_point=(0, 1000), end_point=(0, 0), layer="CPWALL", color="7"),
        BlockReference(name="CPDOOR1", position=(500, 0), layer="CPDOOR", color="7")
    ]
    
    # Create test page
    page = Page(title="Simple Test", scale="100", note="", layers=layers, drawing_elements=elements)
    
    # Create test document
    test_doc = SPSDocument(version="2.0", pages=[page])
    
    # Create floor plan
    fig = create_floor_plan(test_doc, title="Simple Test Floor Plan")
    fig.savefig("simple_test_floor_plan.png", dpi=300, bbox_inches='tight')
    print("Simple test floor plan saved to simple_test_floor_plan.png")
    
    return fig

def test_with_real_file(xml_file="test1.xml", page_index=None):
    """Test with a real XML file."""
    print(f"Now testing with {xml_file}")
    
    if not os.path.exists(xml_file):
        print(f"Error: File {xml_file} not found!")
        return None
    
    try:
        # Parse the XML file
        print(f"Parsing {xml_file}...")
        parser = SPSDocumentParser()
        doc = parser.parse_file(xml_file)
        
        print(f"Successfully parsed {len(doc.pages)} pages")
        for i, page in enumerate(doc.pages):
            print(f"  [{i}] Title: {page.title}")
        
        # Select page to render
        if page_index is not None and 0 <= page_index < len(doc.pages):
            selected_page = doc.pages[page_index]
            print(f"Using page {page_index}: {selected_page.title}")
        else:
            print("No page specified. Using first page.")
            selected_page = doc.pages[0]
        
        # Create a single-page document for rendering
        single_page_doc = SPSDocument(
            version=doc.version,
            pages=[selected_page]
        )
        
        # Create floor plan
        output_filename = f"{xml_file.replace('.xml', '')}_{selected_page.title}_floor_plan.png"
        fig = create_floor_plan(single_page_doc, output_filename, title=selected_page.title)
        
        print(f"Floor plan saved to {output_filename}")
        
        return fig
        
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_all_pages(xml_file="test1.xml"):
    """Test rendering all pages in the document."""
    print(f"Testing all pages in {xml_file}...")
    
    if not os.path.exists(xml_file):
        print(f"Error: File {xml_file} not found!")
        return
    
    try:
        parser = SPSDocumentParser()
        doc = parser.parse_file(xml_file)
        
        for i, page in enumerate(doc.pages):
            print(f"\nRendering page {i}: {page.title}")
            
            # Create single-page document
            single_page_doc = SPSDocument(version=doc.version, pages=[page])
            
            # Create floor plan
            output_filename = f"{xml_file.replace('.xml', '')}_page{i}_{page.title}_floor_plan.png"
            fig = create_floor_plan(single_page_doc, output_filename, title=f"{page.title} (Page {i})")
            
            print(f"Saved to {output_filename}")
            plt.close(fig)  # Close to free memory
            
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        import traceback
        traceback.print_exc()

def test_with_custom_layers(xml_file="test1.xml", visible_layers=None):
    """Test with custom layer filtering."""
    print(f"Testing {xml_file} with custom layer filtering...")
    
    if not os.path.exists(xml_file):
        print(f"Error: File {xml_file} not found!")
        return None
    
    try:
        parser = SPSDocumentParser()
        doc = parser.parse_file(xml_file)
        
        # Use first page
        page = doc.pages[0]
        single_page_doc = SPSDocument(version=doc.version, pages=[page])
        
        # Create floor plan with custom layers
        output_filename = f"{xml_file.replace('.xml', '')}_custom_layers_floor_plan.png"
        fig = create_floor_plan(single_page_doc, output_filename, title=f"{page.title} (Custom Layers)", visible_layers=visible_layers)
        
        print(f"Floor plan with custom layers saved to {output_filename}")
        return fig
        
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function."""
    print("Testing Drawing Engine")
    print("=" * 30)
    
    # Test 1: Simple floor plan
    try:
        test_simple_floor_plan()
    except Exception as e:
        print(f"Error in simple test: {e}")
    
    # Test 2: Real XML file (first page)
    try:
        test_with_real_file("test1.xml")
    except Exception as e:
        print(f"Error in real file test: {e}")
    
    # Test 3: Custom layer filtering
    try:
        # Test with only walls and doors
        test_with_custom_layers("test1.xml", visible_layers=["CPWALL", "CPDOOR"])
    except Exception as e:
        print(f"Error in custom layers test: {e}")
    
    print("\nAll tests completed!")
    print("Check the generated PNG files for results.")

if __name__ == "__main__":
    main() 