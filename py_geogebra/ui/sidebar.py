import tkinter as tk
from tkinter import font as tkfont

from py_geogebra.ui.angle_bisector import Angle_bisector
from py_geogebra.ui.circle_center_point import Circle_center_point
from py_geogebra.ui.circle_center_radius import Circle_center_radius
from py_geogebra.ui.semicircle import Semicircle
from ..ui.point import Point
from ..ui.line import Line
from ..ui.segment import Segment
from ..ui.polyline import Polyline
from ..ui.polygon import Polygon
from ..ui.ray import Ray
from ..ui.perpendicular_bisector import Perpendicular_bisector
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.parallel_line import Parallel_line
from ..ui.regular_polygon import Regular_polygon



class Sidebar:
    def __init__(self, root: tk.Tk, main_area: tk.Frame, width=200):
        # self.frame = tk.Frame(main_area, width=width, bg="#dddddd")
        # self.frame.pack_propagate(False)
        self.canvas = tk.Canvas(main_area,width=width, bg="white")
        self.canvas.pack_propagate(False)

        self.resizing = False
        self.items = []
        self.canvas_tags = {}
        self.base_font_size = 16
        self.num_of_regular_polygons = 0
        self.font_family = "Calibri, mathsans, sans-serif"
        self.font = tkfont.Font(family=self.font_family, size=self.base_font_size)

        self.canvas.bind("<Configure>", self._on_resize)

    def to_dict(self) -> dict:
        return {
            "type": "Sidebar",
            "width": self.canvas.winfo_width(),
            "order": [item.tag for item in self.items],
        }

    def load_from_dict(self, data: dict):
        if not data:
            return
        self.resize(data.get("width", 200))
        self.update()

    def resize(self, width):
        self.canvas.configure(width=width)
        self.canvas.pack_propagate(False)
        self.canvas.update_idletasks()

    def _on_resize(self, event):
        new_width = event.width
        base_width = 200
        scale = new_width / base_width
        new_size = max(10, int(self.base_font_size * scale))
        self.font.configure(size=new_size)

        for widget in self.canvas.winfo_children():
            widget.configure(font=self.font)

    def update(self):
        self.canvas.delete("all")
        self.canvas_tags.clear()
        self.num_of_regular_polygons = 0

        y = 10
        for i, item in enumerate(self.items):
            if isinstance(item, Point):
                # text = tk.Label(
                #     self.canvas,
                #     text=f"{item.label} =  {round(item.pos_x,2), round(item.pos_y,2)}",
                #     fg="black",
                #     bg="#ffffff",
                #     font=self.font,
                # )
                # text.pack(padx=10, pady=10, anchor="nw")
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=f"{item.label} =  {round(item.pos_x,2), round(item.pos_y,2)}",
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Line):
                assert len(item.prescription) == 3
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Line({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Segment):
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label} = Segment({item.point_1.label}, {item.point_2.label})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {item.length}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Ray):
                assert len(item.prescription) == 3
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Ray({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Polyline):
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label} = Polyline({', '.join(p.label for p in item.line_points)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10
            elif isinstance(item, Polygon):
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label} = Polygon({', '.join(p.label for p in item.line_points)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Regular_polygon):
                self.num_of_regular_polygons += 1
                ctx = [p.label for p in item.line_points[:2]]
                ctx.append(str(item.num_points))
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"poly{self.num_of_regular_polygons} = Polygon({', '.join(ctx)})\n"
                        f"{' ' * (len(item.lower_label)-1)}= {round(item.length, 2)}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10



            elif isinstance(item, Perpendicular_bisector):
                assert len(item.prescription) == 3
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: PerpendicularBisector({item.point_1.label}, {item.point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Perpendicular_line):
                assert len(item.prescription) == 3
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: PerpendicularLine({item.point_1.label}, {item.parent_line.lower_label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Parallel_line):
                # assert len(item.prescription) == 3 tuto je item.prescription na zaciatku prazdny takze nebudeme assertovat
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Line({item.point_1.label}, {item.parent_line.lower_label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Angle_bisector):
                assert len(item.prescription) == 3
                a, b, c = item.prescription
                sign_a = "-" if a < 0 else ""
                sign_b = "-" if b < 0 else "+"
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: AngleBisector({item.angle_point_1.label}, {item.point_1.label}, {item.angle_point_2.label})\n"
                        f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Semicircle):
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Semicircle({item.point_1.label}, {item.point_2.label})\n"
                        f"= {item.radius*3.14:.2f}"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Circle_center_point):
                squared = "²"
                sign_x = '+' if item.point_1.pos_x < 0 else '-'
                sign_y = '+' if item.point_1.pos_y < 0 else '-'
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Circle({item.point_1.label}, {item.point_2.label})\n"
                        f"= (x {sign_x} {abs(item.point_1.pos_x):.2f}){squared} + (y {sign_y} {abs(item.point_1.pos_y):.2f}){squared} = {item.radius**2:.2f})"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10

            elif isinstance(item, Circle_center_radius):
                squared = "²"
                sign_x = '+' if item.point_1.pos_x < 0 else '-'
                sign_y = '+' if item.point_1.pos_y < 0 else '-'
                text = self.canvas.create_text(
                    10, y,
                    anchor="nw",
                    text=(
                        f"{item.lower_label}: Circle({item.point_1.label}, {item.radius})\n"
                        f"= (x {sign_x} {abs(item.point_1.pos_x):.2f}){squared} + (y {sign_y} {abs(item.point_1.pos_y):.2f}){squared} = {item.radius**2:.2f})"
                    ),
                    font=self.font,
                    fill="black",
                    tags=f"sidebar_text_{i}"
                )
                self.canvas_tags[text] = item
                bbox = self.canvas.bbox(text)
                height = bbox[3] - bbox[1]
                y += height + 10
