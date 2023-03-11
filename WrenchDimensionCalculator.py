#! /usr/local/bin/python3

from dataclasses import dataclass, field
import math
from decimal import Decimal
import functools
import operator


@dataclass(frozen=True)
class HexWrench():
    """ The HexWrench dataclass defines a parktools hex wrench
        in terms of dimensions useful in designing a tool holder for the wrench
        The size is measured in mm
        Other dimensions are of the hex wrench head size
        And other dimensions are calculated from the provided measured dimensions
    """
    size: Decimal
    head_width: float
    head_short_length: float
    size_f: float
    circumference: float
    square: float
    area: float

@dataclass(frozen=True)
class HexWrenchHolderParameters():
    """ The HexWrenchHolderParameters are the relevant design parameters used 
        to construct the hex wrench tool holder.
        For orientation
        ----> length ----> 
        +--------------------------------+ |
        |           H o l e s            | | Width
        |  x    x    x    x    x    x    | V
        +--------------------------------+

        And Height is the thickness of the tool holder block
    """
    lengthwise_border: float 
    lengthwise_inner_spacing: float
    widthwise_border: float
    height: float
    hole_enlarge_factor: float
    hole_enlarge_min: float

@dataclass(frozen=True)
class HoleCoords():
    """ The Hole Coordinates are the x,y coordinates
        x - along the length axis with left border being 0
        y - along the Width axis with the top border being 0
    """
    x: float
    y: float

@dataclass(frozen=True)
class HoleDetails():
    """ The Hole Details are dimensions of each hole in the tool holder 
        used to hold each Hex Wrench tool
        The key dimensions are 
        - the coordinates (see above), and 
        - the hole diameter (to fit the hex wrench diameter)
    """
    hex_size: Decimal
    hex_long_diameter: float
    hole_diameter: float
    hole_coords: HoleCoords


def create_hex_wrench(size: Decimal, head_width: float, head_short_length: float): 
    """ This function will create a new HexWrench data object by
        taking the raw dimensions and calculating the computable dimensions
        - size is the hex wrench size in mm
        - size_f is just the size as a float
        - head_width is the widest width of the head to be used for spacing the holes
        - head_short_length is the short length of the head to be used for hole placement away from the mounting side of tool holder
    """
    size_f = float(size)
    return HexWrench(
        size,
        head_width,
        head_short_length,
        size_f,
        circumference = 6 * size_f,
        square = math.sqrt(2) * size_f,
        area = 3 / 2 * math.sqrt(3) * size_f * size_f
    )


def compute_hex_long_diameter(hex_size: float):
    """Computes the long diameter using the side dimension of the hex wrench"""
    return 2 / math.sqrt(3) * hex_size


def compute_hole_diameter(hex_long_dia: float, hole_enlarge_factor: float, hole_enlarge_min: float):
    """Computes the hole diameter for the tool holder"""
    return max( hex_long_dia + hole_enlarge_min, hex_long_dia * hole_enlarge_factor )


def compute_hole_detail(hex_size: Decimal, hex_long_dia: float, hole_enlarge_factor, hole_enlarge_min):
    """ Creates a hold detail data object based on dimensions provided.
        ** Note ** The coordinates will be computed in another step, and is thus here set to None
    """
    return HoleDetails(
            hex_size,
            hex_long_dia,
            compute_hole_diameter(
                hex_long_dia, 
                hole_enlarge_factor,
                hole_enlarge_min
            ),
            None
        )


def compute_hole_centers(hex_wrench_widths: list[float], inner_spacing: float, lengthwise_border: float, widthwise_border: float, max_short_handle_length: float ):
    """ Computes hole centers based on the hole sizes and the tool parameters that define desired spacings
        - hex_wrench_widths - is the widest part of the hex wrench and is used for spacing
        - inner_spacing - is the distance to leave between each hex wrench when seated in the tool holder
        - lengthwise_border - is space to leave on the tool holder from first and last holes to the tool holder lengthwise edges


        Y U C H
        Please help me rewrite this as a fold !!!
    """
    y_center = widthwise_border + max_short_handle_length

    centers = []
    half_widths = [ w / 2 for w in hex_wrench_widths ]
    pre_center = lengthwise_border - half_widths[0]
    for half_width in half_widths:
        x_center = pre_center + half_width
        centers.append( HoleCoords(x_center,y_center) )
        pre_center = x_center + half_width + inner_spacing
    return centers


def compute_holder_length(last_hole_x_center: float, hole_dia: float, lengthwise_border: float ):
    """Computes the tool holder full length (x length)"""
    return last_hole_x_center + hole_dia/2.0 + lengthwise_border


def compute_holder_width(max_handle_short_length: float, max_hex_diameter: float, width_border: float):
    """Computes the tool holder width, making sure to leave room for the tool head and an edge border"""
    return width_border + max_handle_short_length + max_hex_diameter + width_border


#
# Here are some Text UI functions
#

