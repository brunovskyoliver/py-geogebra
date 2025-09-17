from .. import state
from ..tools.utils import center, set_cursor, find_translation
from ..ui.free_hand import FreeHand
from ..ui.line import Line
from ..ui.ray import Ray
from ..ui.segment_with_lenght import Segment_with_length
from ..ui.midpoint_or_center import Midpoint_or_center
from ..ui.segment import Segment
from ..ui.polyline import Polyline


def dragging(root, canvas, sidebar, objects, axes):
    def left_click_drag(e):
        if state.selected_tool == "arrow":
            if state.drag_target is None:
                dx = e.x - state.start_pos["x"]
                dy = e.y - state.start_pos["y"]
                objects.offset_x += dx
                objects.offset_y += dy

                width = canvas.winfo_width()
                height = canvas.winfo_height()
                state.center = (
                    width // 2 + objects.offset_x,
                    height // 2 + objects.offset_y,
                )

                objects.refresh()
                state.start_pos["x"] = e.x
                state.start_pos["y"] = e.y

            else:
                cx, cy = state.center
                world_x = (e.x - cx) / (objects.unit_size * objects.scale)
                world_y = (cy - e.y) / (objects.unit_size * objects.scale)

                state.drag_target.pos_x = world_x
                state.drag_target.pos_y = world_y
                state.drag_target.update()
                for obj in objects._objects:
                    if (
                        isinstance(obj, Line)
                        or isinstance(obj, Segment)
                        or isinstance(obj, Ray)
                        or isinstance(obj, Segment_with_length)
                        or isinstance(obj, Midpoint_or_center)
                    ):
                        if (
                            obj.point_1 is state.drag_target
                            or obj.point_2 is state.drag_target
                        ):
                            obj.update()
                        elif (
                            hasattr(obj, "points") 
                            and state.drag_target in obj.points
                            and state.drag_target is not obj.point_1
                            and state.drag_target is not obj.point_2
                        ):
                            find_translation(state.drag_target, obj)
                            obj.update()
                        elif (
                            state.drag_target is not obj.point_1
                            and state.drag_target is not obj.point_2
                        ):
                            objects.refresh()
                    elif isinstance(obj, Polyline):
                        if any(p is state.drag_target for p in obj.points):
                            obj.update()
                        else:
                            objects.refresh()
                sidebar.update()

        elif state.selected_tool == "pen" and state.current_pen is not None:
            cx, cy = state.center
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            state.current_pen.add_point(world_x, world_y)

        elif state.selected_tool == "freehand":
            cx, cy = state.center
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            state.current_pen.add_point(world_x, world_y)

    def right_click_drag(e):
        if state.selected_tool == "pen":
            set_cursor(canvas, "circle")
            r = 8
            items = canvas.find_overlapping(e.x - r, e.y - r, e.x + r, e.y + r)
            for obj in objects._objects:
                if hasattr(obj, "tag") and any(
                    obj.tag in canvas.gettags(i) for i in items
                ):
                    if "pen" in obj.tag:
                        cx, cy = state.center
                        world_x = (e.x - cx) / (objects.unit_size * objects.scale)
                        world_y = (cy - e.y) / (objects.unit_size * objects.scale)
                        obj.delete_point(world_x, world_y, r=0.2)
                        break

    def middle_click_drag(e):
        dx = e.x - state.start_pos["x"]
        dy = e.y - state.start_pos["y"]
        objects.offset_x += dx
        objects.offset_y += dy

        width = canvas.winfo_width()
        height = canvas.winfo_height()
        state.center = (
            width // 2 + objects.offset_x,
            height // 2 + objects.offset_y,
        )

        objects.refresh()
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    def left_click_drag_sidebar(e):
        if state.sidebar_resizing:
            new_width = max(50, e.x)
            state.sidebar_width = new_width
            sidebar.frame.configure(width=new_width)
            sidebar.frame.pack_propagate(False)
            sidebar.frame.update_idletasks()

    canvas.bind("<B1-Motion>", left_click_drag)
    canvas.bind("<B2-Motion>", right_click_drag)
    canvas.bind("<B3-Motion>", middle_click_drag)

    sidebar.frame.bind("<B1-Motion>", left_click_drag_sidebar)
