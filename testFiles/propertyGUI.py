import pyglet
import cv2 as cv
import numpy as np
import visionLibrary as vl


class Rectangle(object):
    # Draws a rectangle into a batch
    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [200, 200, 220, 255] * 4))


class TextWidget(object):
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document,
                                                               width, height,
                                                               multiline=False,
                                                               batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, batch)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)


class Button(object):
    def __init__(self, text, x, y, width, height, batch):
        self.text = text
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.batch = batch
        self.label = pyglet.text.Label(text, x=self.x, y=self.y,
                                       anchor_y='bottom',
                                       color=(0, 0, 0, 255), batch=self.batch)
        pad = 5
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, batch)

    def hit_test(self, x, y):
        return (0 < x - self.x < self.width and
                0 < y - self.y < self.height)


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(400, 720, caption='Vision Settings')

        self.batch = pyglet.graphics.Batch()
        self.labels = [
            pyglet.text.Label('HSV LOWERLIMIT', x=10, y=700, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch),
            pyglet.text.Label('HSV UPPERLIMIT', x=10, y=640, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch)]
        self.widgets = [
            TextWidget(str(vl.hsvLimitLower[0]), 200, 700, 30, self.batch),
            TextWidget(str(vl.hsvLimitLower[1]), 240, 700, 30, self.batch),
            TextWidget(str(vl.hsvLimitLower[2]), 280, 700, 30, self.batch),
            TextWidget(str(vl.hsvLimitUpper[0]), 200, 640, 30, self.batch),
            TextWidget(str(vl.hsvLimitUpper[1]), 240, 640, 30, self.batch),
            TextWidget(str(vl.hsvLimitUpper[2]), 280, 640, 30, self.batch)]

        for prop in vl.visionProperties:
            self.widgets.append(TextWidget(str(vl.visionProperties[prop]), 200,
                                           640 - 40*(len(self.widgets) - 5),
                                           60, self.batch))
            self.labels.append(pyglet.text.Label(prop, x=10,
                                                 y=640 - 40*(len(self.labels) - 1),
                                                 anchor_y='bottom',
                                                 color=(0, 0, 0, 255),
                                                 batch=self.batch))
            if len(self.widgets) == 16:
                self.widgets.append(Button("Enter", 200,
                                           640 - 40*(len(self.widgets) - 3),
                                           50, 30, self.batch))

        self.text_cursor = self.get_system_mouse_cursor('text')

        self.focus = None
        self.set_focus(self.widgets[0])

    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        for widget in self.widgets:
            widget.width = width - 110

    def on_draw(self):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()
        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            if widget.hit_test(x, y) and isinstance(widget, TextWidget):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                if isinstance(widget, TextWidget):
                    self.set_focus(widget)
                    break
                elif isinstance(widget, Button):
                    self.on_key_press(pyglet.window.key.ENTER, None)
                    break
        else:
            self.set_focus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                dir = 0

            self.set_focus(self.widgets[(i + dir) % len(self.widgets)])
        elif symbol == pyglet.window.key.ENTER:
            for widget in self.widgets:
                if self.widgets.index(widget) <= 2:
                    vl.hsvLimitLower[self.widgets.index(widget)] = np.uint8(widget.document.text)
                elif 2 < self.widgets.index(widget) <= 5:
                    vl.hsvLimitUpper[self.widgets.index(widget) - 3] = np.uint8(widget.document.text)
            i = 6
            for prop in visionProperties:
                if isinstance(self.widgets[i], Button):
                    break
                else:
                    vl.visionProperties[prop] = int(self.widgets[i].document.text)
                    i += 1
#            print(hsvLimitLower)
#            print(hsvLimitUpper)
#            print(visionProperties)
        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
            cv.destroyAllWindows()

    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)


window = Window(resizable=True)
pyglet.clock.schedule(vl.isoTarget)
pyglet.app.run()
