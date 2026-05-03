import math
import tkinter as tk
from tkinter import colorchooser
from tkinter import font as tkfont

from .. import globals, state
from ..tools.utils import (
    apply_object_color,
    can_edit_object_name,
    format_angle_value,
    format_length_value,
    format_number,
    get_editable_name_value,
    get_object_color,
    rename_object,
)
from ..ui.angle import Angle
from ..ui.angle_bisector import Angle_bisector
from ..ui.circle_3_points import Circle_3_points
from ..ui.circle_center_point import Circle_center_point
from ..ui.circle_center_radius import Circle_center_radius
from ..ui.compass import Compass
from ..ui.intersect import Intersect
from ..ui.length import Length
from ..ui.line import Line
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.parallel_line import Parallel_line
from ..ui.perpendicular_bisector import Perpendicular_bisector
from ..ui.perpendicular_line import Perpendicular_line
from ..ui.point import Point
from ..ui.point_on_object import Point_on_object
from ..ui.polygon import Polygon
from ..ui.polyline import Polyline
from ..ui.ray import Ray
from ..ui.regular_polygon import Regular_polygon
from ..ui.segment import Segment
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.semicircle import Semicircle
from ..ui.slope import Slope
from ..ui.vector import Vector


class Sidebar:
    def __init__(self, root: tk.Tk, main_area: tk.Frame, width=200):
        self.root = root
        self.container = tk.Frame(main_area, width=width, bg="white")
        self.container.pack_propagate(False)

        self.canvas = tk.Canvas(self.container, width=width, bg="white", highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.pack_propagate(False)

        self.resizing = False
        self.items = []
        self.canvas_tags = {}
        self.selected_item = None
        self.dialog = None
        self.editor_frame = None
        self.base_font_size = 16
        self.font_family = "Calibri, mathsans, sans-serif"
        self.font = tkfont.Font(root=root, family=self.font_family, size=self.base_font_size)

        self.context_var = tk.StringVar(master=root, value="Select an object")
        self.name_var = tk.StringVar(master=root)
        self.editor_error_var = tk.StringVar(master=root)
        self.length_decimals_var = tk.StringVar(
            master=root,
            value=str(getattr(state, "length_decimal_places", 2)),
        )
        self.angle_decimals_var = tk.StringVar(
            master=root,
            value=str(getattr(state, "angle_decimal_places", 2)),
        )

        self._sync_precision_controls()
        self.canvas.bind("<Configure>", self._on_resize)

    def _ensure_dialog(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            return

        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Properties")
        self.dialog.configure(bg="#f6f6f6")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.root)
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)

        self.editor_frame = tk.Frame(
            self.dialog,
            bg="#f6f6f6",
            padx=12,
            pady=12,
        )
        self.editor_frame.pack(fill="both", expand=True)
        self._build_editor()
        self._configure_widget_fonts(self.editor_frame)

    def _close_dialog(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.destroy()
        self.dialog = None
        self.editor_frame = None

    def _build_editor(self):
        label_fg = "#222222"
        self.editor_title = tk.Label(
            self.editor_frame,
            text="Properties",
            bg="#f6f6f6",
            fg=label_fg,
            anchor="w",
            font=self.font,
        )
        self.editor_title.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.context_label = tk.Label(
            self.editor_frame,
            textvariable=self.context_var,
            bg="#f6f6f6",
            fg="#333333",
            anchor="w",
            justify="left",
            wraplength=180,
            font=self.font,
        )
        self.context_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 10))

        self.name_label = tk.Label(self.editor_frame, text="Name", bg="#f6f6f6", fg=label_fg, anchor="w", font=self.font)
        self.name_entry = tk.Entry(self.editor_frame, textvariable=self.name_var, font=self.font)
        self.name_apply = tk.Button(
            self.editor_frame,
            text="Apply",
            command=self.apply_name_change,
            font=self.font,
        )
        self.name_entry.bind("<Return>", lambda _event: self.apply_name_change())
        self.name_entry.bind("<FocusOut>", lambda _event: self.apply_name_change())
        self.name_error = tk.Label(
            self.editor_frame,
            textvariable=self.editor_error_var,
            bg="#f6f6f6",
            fg="#b00020",
            anchor="w",
            justify="left",
            wraplength=180,
            font=self.font,
        )

        self.color_label = tk.Label(self.editor_frame, text="Color", bg="#f6f6f6", fg=label_fg, anchor="w", font=self.font)
        self.color_swatch = tk.Label(
            self.editor_frame,
            text="      ",
            bg="#000000",
            relief="solid",
            borderwidth=1,
        )
        self.color_button = tk.Button(
            self.editor_frame,
            text="Choose...",
            command=self.choose_color,
            font=self.font,
        )

        self.length_label = tk.Label(
            self.editor_frame,
            text="Length decimals",
            bg="#f6f6f6",
            fg=label_fg,
            anchor="w",
            font=self.font,
        )
        self.length_spinbox = tk.Spinbox(
            self.editor_frame,
            from_=0,
            to=6,
            width=4,
            textvariable=self.length_decimals_var,
            command=lambda: self.apply_precision_change("length"),
            font=self.font,
        )
        self.length_spinbox.bind("<Return>", lambda _event: self.apply_precision_change("length"))
        self.length_spinbox.bind("<FocusOut>", lambda _event: self.apply_precision_change("length"))

        self.angle_label = tk.Label(
            self.editor_frame,
            text="Angle decimals",
            bg="#f6f6f6",
            fg=label_fg,
            anchor="w",
            font=self.font,
        )
        self.angle_spinbox = tk.Spinbox(
            self.editor_frame,
            from_=0,
            to=6,
            width=4,
            textvariable=self.angle_decimals_var,
            command=lambda: self.apply_precision_change("angle"),
            font=self.font,
        )
        self.angle_spinbox.bind("<Return>", lambda _event: self.apply_precision_change("angle"))
        self.angle_spinbox.bind("<FocusOut>", lambda _event: self.apply_precision_change("angle"))

        self.editor_frame.grid_columnconfigure(1, weight=1)
        self._layout_name_widgets(show=False)
        self._layout_color_widgets(show=False)
        self._layout_precision_widgets(None)

    def _layout_name_widgets(self, show: bool):
        widgets = (self.name_label, self.name_entry, self.name_apply, self.name_error)
        if not show:
            for widget in widgets:
                widget.grid_remove()
            return

        self.name_label.grid(row=2, column=0, sticky="w")
        self.name_entry.grid(row=2, column=1, sticky="ew", padx=(6, 6))
        self.name_apply.grid(row=2, column=2, sticky="e")
        self.name_error.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(4, 0))

    def _layout_color_widgets(self, show: bool):
        widgets = (self.color_label, self.color_swatch, self.color_button)
        if not show:
            for widget in widgets:
                widget.grid_remove()
            return

        self.color_label.grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.color_swatch.grid(row=4, column=1, sticky="w", padx=(6, 6), pady=(10, 0))
        self.color_button.grid(row=4, column=2, sticky="e", pady=(10, 0))

    def _shows_length_precision(self, item) -> bool:
        return isinstance(
            item,
            (
                Segment,
                Segment_with_length,
                Length,
                Vector,
                Polyline,
                Polygon,
                Regular_polygon,
                Semicircle,
                Circle_center_point,
                Circle_center_radius,
                Circle_3_points,
                Compass,
            ),
        )

    def _shows_angle_precision(self, item) -> bool:
        return isinstance(item, Angle)

    def _layout_precision_widgets(self, item):
        show_length = item is not None and self._shows_length_precision(item)
        show_angle = item is not None and self._shows_angle_precision(item)

        if show_length:
            self.length_label.grid(row=5, column=0, sticky="w", pady=(10, 4))
            self.length_spinbox.grid(row=5, column=2, sticky="e", pady=(10, 4))
        else:
            self.length_label.grid_remove()
            self.length_spinbox.grid_remove()

        if show_angle:
            angle_row = 6 if show_length else 5
            angle_pady = 0 if show_length else (10, 0)
            self.angle_label.grid(row=angle_row, column=0, sticky="w", pady=angle_pady)
            self.angle_spinbox.grid(row=angle_row, column=2, sticky="e", pady=angle_pady)
        else:
            self.angle_label.grid_remove()
            self.angle_spinbox.grid_remove()

    def set_selected_item(self, item, *, close_dialog=False):
        self.selected_item = item
        self.update()

        if item is None:
            self.editor_error_var.set("")
            self.context_var.set("Select an object")
            self.name_var.set("")
            self._close_dialog()
            return

        if close_dialog:
            self._close_dialog()

    def to_dict(self) -> dict:
        return {
            "type": "Sidebar",
            "width": self.container.winfo_width(),
            "order": [item.tag for item in self.items],
        }

    def load_from_dict(self, data: dict):
        if not data:
            return
        self.resize(data.get("width", 200))
        self._sync_precision_controls()
        self.update()

    def resize(self, width):
        self.container.configure(width=width)
        self.canvas.configure(width=width)
        self.container.pack_propagate(False)
        self.canvas.pack_propagate(False)
        self.container.update_idletasks()

    def _configure_widget_fonts(self, widget):
        try:
            widget.configure(font=self.font)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._configure_widget_fonts(child)

    def _on_resize(self, event):
        new_width = event.width
        base_width = 200
        scale = new_width / base_width
        new_size = max(10, int(self.base_font_size * scale))
        self.font.configure(size=new_size)
        if self.dialog is not None and self.dialog.winfo_exists():
            self.context_label.configure(wraplength=max(180, new_width + 60))
            self.name_error.configure(wraplength=max(180, new_width + 60))
            self._configure_widget_fonts(self.editor_frame)

    def _sync_precision_controls(self):
        self.length_decimals_var.set(str(getattr(state, "length_decimal_places", 2)))
        self.angle_decimals_var.set(str(getattr(state, "angle_decimal_places", 2)))

    def _format_line_equation(self, item, constructor_name: str) -> str:
        if not isinstance(item.prescription, (list, tuple)) or len(item.prescription) != 3:
            a, b, c = 0, 0, 0
        else:
            a, b, c = item.prescription

        sign_a = "-" if a < 0 else ""
        sign_b = "-" if b < 0 else "+"
        return (
            f"{item.lower_label}: {constructor_name}\n"
            f"= {sign_a}{abs(a)}x {sign_b} {abs(b)}y = {c}"
        )

    def _format_circle_equation(self, item, constructor_name: str) -> str:
        squared = "²"
        sign_x = "+" if item.center.pos_x < 0 else "-"
        sign_y = "+" if item.center.pos_y < 0 else "-"
        return (
            f"{item.lower_label}: {constructor_name}\n"
            f"= (x {sign_x} {format_number(abs(item.center.pos_x))}){squared} + "
            f"(y {sign_y} {format_number(abs(item.center.pos_y))}){squared} = {format_number(item.radius**2)})"
        )

    def _item_text(self, item) -> str | None:
        if isinstance(item, (Point, Point_on_object, Intersect, Midpoint_or_center)):
            return f"{item.label} = ({format_number(item.pos_x)}, {format_number(item.pos_y)})"

        if isinstance(item, Line):
            return self._format_line_equation(item, f"Line({item.point_1.label}, {item.point_2.label})")

        if isinstance(item, Segment):
            return (
                f"{item.lower_label} = Segment({item.point_1.label}, {item.point_2.label})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Segment_with_length):
            return (
                f"{item.lower_label} = Segment({item.point_1.label}, {item.point_2.label})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Length):
            return (
                f"{item.lower_label} = Distance({item.point_1.label}, {item.point_2.label})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.value)}"
            )

        if isinstance(item, Slope):
            target_label = (
                item.target.lower_label
                if getattr(item.target, "lower_label", "")
                else (
                    f"{item.target.point_1.label}{item.target.point_2.label}"
                    if getattr(item.target, "point_1", None) is not None
                    and getattr(item.target, "point_2", None) is not None
                    else "line"
                )
            )
            return (
                f"{item.lower_label} = Slope({target_label})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {item.display_value}"
            )

        if isinstance(item, Ray):
            return self._format_line_equation(item, f"Ray({item.point_1.label}, {item.point_2.label})")

        if isinstance(item, Vector):
            return (
                f"{item.lower_label} = Vector({item.point_1.label}, {item.point_2.label})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Polyline):
            return (
                f"{item.lower_label} = Polyline({', '.join(p.label for p in item.line_points)})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Polygon):
            return (
                f"{item.lower_label} = Polygon({', '.join(p.label for p in item.line_points)})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Regular_polygon):
            ctx = [p.label for p in item.line_points[:2]]
            ctx.append(str(item.num_points))
            return (
                f"{item.lower_label} = Polygon({', '.join(ctx)})\n"
                f"{' ' * (len(item.lower_label) - 1)}= {format_length_value(item.length)}"
            )

        if isinstance(item, Perpendicular_bisector):
            return self._format_line_equation(
                item,
                f"PerpendicularBisector({item.point_1.label}, {item.point_2.label})",
            )

        if isinstance(item, Perpendicular_line):
            parent_label = (
                item.parent_line.lower_label
                if hasattr(item.parent_line, "lower_label")
                else (getattr(item, "parent_line_label", None) or "?")
            )
            point_label = item.point_1.label if item.point_1 else "?"
            return self._format_line_equation(item, f"PerpendicularLine({point_label}, {parent_label})")

        if isinstance(item, Parallel_line):
            parent_label = (
                item.parent_line.lower_label
                if hasattr(item.parent_line, "lower_label")
                else (getattr(item, "parent_line_label", None) or "?")
            )
            point_label = item.point_1.label if item.point_1 else "?"
            return self._format_line_equation(item, f"Line({point_label}, {parent_label})")

        if isinstance(item, Angle_bisector):
            return self._format_line_equation(
                item,
                f"AngleBisector({item.angle_point_1.label}, {item.point_1.label}, {item.angle_point_2.label})",
            )

        if isinstance(item, Semicircle):
            return (
                f"{item.lower_label}: Semicircle({item.point_1.label}, {item.point_2.label})\n"
                f"= {format_length_value(item.radius * math.pi)}"
            )

        if isinstance(item, Circle_center_point):
            return self._format_circle_equation(
                item,
                f"Circle({item.center.label}, {item.point_2.label})",
            )

        if isinstance(item, Circle_center_radius):
            return self._format_circle_equation(
                item,
                f"Circle({item.center.label}, {format_length_value(item.radius)})",
            )

        if isinstance(item, Circle_3_points):
            return self._format_circle_equation(
                item,
                f"Circle({item.point_1.label}, {item.point_2.label}, {item.point_3.label})",
            )

        if isinstance(item, Compass):
            return self._format_circle_equation(
                item,
                f"Circle({item.center.label}, Segment({item.r_point_1.label}, {item.r_point_2.label}))",
            )

        if isinstance(item, Angle):
            ctx = [item.point_1.label, item.anchor.label, item.point_2.label]
            label = item.label or "a"
            return (
                f"{label} = Angle({', '.join(ctx)})\n"
                f"{' ' * (len(label) - 1)}= {format_angle_value(item.angle)}"
            )

        return None

    def _item_context(self, item) -> str:
        item_type = item.__class__.__name__.replace("_", " ")
        identifier = get_editable_name_value(item)
        if identifier:
            return f"{item_type}: {identifier}"
        return item_type

    def show_item(self, item):
        self.set_selected_item(item)
        self.editor_error_var.set("")
        self._sync_precision_controls()

        if item is None:
            return

        self._ensure_dialog()
        self.context_var.set(self._item_context(item))
        editable_name = get_editable_name_value(item)
        self.name_var.set(editable_name or "")
        self._layout_name_widgets(show=can_edit_object_name(item))
        self._layout_color_widgets(show=True)
        self._layout_precision_widgets(item)
        self.color_swatch.configure(bg=get_object_color(item))
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.title(f"Properties - {self._item_context(item)}")

    def apply_name_change(self):
        item = self.selected_item
        if item is None or not can_edit_object_name(item):
            return

        success, error = rename_object(item, self.name_var.get(), state)
        if not success:
            self.editor_error_var.set(error)
            self.name_var.set(get_editable_name_value(item) or "")
            return

        self.editor_error_var.set("")
        self.name_var.set(get_editable_name_value(item) or "")
        globals.objects.refresh()
        self.update()
        self.show_item(item)

    def choose_color(self):
        item = self.selected_item
        if item is None:
            return

        parent = self.dialog if self.dialog is not None and self.dialog.winfo_exists() else self.container
        chosen = colorchooser.askcolor(color=get_object_color(item), parent=parent)[1]
        if not chosen:
            return

        apply_object_color(item, chosen)
        globals.objects.refresh()
        self.update()
        self.show_item(item)

    def apply_precision_change(self, kind: str):
        attr = "length_decimal_places" if kind == "length" else "angle_decimal_places"
        variable = self.length_decimals_var if kind == "length" else self.angle_decimals_var

        try:
            value = int(variable.get())
        except ValueError:
            value = getattr(state, attr, 2)

        value = max(0, min(6, value))
        setattr(state, attr, value)
        variable.set(str(value))
        globals.objects.refresh()
        self.update()
        if self.selected_item is not None:
            self.show_item(self.selected_item)

    def update(self):
        self.canvas.delete("all")
        self.canvas_tags.clear()

        y = 10
        for index, item in enumerate(self.items):
            text_value = self._item_text(item)
            if not text_value:
                continue

            text_id = self.canvas.create_text(
                10,
                y,
                anchor="nw",
                text=text_value,
                font=self.font,
                fill=get_object_color(item),
                tags=f"sidebar_text_{index}",
            )
            self.canvas_tags[text_id] = item

            bbox = self.canvas.bbox(text_id)
            if bbox and item is self.selected_item:
                rect_id = self.canvas.create_rectangle(
                    bbox[0] - 6,
                    bbox[1] - 4,
                    bbox[2] + 6,
                    bbox[3] + 4,
                    fill="#eef3ff",
                    outline="",
                )
                self.canvas.tag_lower(rect_id, text_id)
                self.canvas_tags[rect_id] = item
                bbox = self.canvas.bbox(rect_id)

            if bbox:
                height = bbox[3] - bbox[1]
                y += height + 10

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
