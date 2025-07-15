import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import os

@dataclass
class Layer:
    """Represents a drawing layer."""
    name: str
    color: str
    off: bool = False

@dataclass
class DrawingElement:
    """Base class for all drawing elements."""
    element_type: str
    layer: str
    color: str = ""

@dataclass
class Line:
    """Represents a line element."""
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    element_type: str = "Line"
    layer: str = ""
    color: str = ""

@dataclass
class BlockReference:
    """Represents a block reference (door, window, etc.)."""
    name: str
    position: Tuple[float, float]
    angle: float = 0.0
    scale: Tuple[float, float] = (1.0, 1.0)
    element_type: str = "BlockReference"
    layer: str = ""
    color: str = ""

@dataclass
class Text:
    """Represents a text element."""
    text: str
    position: Tuple[float, float]
    font: str = ""
    height: float = 10.0
    angle: float = 0.0
    element_type: str = "Text"
    layer: str = ""
    color: str = ""

@dataclass
class Circle:
    """Represents a circle element."""
    center: Tuple[float, float]
    radius: float
    element_type: str = "Circle"
    layer: str = ""
    color: str = ""

@dataclass
class Arc:
    """Represents an arc element."""
    center: Tuple[float, float]
    radius: float
    start_angle: float
    end_angle: float
    element_type: str = "Arc"
    layer: str = ""
    color: str = ""

@dataclass
class Page:
    """Represents a drawing page."""
    title: str
    scale: str
    note: str
    layers: List[Layer]
    drawing_elements: List[DrawingElement]

@dataclass
class SPSDocument:
    """Represents the complete SPSDocument."""
    version: str
    pages: List[Page]

