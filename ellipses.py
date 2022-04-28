import ipywidgets
from matplotlib import pyplot as P
import numpy as N


class EllipsisStack(ipywidgets.HBox):
    def __init__(self, rotate_text=True):
        super(EllipsisStack, self).__init__()
        self.rot_txt = rotate_text
        output = ipywidgets.Output()
        self.fig = None
        self.dpi = 150
        self.ax = None
        self.ax_logo = None
        self.logo = P.imread("CEA_Irfu.png")
        print(self.logo.shape)
        with output:
            self.create_figure_and_axis()
        self.inserted_txt_2 = "JACQUES PREVERT"
        self.inserted_txt_1 = "École maternelle"
        self.letter_cols = ['y', 'c', 'g', 'r']

        self.n = 15
        self.a0 = 8.4
        self.b0 = 5.9
        self.np0 = 4000
        self.extinct = 2
        self.do_rot = True
        self.plot_text = True
        self.dt = 25.0

        # Define controls
        n_slider = ipywidgets.IntSlider(min=5, max=50, value=self.n, step=1, description="n", continuous_update=True)
        ext_slider = ipywidgets.IntSlider(min=0, max=4, value=self.extinct, step=1, description="extinction",
                                          continuous_update=True)
        a0_slider = ipywidgets.FloatSlider(min=1.0, max=10.0, value=self.a0, step=0.1, readout_format='.1f',
                                           continuous_update=False, description="a")
        b0_slider = ipywidgets.FloatSlider(min=1.0, max=10.0, value=self.b0, step=0.1, readout_format='.1f',
                                           continuous_update=False, description="b")
        np0_slider = ipywidgets.IntSlider(min=100, max=5000, value=self.np0, step=10, description="np0",
                                          continuous_update=False)
        dt_slider = ipywidgets.FloatSlider(min=10.0, max=50.0, value=self.dt, step=1.0, readout_format='.1f',
                                           continuous_update=False, description="dt (deg)")
        rot_cb = ipywidgets.Checkbox(value=self.do_rot, description="Rotate ellipses")

        controls = ipywidgets.VBox([n_slider, ext_slider, a0_slider, b0_slider, np0_slider, dt_slider, rot_cb])
        controls.layout = self.make_box_layout()
        out_box = ipywidgets.Box([output])
        out_box.layout = self.make_box_layout()

        # Observe stuff
        a0_slider.observe(self.update_a0, 'value')
        b0_slider.observe(self.update_b0, 'value')
        np0_slider.observe(self.update_np0, 'value')
        n_slider.observe(self.update_n, 'value')
        ext_slider.observe(self.update_extinction, 'value')
        dt_slider.observe(self.update_dt, 'value')
        rot_cb.observe(self.update_rot, 'value')

        # Add to children
        self.children = [controls, out_box]

        self.redraw_ellipses()
        self.insert_logo()

    def create_figure_and_axis(self, white_background=False):
        bgcolor = 'w' if white_background else 'k'
        self.fig, self.ax = P.subplots(subplot_kw={'facecolor': bgcolor, 'aspect': 'equal'},
                                       constrained_layout=True, figsize=(11.693, 8.268),  # A4
                                       facecolor=bgcolor)

        height = 0.1
        self.ax_logo = self.fig.add_axes([0.75, 0.8, height*self.logo.shape[1]/self.logo.shape[0], height],
                                         anchor='NE', zorder=1)
        self.ax_logo.axis('off')

        # self.ax.set_frame_on(False)
        self.fig.canvas.toolbar_position = 'bottom'
        self.ax.axis("off")

    def insert_logo(self):
        if self.ax_logo is not None:
            self.ax_logo.imshow(self.logo)

    @staticmethod
    def make_box_layout():
        return ipywidgets.Layout(border='solid 1px black', margin='0px 10px 10px 0px',
                                 padding='5px 5px 5px 5px')  # , height='350px')

    def parameters(self):
        return {'n': self.n, 'a0': self.a0, 'b0': self.b0, 'np0': self.np0, 'dt': self.dt}

    def update_n(self, change):
        self.n = change.new
        self.redraw_ellipses()

    def update_extinction(self, change):
        self.extinct = change.new
        self.redraw_ellipses()

    def update_a0(self, change):
        self.a0 = change.new
        self.redraw_ellipses()

    def update_b0(self, change):
        self.b0 = change.new
        self.redraw_ellipses()

    def update_np0(self, change):
        self.np0 = change.new
        self.redraw_ellipses()

    def update_dt(self, change):
        self.dt = change.new
        self.redraw_ellipses()

    def update_rot(self, change):
        self.do_rot = change.new
        self.redraw_ellipses()

    def redraw_ellipses(self, savefigs=False):
        for line in self.ax.lines[::-1]:
            line.remove()
        for text in self.ax.texts[::-1]:
            text.remove()

        for i in range(self.n):
            ang = i * self.dt
            cang = N.cos(ang * N.pi / 180.0)
            sang = N.sin(ang * N.pi / 180.0)
            if i == 0:
                a = self.a0
                b = self.b0
                np = self.np0
            else:
                delta = (a / b - b / a) * N.sin(self.dt * N.pi / 180.0)
                r = N.sqrt(1 + delta ** 2 / 4.0) - delta / 2.0
                # print("r= ", r)
                a = a * r
                b = b * r
                if self.extinct == 4:
                    np = int(np*(1.0-N.sqrt(1.0-r)))
                elif self.extinct == 3:
                    np = int(np * r)
                elif self.extinct == 2:
                    np = int(np * (1.0 - (1.0 - r)**2))
                elif self.extinct == 1:
                    np = int(np * (1.0 - (1.0 - r) ** 3))

            # Random points along a 'thick' elliptical trajectory (thickness = eps)
            eps = 0.15
            p = 1.0 + N.random.uniform(size=np) * eps - eps / 2.0
            delta = N.random.uniform(size=np) * 2 * N.pi
            x = p * a * N.cos(delta)
            # y = ((p-1.0)*a + b)*N.sin(delta)
            y = p * b * N.sin(delta)
            # Rotation by angle 'ang'
            if self.do_rot:
                xrot = x * cang - y * sang
                yrot = x * sang + y * cang
            else:
                xrot = x
                yrot = y
            self.ax.plot(xrot, yrot, marker=',', color='y', linewidth=0)

            # Plot cross at origin
            self.ax.plot([-a / 100.0, a / 100.0], [0.0, 0.0], 'y--', linewidth=1)
            self.ax.plot([0.0, 0.0], [-a / 100.0, a / 100.0], 'y--', linewidth=1)

            if self.plot_text:
                self.insert_text(i)

            # Set axis limits
            self.ax.set_xlim(-1.35 * self.a0, 1.35 * self.a0)

            if i == 0:
                self.insert_logo()

            if savefigs:
                if i != 0:
                    self.ax_logo.cla()
                    self.ax_logo.axis("off")
                P.subplots_adjust(0.03, 0.05, 0.98, 0.97)
                P.savefig("png/ellipsis_{iell:02d}.png".format(iell=i), facecolor='w', dpi=self.dpi)
                self.ax.cla()
                self.ax.axis("off")

    def insert_text(self, iellipse):
        ang = iellipse * self.dt
        cang = N.cos(ang * N.pi / 180.0)
        sang = N.sin(ang * N.pi / 180.0)

        # Insert school type (lower left corner)
        x = - self.a0 / 4.0
        y = -self.b0 * 1.1
        if self.rot_txt:
            if iellipse < len(self.inserted_txt_1):
                if not self.do_rot:
                    xrot = x * cang + y * sang
                    yrot = -x * sang + y * cang
                else:
                    xrot = x
                    yrot = y
                    ang = 0.0

                txt = self.inserted_txt_1[-1-iellipse] if iellipse < self.n - 1 else self.inserted_txt_1[:-iellipse]
                txt += " " * iellipse
                col = self.letter_cols[iellipse % len(self.letter_cols)]
                self.ax.text(xrot, yrot, txt, size=14, rotation=-ang, ha="right", va="center",
                             fontdict={'color': col, 'family': 'Monospace'})  # 'Andale Mono'})
        else:
            if iellipse == 0: # Only display on first slide
                for ic, c in enumerate(self.inserted_txt_1):
                    txt = self.inserted_txt_1[-1 - ic] + " " * ic
                    col = self.letter_cols[ic % len(self.letter_cols)]
                    self.ax.text(x, y, txt, size=14, ha="right", va="center",
                                 fontdict={'color': col, 'family': 'Monospace'})  # 'Andale Mono'})

        # Insert school name (lower right corner)
        x = self.a0 / 4.0
        y = -self.b0 * 1.1
        if self.rot_txt:
            if iellipse < len(self.inserted_txt_2):

                if not self.do_rot:
                    xrot = x * cang + y * sang
                    yrot = -x * sang + y * cang
                else:
                    xrot = x
                    yrot = y
                    ang = 0.0

                txt = " " * iellipse
                txt += self.inserted_txt_2[iellipse] if iellipse < self.n - 1 else self.inserted_txt_2[iellipse:]
                col = self.letter_cols[iellipse % len(self.letter_cols)]
                self.ax.text(xrot, yrot, txt, size=14, rotation=-ang, ha="left", va="center",
                             fontdict={'color': col, 'family': 'Monospace'})  # 'Andale Mono'})
        else:
            if iellipse == 0:  # Only display on first slide
                for ic, c in enumerate(self.inserted_txt_2):
                    txt = " " * ic + self.inserted_txt_2[ic]
                    col = self.letter_cols[ic % len(self.letter_cols)]
                    self.ax.text(x, y, txt, size=14, ha="left", va="center",
                                 fontdict={'color': col, 'family': 'Monospace'})  # 'Andale Mono'})

        # Insert o at alignment hole position
        x = -0.8 * self.a0 / N.sqrt(2.0)
        y = 1.4 * self.b0 / N.sqrt(2.0)
        if not self.do_rot:
            xrot = x * cang + y * sang
            yrot = -x * sang + y * cang
        else:
            xrot = x
            yrot = y
            ang = 0.0
        self.ax.text(xrot, yrot, "o", size=10, rotation=-ang, ha="left", va="center",
                     fontdict={'color': 'y', 'family': 'Monospace'})

    def save_figures(self, dpi=150):
        self.create_figure_and_axis(white_background=True)
        self.dpi = dpi
        self.redraw_ellipses(savefigs=True)


__all__ = ["EllipsisStack"]