def print_boxed_text(text: str, width: int = None, nbr_blank_lines: int = 1):
    """Prints a title inside of a box for boldness"""

    def print_top_bottom(width:int):
        print( '+' + '-'*width + '+' )

    def print_blank_line(width: int, nbr_blank_lines: int):
        for i in range(nbr_blank_lines):
            print( '|' + ' '*width + '|' )

    def print_text(width: int, text: str):
        line_filler = ' '*(width - len(text.expandtabs()) - 1)
        print( '| ' + text + line_filler + '|' )

    if width is None:
        width = 2 + len(text)

    print_top_bottom(width)
    print_blank_line(width, nbr_blank_lines)
    print_text(width, text)
    print_blank_line(width, nbr_blank_lines)
    print_top_bottom(width)


def print_table_header(title: str, header: str, line_separator_char: str = '-', nbr_blank_lines: int = 2):
    """Prints a table title and column headers for a table dump"""
    for i in range(nbr_blank_lines):
        print()
    print(f"{title}:")
    print(header)
    print(line_separator_char*len(header.expandtabs()))

############################################################

############################################################

if __name__ == '__main__':

    # ######################
    # Configuration & Setup 
    # ######################

    hex_set = [ 
        create_hex_wrench(size=2,   head_width=24, head_short_length=36), 
        create_hex_wrench(size=2.5, head_width=24, head_short_length=36),
        create_hex_wrench(size=3,   head_width=24, head_short_length=36),
        create_hex_wrench(size=4,   head_width=24, head_short_length=36),
        create_hex_wrench(size=5,   head_width=24, head_short_length=36),
        create_hex_wrench(size=6,   head_width=24, head_short_length=36),
        create_hex_wrench(size=8,   head_width=24, head_short_length=36),
        create_hex_wrench(size=10,  head_width=31, head_short_length=46),
    ]

    hex_wrench_holder_parameters = HexWrenchHolderParameters(
            lengthwise_border=5, 
            lengthwise_inner_spacing=2.5, 
            widthwise_border=5,
            height=38,
            hole_enlarge_factor=1.20,
            hole_enlarge_min = 1
        )

    # ######################
    # Dimension Computations
    # ######################

    hole_details = [    compute_hole_detail(
                            hw.size, 
                            compute_hex_long_diameter(hw.size_f),
                            hex_wrench_holder_parameters.hole_enlarge_factor,
                            hex_wrench_holder_parameters.hole_enlarge_min
                            )
                        for hw in hex_set 
                    ]

    hex_wrench_widths = [   max( hd.hole_diameter, hw.head_width ) 
                            for (hw,hd) in zip(hex_set,hole_details) ]

    max_handle_short_length = max([ hw.head_short_length for hw in hex_set ])

    max_hole_diameter = max([ hd.hole_diameter for hd in hole_details ])

    hole_centers = compute_hole_centers(
        hex_wrench_widths = hex_wrench_widths, 
        inner_spacing = hex_wrench_holder_parameters.lengthwise_inner_spacing,
        lengthwise_border = hex_wrench_holder_parameters.lengthwise_border,
        widthwise_border = hex_wrench_holder_parameters.widthwise_border,
        max_short_handle_length = max_handle_short_length
    )

    # Create a new Hole Details list which includes the computed hole_centers
    hole_details = [ HoleDetails(
                        hd.hex_size,
                        hd.hex_long_diameter,
                        hd.hole_diameter,
                        coord
                        )
                        for (hd, coord) in zip( hole_details, hole_centers )
                    ]

    # Calculate the tool holder length (x-axis)
    holder_length = compute_holder_length(
        last_hole_x_center = hole_details[-1].hole_coords.x,
        hole_dia = hole_details[-1].hex_long_diameter,
        lengthwise_border = hex_wrench_holder_parameters.lengthwise_border )

    # Calculate the tool holder width (y-axis)
    holder_width = compute_holder_width(
        max_handle_short_length = max([ hw.head_short_length for hw in hex_set ]),
        max_hex_diameter = max_hole_diameter,
        width_border = hex_wrench_holder_parameters.widthwise_border )

    # ######################
    # Display Results
    # ######################

    print_boxed_text(f"Tool Holder for {len(hex_set)} hex wrenches")

    # Dump table of Hole Details
    print_table_header("Hole details","hex size (mm)\thex diameter\thole diameter\tcoords")
    for hd in hole_details:
        if (hd.hole_coords is None):
            print(f"{hd.hex_size}\t\t{hd.hex_long_diameter:.2f}\t\t{hd.hole_diameter:.2f}\t\tNone")
        else:
            print(f"{hd.hex_size}\t\t{hd.hex_long_diameter:.2f}\t\t{hd.hole_diameter:.2f}\t\t( {hd.hole_coords.x:.2f}, {hd.hole_coords.y:.2f} )")

    # Dump table of Tool Holder Dimensions
    print_table_header("Tool Holder Dimensions","length\twidth\theight")
    print(f"{holder_length:.2f}\t{holder_width:.2f}\t{hex_wrench_holder_parameters.height:.2f}")

    print()



