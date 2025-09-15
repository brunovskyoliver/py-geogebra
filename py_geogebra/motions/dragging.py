from .. import state
from ..tools.utils import center, set_cursor
from ..ui.free_hand import FreeHand
from ..ui.line import Line


def dragging(root, canvas, objects, axes):
    def left_click_drag(e):
        if state.selected_tool == "arrow":
            if state.drag_target is None:
                dx = e.x - state.start_pos["x"]
                dy = e.y - state.start_pos["y"]
                objects.offset_x += dx
                objects.offset_y += dy
                objects.refresh()
                state.start_pos["x"] = e.x
                state.start_pos["y"] = e.y
            else:
                cx, cy = center(canvas, objects)
                world_x = (e.x - cx) / (objects.unit_size * objects.scale)
                world_y = (cy - e.y) / (objects.unit_size * objects.scale)

                state.drag_target.pos_x = world_x
                state.drag_target.pos_y = world_y
                state.drag_target.update()
                for obj in objects._objects:
                    if isinstance(obj, Line):
                        if (
                            obj.point_1 is state.drag_target
                            or obj.point_2 is state.drag_target
                        ):
                            obj.update()

        elif state.selected_tool == "pen" and state.current_pen is not None:
            cx, cy = center(canvas, objects)
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            state.current_pen.add_point(world_x, world_y)

        elif state.selected_tool == "freehand":
            cx, cy = center(canvas, objects)
            world_x = (e.x - cx) / (objects.unit_size * objects.scale)
            world_y = (cy - e.y) / (objects.unit_size * objects.scale)
            line = FreeHand(root, canvas)
            line.unit_size = objects.unit_size
            line.pos_x1 = state.freehand_last_pos["x"]
            line.pos_y1 = state.freehand_last_pos["y"]
            line.pos_x2 = world_x
            line.pos_y2 = world_y
            line.cx = cx
            line.cy = cy
            line.update()
            state.freehand_last_pos["x"] = world_x
            state.freehand_last_pos["y"] = world_y


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
                        cx, cy = center(canvas, objects)
                        world_x = (e.x - cx) / (objects.unit_size * objects.scale)
                        world_y = (cy - e.y) / (objects.unit_size * objects.scale)
                        obj.delete_point(world_x, world_y, r=0.2)
                        break

    def middle_click_drag(e):
        dx = e.x - state.start_pos["x"]
        dy = e.y - state.start_pos["y"]
        objects.offset_x += dx
        objects.offset_y += dy
        objects.refresh()
        state.start_pos["x"] = e.x
        state.start_pos["y"] = e.y

    canvas.bind("<B1-Motion>", left_click_drag)
    canvas.bind("<B2-Motion>", right_click_drag)
    canvas.bind("<B3-Motion>", middle_click_drag)