class SPSDocumentParser:
    """Parser for SPSDocument format."""
    
    def __init__(self):
        self.supported_elements = {
            'Line': self._parse_line,
            'BlockReference': self._parse_block_reference,
            'Text': self._parse_text,
            'Circle': self._parse_circle,
            'Arc': self._parse_arc,
            'Polyline': self._parse_polyline
        }
    
    def parse_file(self, file_path: str) -> SPSDocument:
        """Parse an SPSDocument XML file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        return self._parse_sps_document(root)
    
    def _parse_sps_document(self, root: ET.Element) -> SPSDocument:
        """Parse the root SPSDocument element."""
        version = root.get('version', '2.0')
        pages = []
        
        pages_elem = root.find('Pages')
        if pages_elem is not None:
            for page_elem in pages_elem.findall('Page'):
                page = self._parse_page(page_elem)
                pages.append(page)
        
        return SPSDocument(version=version, pages=pages)
    
    def _parse_page(self, page_elem: ET.Element) -> Page:
        """Parse a Page element."""
        title = page_elem.get('title', '')
        scale = page_elem.get('scale', '100')
        note = page_elem.get('note', '')
        
        layers = []
        drawing_elements = []
        
        database = page_elem.find('Database')
        if database is not None:
            # Parse layers
            layer_table = database.find('LayerTable')
            if layer_table is not None:
                for layer_elem in layer_table.findall('Layer'):
                    layer = self._parse_layer(layer_elem)
                    layers.append(layer)
            
            # Parse drawing elements
            block_table = database.find('BlockTable')
            if block_table is not None:
                for block_elem in block_table.findall('Block'):
                    elements = self._parse_block(block_elem)
                    drawing_elements.extend(elements)
        
        return Page(
            title=title,
            scale=scale,
            note=note,
            layers=layers,
            drawing_elements=drawing_elements
        )
    
    def _parse_layer(self, layer_elem: ET.Element) -> Layer:
        """Parse a Layer element."""
        name = layer_elem.get('name', '')
        color = layer_elem.get('color', '7')
        off = layer_elem.get('off', 'false').lower() == 'true'
        
        return Layer(name=name, color=color, off=off)
    
    def _parse_block(self, block_elem: ET.Element) -> List[DrawingElement]:
        """Parse a Block element and return its drawing elements."""
        elements = []
        
        for child in block_elem:
            tag = child.tag
            if tag == 'Polyline':
                poly_lines = self._parse_polyline(child)
                if poly_lines:
                    elements.extend(poly_lines)
                continue
            if tag in self.supported_elements:
                try:
                    element = self.supported_elements[tag](child)
                    if element:
                        elements.append(element)
                except Exception as e:
                    print(f"Warning: Failed to parse {tag} element: {e}")
        
        return elements
    
    def _parse_line(self, line_elem: ET.Element) -> Line:
        """Parse a Line element."""
        spt = line_elem.get('spt', '0,0')
        ept = line_elem.get('ept', '0,0')
        layer = line_elem.get('layer', '')
        color = line_elem.get('color', '')
        
        start_point = self.parse_coordinates(spt)
        end_point = self.parse_coordinates(ept)
        
        return Line(
            start_point=start_point,
            end_point=end_point,
            layer=layer,
            color=color
        )
    
    def _parse_block_reference(self, block_elem: ET.Element) -> BlockReference:
        """Parse a BlockReference element."""
        name = block_elem.get('name', '')
        position_str = block_elem.get('position', '0,0')
        angle = float(block_elem.get('angle', '0'))
        scale_str = block_elem.get('scale', '1,1')
        layer = block_elem.get('layer', '')
        color = block_elem.get('color', '')
        
        position = self.parse_coordinates(position_str)
        scale = self.parse_coordinates(scale_str)
        
        return BlockReference(
            name=name,
            position=position,
            angle=angle,
            scale=scale,
            layer=layer,
            color=color
        )
    
    def _parse_text(self, text_elem: ET.Element) -> Text:
        """Parse a Text element."""
        text = text_elem.get('text', '')
        position_str = text_elem.get('position', '0,0')
        font = text_elem.get('font', '')
        height = float(text_elem.get('height', '10'))
        angle = float(text_elem.get('angle', '0'))
        layer = text_elem.get('layer', '')
        color = text_elem.get('color', '')
        
        position = self.parse_coordinates(position_str)
        
        return Text(
            text=text,
            position=position,
            font=font,
            height=height,
            angle=angle,
            layer=layer,
            color=color
        )
    
    def _parse_circle(self, circle_elem: ET.Element) -> Circle:
        """Parse a Circle element."""
        center_str = circle_elem.get('center', '0,0')
        radius = float(circle_elem.get('radius', '0'))
        layer = circle_elem.get('layer', '')
        color = circle_elem.get('color', '')
        
        center = self.parse_coordinates(center_str)
        
        return Circle(
            center=center,
            radius=radius,
            layer=layer,
            color=color
        )
    
    def _parse_arc(self, arc_elem: ET.Element) -> Arc:
        """Parse an Arc element."""
        center_str = arc_elem.get('center', '0,0')
        radius = float(arc_elem.get('radius', '0'))
        start_angle = float(arc_elem.get('startAng', '0'))
        end_angle = float(arc_elem.get('endAng', '0'))
        layer = arc_elem.get('layer', '')
        color = arc_elem.get('color', '')
        
        center = self.parse_coordinates(center_str)
        
        return Arc(
            center=center,
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
            layer=layer,
            color=color
        )
    
    def _parse_polyline(self, polyline_elem: ET.Element) -> Optional[List[Line]]:
        """Parse a Polyline element as a sequence of Line elements."""
        vertices_str = polyline_elem.get('vertices', '')
        layer = polyline_elem.get('layer', '')
        color = polyline_elem.get('color', '')
        if not vertices_str:
            return None
        coords = [float(x) for x in vertices_str.split(',') if x.strip()]
        if len(coords) < 4:
            return None
        points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
        lines = []
        for i in range(len(points) - 1):
            lines.append(Line(start_point=points[i], end_point=points[i+1], layer=layer, color=color))
        # If isClosed, connect last to first
        is_closed = polyline_elem.get('isClosed', 'false').lower() == 'true'
        if is_closed and len(points) > 2:
            lines.append(Line(start_point=points[-1], end_point=points[0], layer=layer, color=color))
        return lines
    
    def parse_coordinates(self, coord_str: str) -> Tuple[float, float]:
        """Parse coordinate string like '100.5,200.75' to tuple."""
        try:
            parts = coord_str.split(',')
            if len(parts) == 2:
                return (float(parts[0]), float(parts[1]))
            else:
                return (0.0, 0.0)
        except (ValueError, IndexError):
            return (0.0, 0.0)
    
    def convert_to_standard_xml(self, sps_doc: SPSDocument) -> str:
        """Convert SPSDocument to standard XML format."""
        root = ET.Element("floorplan")
        root.set("version", sps_doc.version)
        
        for page in sps_doc.pages:
            page_elem = ET.SubElement(root, "page")
            page_elem.set("title", page.title)
            page_elem.set("scale", page.scale)
            page_elem.set("note", page.note)
            
            # Add layers
            layers_elem = ET.SubElement(page_elem, "layers")
            for layer in page.layers:
                layer_elem = ET.SubElement(layers_elem, "layer")
                layer_elem.set("name", layer.name)
                layer_elem.set("color", layer.color)
                layer_elem.set("off", str(layer.off))
            
            # Add drawing elements
            elements_elem = ET.SubElement(page_elem, "elements")
            for element in page.drawing_elements:
                elem = ET.SubElement(elements_elem, "element")
                elem.set("type", element.element_type)
                elem.set("layer", element.layer)
                elem.set("color", element.color)
                
                if isinstance(element, Line):
                    elem.set("start_x", str(element.start_point[0]))
                    elem.set("start_y", str(element.start_point[1]))
                    elem.set("end_x", str(element.end_point[0]))
                    elem.set("end_y", str(element.end_point[1]))
                
                elif isinstance(element, BlockReference):
                    elem.set("name", element.name)
                    elem.set("x", str(element.position[0]))
                    elem.set("y", str(element.position[1]))
                    elem.set("angle", str(element.angle))
                
                elif isinstance(element, Text):
                    elem.set("text", element.text)
                    elem.set("x", str(element.position[0]))
                    elem.set("y", str(element.position[1]))
                    elem.set("font", element.font)
                    elem.set("height", str(element.height))
                    elem.set("angle", str(element.angle))
                
                elif isinstance(element, Circle):
                    elem.set("center_x", str(element.center[0]))
                    elem.set("center_y", str(element.center[1]))
                    elem.set("radius", str(element.radius))
                
                elif isinstance(element, Arc):
                    elem.set("center_x", str(element.center[0]))
                    elem.set("center_y", str(element.center[1]))
                    elem.set("radius", str(element.radius))
                    elem.set("start_angle", str(element.start_angle))
                    elem.set("end_angle", str(element.end_angle))
        
        return ET.tostring(root, encoding='unicode')
    
    def export_for_matplotlib(self, sps_doc: SPSDocument) -> Dict[str, Any]:
        """Export data in a format suitable for matplotlib plotting."""
        result = {
            "pages": [],
            "layers": {}
        }
        
        # Create layer color mapping
        for page in sps_doc.pages:
            for layer in page.layers:
                result["layers"][layer.name] = {
                    "color": layer.color,
                    "visible": not layer.off
                }
        
        # Process each page
        for page in sps_doc.pages:
            page_data = {
                "title": page.title,
                "scale": page.scale,
                "lines": [],
                "texts": [],
                "blocks": [],
                "circles": [],
                "arcs": []
            }
            
            for element in page.drawing_elements:
                if isinstance(element, Line):
                    page_data["lines"].append({
                        "x": [element.start_point[0], element.end_point[0]],
                        "y": [element.start_point[1], element.end_point[1]],
                        "layer": element.layer,
                        "color": element.color
                    })
                
                elif isinstance(element, Text):
                    page_data["texts"].append({
                        "x": element.position[0],
                        "y": element.position[1],
                        "text": element.text,
                        "font": element.font,
                        "height": element.height,
                        "angle": element.angle,
                        "layer": element.layer,
                        "color": element.color
                    })
                
                elif isinstance(element, BlockReference):
                    page_data["blocks"].append({
                        "x": element.position[0],
                        "y": element.position[1],
                        "name": element.name,
                        "angle": element.angle,
                        "scale": element.scale,
                        "layer": element.layer,
                        "color": element.color
                    })
                
                elif isinstance(element, Circle):
                    page_data["circles"].append({
                        "x": element.center[0],
                        "y": element.center[1],
                        "radius": element.radius,
                        "layer": element.layer,
                        "color": element.color
                    })
                
                elif isinstance(element, Arc):
                    page_data["arcs"].append({
                        "x": element.center[0],
                        "y": element.center[1],
                        "radius": element.radius,
                        "start_angle": element.start_angle,
                        "end_angle": element.end_angle,
                        "layer": element.layer,
                        "color": element.color
                    })
            
            result["pages"].append(page_data)
        
        return result 