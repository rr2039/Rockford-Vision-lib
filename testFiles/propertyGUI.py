import pyglet
import cv2 as cv
import numpy as np

vs = cv.VideoCapture(0)
hsvLimitLower = np.array([70, 90, 60])  # (H,S,V) #243
hsvLimitUpper = np.array([100, 255, 255])
visionProperties = {"areaMin": 3,
                    "widthMin": 10,
                    "widthMax": 1003,
                    "heightMin": 2,
                    "heightMax": 1003,
                    "vertexMin": 0,
                    "vertexMax": 1000000,
                    "ratioMin": 1,
                    "ratioMax": 1000,
                    "solidityMin": 5,
                    "solidityMax": 48}


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
        global hsvLimitLower
        global hsvLimitUpper
        global visionProperties
        super(Window, self).__init__(400, 720, caption='Vision Settings')

        self.batch = pyglet.graphics.Batch()
        self.labels = [
            pyglet.text.Label('HSV LOWERLIMIT', x=10, y=700, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch),
            pyglet.text.Label('HSV UPPERLIMIT', x=10, y=640, anchor_y='bottom',
                              color=(0, 0, 0, 255), batch=self.batch)]
        self.widgets = [
            TextWidget(str(hsvLimitLower[0]), 200, 700, 30, self.batch),
            TextWidget(str(hsvLimitLower[1]), 240, 700, 30, self.batch),
            TextWidget(str(hsvLimitLower[2]), 280, 700, 30, self.batch),
            TextWidget(str(hsvLimitUpper[0]), 200, 640, 30, self.batch),
            TextWidget(str(hsvLimitUpper[1]), 240, 640, 30, self.batch),
            TextWidget(str(hsvLimitUpper[2]), 280, 640, 30, self.batch)]

        for prop in visionProperties:
            self.widgets.append(TextWidget(str(visionProperties[prop]), 200,
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
        global hsvLimitLower
        global hsvLimitUpper
        global visionProperties
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
                    hsvLimitLower[self.widgets.index(widget)] = np.uint8(widget.document.text)
                elif 2 < self.widgets.index(widget) <= 5:
                    hsvLimitUpper[self.widgets.index(widget) - 3] = np.uint8(widget.document.text)
            i = 6
            for prop in visionProperties:
                if isinstance(self.widgets[i], Button):
                    break
                else:
                    visionProperties[prop] = int(self.widgets[i].document.text)
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


def filterContours(contours):
    output = []
    global visionProperties
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if (w < visionProperties["widthMin"] or w > visionProperties["widthMax"]):
            continue
        if (h < visionProperties["heightMin"] or h > visionProperties["heightMax"]):
            continue
        area = cv.contourArea(contour)
        if area < visionProperties["areaMin"]:
            continue
        hull = cv.convexHull(contour)
        solid = 100 * area / cv.contourArea(hull)
        if (solid < visionProperties["solidityMin"]) or (solid > visionProperties["solidityMax"]):
            continue
        if (len(contour) < visionProperties["vertexMin"] or len(contour) > visionProperties["vertexMax"]):
            continue
        ratio = (float)(w) / h
        if (ratio < visionProperties["ratioMin"] or ratio > visionProperties["ratioMax"]):
            continue
        output.append(contour)
    return output


def main(dt):
    global vs
    global hsvLimitLower
    global hsvLimitUpper
    retval, frame = vs.read()
    # frame = cv.imread(r"9ft.png")
    cv.imshow('frame', frame)
    kernel = np.ones((5, 5), np.uint8)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, hsvLimitLower, hsvLimitUpper)
    cv.imshow('mask', mask)
    contours, hierarchy = cv.findContours(mask, 1, 2)
#   cnt = contours[0]
    backdrop = np.zeros((480, 640, 3))  # Backdrop to display the contours

    frame_and_target_contour = frame
    filteredContours = filterContours(contours)
    try:
        cnt = filteredContours[0]
        M = cv.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        print(cx)
        print(cy)
    except:
        pass
    try:
        x, y, w, h = cv.boundingRect(filteredContours[0])
        rect = cv.rectangle(backdrop, (x, y),
                            ((x + w), (y + h)), (255, 0, 0), 10)
        print(rect)
    except:
        pass
    cv.imshow('processed', cv.drawContours(backdrop,
              filteredContours, -1, (0, 255, 0), 3))


window = Window(resizable=True)
pyglet.clock.schedule(main)
pyglet.app.run()
