#!/usr/bin/env python3
"""
Debug script to print all elements near the bottom left of the floor plan in test8.xml.
"""

from xml_parser import SPSDocumentParser

# Define the region of interest (bottom left)
X_MAX = 10000
Y_MIN = 20000

def debug_bottom_left():
    parser = SPSDocumentParser()
    doc = parser.parse_file("test8.xml")
    page = doc.pages[0]
    print(f"Page title: {page.title}")
    print("\nElements near bottom left (x < 10000, y > 20000):\n")
    for elem in page.drawing_elements:
        pos = None
        if hasattr(elem, 'position'):
            pos = elem.position
        elif hasattr(elem, 'start_point'):
            pos = elem.start_point
        if pos:
            x, y = pos[0], pos[1]
            if x < X_MAX and y > Y_MIN:
                print(f"Type: {type(elem).__name__}, Pos: {pos}, Layer: {getattr(elem, 'layer', None)}, Name: {getattr(elem, 'name', None)}")
                if hasattr(elem, 'end_point'):
                    print(f"  End: {elem.end_point}")
                if hasattr(elem, 'scale'):
                    print(f"  Scale: {elem.scale}")
                if hasattr(elem, 'angle'):
                    print(f"  Angle: {elem.angle}")
                if hasattr(elem, 'matrix'):
                    print(f"  Matrix: {elem.matrix}")
    print("\nDone.")

if __name__ == "__main__":
    debug_bottom_left() 