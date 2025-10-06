import tkinter as tk
from ..tools.utils import world_to_screen, find_2lines_intersection, find_translation, get_label, find_translation_between_points
from .segment import Segment
from .segment_with_lenght import Segment_with_length
from .polyline import Polyline
from .ray import Ray
from .. import globals
from .. import state

class Create_Intersect:
    def __init__(
        self,
        line_1,
        line_2,
        root: tk.Tk,
        unit_size: int = 40,
        color="grey",
    ):

        self.root = root
        self.color = color

        self.unit_size = unit_size

        line_1.deselect()
        
        intersects = []

        if isinstance(line_1, Polyline) and isinstance(line_2, Polyline):
            for i in range(len(line_1.line_points) - 1):
                for i2 in range(len(line_2.line_points) - 1):
                    intersect = Intersect(
                        root,
                        label=get_label(state),
                        unit_size=unit_size,
                    )
                    intersect.point_1 = line_1.line_points[i]
                    intersect.point_2 = line_1.line_points[i + 1]
                    intersect.point_3 = line_2.line_points[i2]
                    intersect.point_4 = line_2.line_points[i2 + 1]
                    intersect.line_1 = line_1
                    intersect.line_2 = line_2

                    intersects.append(intersect)
                    globals.objects.register(intersect)
        if isinstance(line_1, Polyline) and not isinstance(line_2, Polyline):
            for i in range(len(line_1.line_points) - 1):
                intersect = Intersect(
                    root,
                    label=get_label(state),
                    unit_size=unit_size,
                )
                intersect.point_1 = line_1.line_points[i]
                intersect.point_2 = line_1.line_points[i + 1]
                intersect.point_3 = line_2.point_1
                intersect.point_4 = line_2.point_2
                intersect.line_1 = line_1
                intersect.line_2 = line_2

                intersects.append(intersect)
                globals.objects.register(intersect)
        if not isinstance(line_1, Polyline) and isinstance(line_2, Polyline):
            for i in range(len(line_2.line_points) - 1):
                intersect = Intersect(
                    root,
                    label=get_label(state),
                    unit_size=unit_size,
                )
                intersect.point_1 = line_1.point_1
                intersect.point_2 = line_1.point_2
                intersect.point_3 = line_2.line_points[i]
                intersect.point_4 = line_2.line_points[i + 1]
                intersect.line_1 = line_1
                intersect.line_2 = line_2

                intersects.append(intersect)
                globals.objects.register(intersect)
        if not isinstance(line_1, Polyline) and not isinstance(line_2, Polyline):
            
            intersect = Intersect(
                root,
                label=get_label(state),
                unit_size=unit_size,
            )
            intersect.point_1 = line_1.point_1
            intersect.point_2 = line_1.point_2
            intersect.point_3 = line_2.point_1
            intersect.point_4 = line_2.point_2
            intersect.line_1 = line_1
            intersect.line_2 = line_2

            intersects.append(intersect)
            globals.objects.register(intersect)
            
        

                
            
        
        



class Intersect:
    def __init__(
        self,
        root: tk.Tk,
        label: str = "",
        unit_size: int = 40,
        color="grey",
    ):

        self.root = root
        self.canvas = globals.canvas
        self.color = color
        self.objects = globals.objects

        self.pos_x = 0
        self.pos_y = 0
        self.label = label

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = 1.0  # zoom factor
        self.unit_size = unit_size

        self.x = 0
        self.y = 0

        self.point_1 = None
        self.point_2 = None
        self.point_3 = None
        self.point_4 = None
        
        self.line_1 = None
        self.line_2 = None
        
        self.points = []
        
        self.translation = 0
        self.is_drawable = True

        self.tag = f"intersect_{id(self)}"
        self.selected = False
        self.highlight_tag = f"{self.tag}_highlight"

    def select(self):
        self.selected = True
        self.update()

    def deselect(self):
        self.selected = False
        self.update()

    def update(self):
        self.points = [self.point_1, self.point_2, self.point_3, self.point_4] #toto si nevsimajme ze sa assignuje kazdy update
        self.canvas.delete(self.tag)
        self.canvas.delete(self.highlight_tag)

        self.is_drawable = True
        

        self.pos_x, self.pos_y = find_2lines_intersection(self.points)
        
        
        if isinstance(self.line_1, Segment) or isinstance(
            self.line_1, Segment_with_length
        ):
            find_translation(self, self.line_1)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_1, Ray):
            find_translation(self, self.line_1)
            if self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_1, Polyline):
            find_translation_between_points(self, self.points[0], self.points[1])
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
                
                
        if isinstance(self.line_2, Segment) or isinstance(
            self.line_2, Segment_with_length
        ):
            find_translation(self, self.line_2)
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_2, Ray):
            find_translation(self, self.line_2)
            if self.translation < 0:
                self.is_drawable = False
        elif isinstance(self.line_1, Polyline):
            find_translation_between_points(self, self.points[2], self.points[3])
            if self.translation > 1 or self.translation < 0:
                self.is_drawable = False
                

        if self.is_drawable:

            visual_scale = min(max(1, self.scale**0.5), 1.9)

            x, y = world_to_screen(self.pos_x, self.pos_y)
            self.x, self.y = x, y

            r = 6.0 * visual_scale

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=self.color,
                outline="",
                tags=(self.tag,),
            )

            if self.selected:
                r_h = r * 1.4
                self.canvas.create_oval(
                    x - r_h,
                    y - r_h,
                    x + r_h,
                    y + r_h,
                    outline=self.color,
                    width=2,
                    fill="",  # no fill so it looks like a ring
                    tags=(self.highlight_tag,),  # must be a tuple
                )

            if self.label:
                self.canvas.create_text(
                    x + 10 * visual_scale,
                    y - 15 * visual_scale,
                    text=self.label,
                    font=("Arial", int(12 * visual_scale)),
                    fill="blue",
                    tags=self.tag,
                )
