import unittest
import xml.etree.ElementTree as ET
from xml_parser import SPSDocumentParser, DrawingElement, Layer, Page
import tempfile
import os

class TestSPSDocumentParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = SPSDocumentParser()
        
        # Create a minimal test XML file
        self.test_xml_content = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="Test Page" scale="100" note="">
         <Database>
            <LayerTable>
               <Layer name="CPWALL" color="2" off="false"/>
               <Layer name="CPDOOR" color="4" off="false"/>
               <Layer name="CPTEXT" color="3" off="false"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE" origin="0,0">
                  <Line spt="100,100" ept="200,100" layer="CPWALL" color="2"/>
                  <Line spt="200,100" ept="200,200" layer="CPWALL" color="2"/>
                  <Line spt="200,200" ept="100,200" layer="CPWALL" color="2"/>
                  <Line spt="100,200" ept="100,100" layer="CPWALL" color="2"/>
                  <BlockReference name="CPDOOR1" position="150,100" angle="0" scale="1,1" layer="CPDOOR" color="4"/>
                  <Text font="Arial" position="150,150" height="10" text="Room 101" angle="0" layer="CPTEXT" color="3"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(self.test_xml_content)
            self.test_file_path = f.name

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, 'test_file_path') and os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)

    def test_parse_basic_structure(self):
        """Test that the parser can read basic SPSDocument structure."""
        result = self.parser.parse_file(self.test_file_path)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.version, "2.0")
        self.assertEqual(len(result.pages), 1)
        
        page = result.pages[0]
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.scale, "100")
        self.assertEqual(page.note, "")

    def test_parse_layers(self):
        """Test that layers are correctly parsed."""
        result = self.parser.parse_file(self.test_file_path)
        page = result.pages[0]
        
        self.assertEqual(len(page.layers), 3)
        
        # Check layer properties
        wall_layer = next(layer for layer in page.layers if layer.name == "CPWALL")
        self.assertEqual(wall_layer.color, "2")
        self.assertFalse(wall_layer.off)
        
        door_layer = next(layer for layer in page.layers if layer.name == "CPDOOR")
        self.assertEqual(door_layer.color, "4")
        self.assertFalse(door_layer.off)

    def test_parse_drawing_elements(self):
        """Test that drawing elements are correctly parsed."""
        result = self.parser.parse_file(self.test_file_path)
        page = result.pages[0]
        
        # Should have 4 lines, 1 block reference, 1 text
        self.assertEqual(len(page.drawing_elements), 6)
        
        # Check lines
        lines = [elem for elem in page.drawing_elements if elem.element_type == "Line"]
        self.assertEqual(len(lines), 4)
        
        # Check first line coordinates
        first_line = lines[0]
        self.assertEqual(first_line.start_point, (100, 100))
        self.assertEqual(first_line.end_point, (200, 100))
        self.assertEqual(first_line.layer, "CPWALL")
        
        # Check block references
        blocks = [elem for elem in page.drawing_elements if elem.element_type == "BlockReference"]
        self.assertEqual(len(blocks), 1)
        
        block = blocks[0]
        self.assertEqual(block.name, "CPDOOR1")
        self.assertEqual(block.position, (150, 100))
        self.assertEqual(block.layer, "CPDOOR")
        
        # Check text
        texts = [elem for elem in page.drawing_elements if elem.element_type == "Text"]
        self.assertEqual(len(texts), 1)
        
        text = texts[0]
        self.assertEqual(text.text, "Room 101")
        self.assertEqual(text.position, (150, 150))
        self.assertEqual(text.font, "Arial")
        self.assertEqual(text.height, 10)

    def test_convert_to_standard_xml(self):
        """Test conversion to standard XML format."""
        result = self.parser.parse_file(self.test_file_path)
        standard_xml = self.parser.convert_to_standard_xml(result)
        
        # Parse the standard XML
        root = ET.fromstring(standard_xml)
        
        # Check structure
        self.assertEqual(root.tag, "floorplan")
        self.assertEqual(root.get("version"), "2.0")
        
        # Check pages
        pages = root.findall("page")
        self.assertEqual(len(pages), 1)
        
        page = pages[0]
        self.assertEqual(page.get("title"), "Test Page")
        self.assertEqual(page.get("scale"), "100")
        
        # Check layers
        layers = page.findall("layers/layer")
        self.assertEqual(len(layers), 3)
        
        # Check elements
        elements = page.findall("elements/element")
        self.assertEqual(len(elements), 6)

    def test_parse_coordinates(self):
        """Test coordinate parsing from string format."""
        coords = self.parser.parse_coordinates("100.5,200.75")
        self.assertEqual(coords, (100.5, 200.75))
        
        coords = self.parser.parse_coordinates("0,0")
        self.assertEqual(coords, (0, 0))
        
        coords = self.parser.parse_coordinates("-123.456,789.012")
        self.assertEqual(coords, (-123.456, 789.012))

    def test_parse_real_file(self):
        """Test parsing one of the actual XML files."""
        if os.path.exists("test4.xml"):
            result = self.parser.parse_file("test4.xml")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.version, "2.0")
            self.assertGreater(len(result.pages), 0)
            
            # Check that we can convert to standard XML
            standard_xml = self.parser.convert_to_standard_xml(result)
            self.assertIsInstance(standard_xml, str)
            self.assertIn("<floorplan", standard_xml)

    def test_handle_missing_attributes(self):
        """Test handling of missing optional attributes."""
        incomplete_xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="Test" scale="100">
         <Database>
            <LayerTable>
               <Layer name="CPWALL" color="2"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE">
                  <Line spt="100,100" ept="200,100" layer="CPWALL"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(incomplete_xml)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            self.assertIsNotNone(result)
            self.assertEqual(len(result.pages), 1)
            
            page = result.pages[0]
            self.assertEqual(page.title, "Test")
            self.assertEqual(page.scale, "100")
            self.assertEqual(page.note, "")  # Should default to empty string
            
            self.assertEqual(len(page.drawing_elements), 1)
            line = page.drawing_elements[0]
            self.assertEqual(line.layer, "CPWALL")
            self.assertEqual(line.color, "")  # Should default to empty string
        finally:
            os.unlink(temp_file)

    def test_export_for_matplotlib(self):
        """Test export of data suitable for matplotlib plotting."""
        result = self.parser.parse_file(self.test_file_path)
        plot_data = self.parser.export_for_matplotlib(result)
        
        self.assertIsInstance(plot_data, dict)
        self.assertIn("pages", plot_data)
        self.assertIn("layers", plot_data)
        
        page_data = plot_data["pages"][0]
        self.assertIn("lines", page_data)
        self.assertIn("texts", page_data)
        self.assertIn("blocks", page_data)
        
        # Check that coordinates are in the right format for matplotlib
        lines = page_data["lines"]
        self.assertGreater(len(lines), 0)
        
        for line in lines:
            self.assertIn("x", line)
            self.assertIn("y", line)
            self.assertIn("layer", line)
            self.assertIn("color", line)

    def test_parse_circle_and_arc(self):
        """Test parsing of Circle and Arc elements."""
        xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="CircleArcTest" scale="100" note="">
         <Database>
            <LayerTable>
               <Layer name="CIRCLE" color="5"/>
               <Layer name="ARC" color="6"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE" origin="0,0">
                  <Circle center="10,20" radius="5" layer="CIRCLE" color="5"/>
                  <Arc center="30,40" radius="10" startAng="0" endAng="1.57" layer="ARC" color="6"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            page = result.pages[0]
            circles = [e for e in page.drawing_elements if getattr(e, 'element_type', None) == 'Circle']
            arcs = [e for e in page.drawing_elements if getattr(e, 'element_type', None) == 'Arc']
            self.assertEqual(len(circles), 1)
            self.assertEqual(len(arcs), 1)
            self.assertEqual(circles[0].center, (10, 20))
            self.assertEqual(circles[0].radius, 5)
            self.assertEqual(arcs[0].center, (30, 40))
            self.assertEqual(arcs[0].radius, 10)
            self.assertEqual(arcs[0].start_angle, 0)
            self.assertEqual(arcs[0].end_angle, 1.57)
        finally:
            os.unlink(temp_file)

    def test_parse_multiple_pages_and_layers(self):
        """Test parsing of multiple pages and layers."""
        xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="Page1" scale="100" note="">
         <Database>
            <LayerTable>
               <Layer name="L1" color="1"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE" origin="0,0">
                  <Line spt="0,0" ept="1,1" layer="L1" color="1"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
      <Page title="Page2" scale="200" note="Second">
         <Database>
            <LayerTable>
               <Layer name="L2" color="2"/>
               <Layer name="L3" color="3"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE" origin="0,0">
                  <Line spt="2,2" ept="3,3" layer="L2" color="2"/>
                  <Line spt="4,4" ept="5,5" layer="L3" color="3"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            self.assertEqual(len(result.pages), 2)
            self.assertEqual(result.pages[0].title, "Page1")
            self.assertEqual(result.pages[1].title, "Page2")
            self.assertEqual(len(result.pages[0].layers), 1)
            self.assertEqual(len(result.pages[1].layers), 2)
            self.assertEqual(len(result.pages[0].drawing_elements), 1)
            self.assertEqual(len(result.pages[1].drawing_elements), 2)
        finally:
            os.unlink(temp_file)

    def test_parse_unsupported_element(self):
        """Test that unsupported elements are ignored and do not break parsing."""
        xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="Test" scale="100">
         <Database>
            <LayerTable>
               <Layer name="CPWALL" color="2"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE">
                  <Line spt="100,100" ept="200,100" layer="CPWALL"/>
                  <Unsupported foo="bar"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            page = result.pages[0]
            self.assertEqual(len(page.drawing_elements), 1)
            self.assertEqual(page.drawing_elements[0].element_type, "Line")
        finally:
            os.unlink(temp_file)

    def test_parse_polyline_ignored(self):
        """Test that Polyline elements are currently ignored (not parsed as lines)."""
        xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<SPSDocument version="2.0">
   <Pages>
      <Page title="Test" scale="100">
         <Database>
            <LayerTable>
               <Layer name="CPWALL" color="2"/>
            </LayerTable>
            <BlockTable>
               <Block name="*MODEL_SPACE">
                  <Polyline num="3" vertices="0,0,1,1,2,2" layer="CPWALL" color="2"/>
               </Block>
            </BlockTable>
         </Database>
      </Page>
   </Pages>
</SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            page = result.pages[0]
            self.assertEqual(len(page.drawing_elements), 0)
        finally:
            os.unlink(temp_file)

    def test_parse_empty_file(self):
        """Test parsing an empty file raises an error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            temp_file = f.name
        try:
            with self.assertRaises(ET.ParseError):
                self.parser.parse_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_parse_missing_file(self):
        """Test parsing a missing file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("nonexistent_file.xml")

    def test_malformed_xml_missing_closing_tag(self):
        """Test that missing closing tags raise a ParseError."""
        malformed = '''<SPSDocument version="2.0"><Pages><Page title="Bad" scale="100"><Database>'''  # No closing tags
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(malformed)
            temp_file = f.name
        try:
            with self.assertRaises(ET.ParseError):
                self.parser.parse_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_extreme_coordinates(self):
        """Test parsing of elements with extreme coordinate values."""
        xml = '''<SPSDocument version="2.0"><Pages><Page title="Extreme" scale="100"><Database><LayerTable><Layer name="L" color="1"/></LayerTable><BlockTable><Block name="*MODEL_SPACE"><Line spt="-1e10,1e10" ept="1e-10,-1e-10" layer="L" color="1"/></Block></BlockTable></Database></Page></Pages></SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            line = result.pages[0].drawing_elements[0]
            self.assertEqual(line.start_point, (-1e10, 1e10))
            self.assertEqual(line.end_point, (1e-10, -1e-10))
        finally:
            os.unlink(temp_file)

    def test_special_characters_and_unicode(self):
        """Test parsing of special characters and Unicode in attributes and text."""
        xml = '''<SPSDocument version="2.0"><Pages><Page title="특수문자 &amp; 漢字" scale="100"><Database><LayerTable><Layer name="L&amp;&lt;&gt;" color="1"/></LayerTable><BlockTable><Block name="*MODEL_SPACE"><Text font="Arial" position="0,0" height="10" text="안녕하세요 &amp; Hello 漢字" angle="0" layer="L&amp;&lt;&gt;" color="1"/></Block></BlockTable></Database></Page></Pages></SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            page = result.pages[0]
            self.assertIn("특수문자", page.title)
            self.assertIn("漢字", page.title)
            self.assertEqual(page.layers[0].name, "L&<>")
            text = page.drawing_elements[0]
            self.assertIn("안녕하세요", text.text)
            self.assertIn("漢字", text.text)
        finally:
            os.unlink(temp_file)

    def test_unknown_tags_and_attributes(self):
        """Test that unknown tags and attributes are ignored gracefully."""
        xml = '''<SPSDocument version="2.0"><Pages><Page title="Unknowns" scale="100" foo="bar"><Database><LayerTable><Layer name="L" color="1" unknown="yes"/></LayerTable><BlockTable><Block name="*MODEL_SPACE"><Line spt="0,0" ept="1,1" layer="L" color="1"/><Mystery attr="?"/></Block></BlockTable></Database></Page></Pages></SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            self.assertEqual(result.pages[0].title, "Unknowns")
            self.assertEqual(result.pages[0].layers[0].name, "L")
            self.assertEqual(len(result.pages[0].drawing_elements), 1)
        finally:
            os.unlink(temp_file)

    def test_boolean_variants(self):
        """Test all string representations for booleans in 'off' attribute."""
        for val, expected in [("true", True), ("True", True), ("TRUE", True), ("false", False), ("False", False), ("FALSE", False), ("0", False), ("1", False)]:
            xml = f'''<SPSDocument version="2.0"><Pages><Page title="Bool" scale="100"><Database><LayerTable><Layer name="L" color="1" off="{val}"/></LayerTable></Database></Page></Pages></SPSDocument>'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml)
                temp_file = f.name
            try:
                result = self.parser.parse_file(temp_file)
                self.assertEqual(result.pages[0].layers[0].off, expected)
            finally:
                os.unlink(temp_file)

    def test_version_compatibility(self):
        """Test parsing of different SPSDocument versions."""
        for version in ["1.0", "2.0", "2.1", "unknown"]:
            xml = f'''<SPSDocument version="{version}"><Pages><Page title="Ver" scale="100"><Database><LayerTable><Layer name="L" color="1"/></LayerTable></Database></Page></Pages></SPSDocument>'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml)
                temp_file = f.name
            try:
                result = self.parser.parse_file(temp_file)
                self.assertEqual(result.version, version)
            finally:
                os.unlink(temp_file)

    def test_round_trip_conversion(self):
        """Test that parsing and converting to standard XML and back preserves data."""
        xml = '''<SPSDocument version="2.0"><Pages><Page title="RoundTrip" scale="100"><Database><LayerTable><Layer name="L" color="1"/></LayerTable><BlockTable><Block name="*MODEL_SPACE"><Line spt="0,0" ept="1,1" layer="L" color="1"/></Block></BlockTable></Database></Page></Pages></SPSDocument>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            temp_file = f.name
        try:
            result = self.parser.parse_file(temp_file)
            std_xml = self.parser.convert_to_standard_xml(result)
            # Parse the standard XML and check for expected tags/attributes
            root = ET.fromstring(std_xml)
            self.assertEqual(root.tag, "floorplan")
            page = root.find("page")
            self.assertIsNotNone(page)
            self.assertEqual(page.get("title"), "RoundTrip")
            layers = page.find("layers")
            self.assertIsNotNone(layers)
            elements = page.find("elements")
            self.assertIsNotNone(elements)
            line_elem = elements.find("element[@type='Line']")
            self.assertIsNotNone(line_elem)
            self.assertEqual(line_elem.get("start_x"), "0.0")
            self.assertEqual(line_elem.get("end_y"), "1.0")
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main() 