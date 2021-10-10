import numpy as np


def to_int(_float):
    return int(round(_float) + 0.1)


class Mask:
    """
    Object managing geometry information about detector-accessible area.
    """
    def __init__(self, frame_width, frame_height, radius, radius_y=0,
                 offset_x=0, offset_y=0):
        """
        :param frame_width: Width of collected frame in pixels.
        :type frame_width: int
        :param frame_height: Height of collected frame in pixels.
        :type frame_height: int
        :param radius: Horizontal radius of detector-accessible area on frame.
        :type radius: int
        :param radius_y: Vertical radius of accessible area, if unequal radius.
        :type radius_y: int
        :param offset_x: Detector-accessible area horizontal offset, default 0.
        :type offset_x: int
        :param offset_y: Detector-accessible area vertical offset, default 0.
        :type offset_y: int
        """
        self.x_lim = frame_width
        self.y_lim = frame_height
        self.r_x = radius
        self.r_y = radius if radius_y is 0 else radius_y
        self.x_center = self.x_lim / 2 + offset_x
        self.y_center = self.y_lim / 2 + offset_y

    @property
    def north_gap(self):
        return self.y_lim - self.y_center - self.r_y

    @property
    def east_gap(self):
        return self.x_lim - self.x_center - self.r_x

    @property
    def south_gap(self):
        return self.y_center - self.r_y

    @property
    def west_gap(self):
        return self.x_center - self.r_x

    @property
    def clips_north(self):
        return self.north_gap < 0

    @property
    def clips_west(self):
        return self.west_gap < 0

    @property
    def clips_south(self):
        return self.south_gap < 0

    @property
    def clips_east(self):
        return self.east_gap < 0

    @property
    def north_rect(self):
        return 0, to_int(self.y_lim-self.north_gap), \
               to_int(self.x_lim), to_int(self.north_gap)

    @property
    def east_rect(self):
        return to_int(self.x_lim-self.east_gap), 0, \
               to_int(self.east_gap), to_int(self.y_lim)

    @property
    def south_rect(self):
        return 0, 0, to_int(self.x_lim), to_int(self.south_gap)

    @property
    def west_rect(self):
        return 0, 0, to_int(self.west_gap), to_int(self.y_lim)

    @property
    def ne_start(self):
        return np.arccos(1+self.north_gap/self.r_y) if self.clips_north else 0

    @property
    def ne_end(self):
        return np.arcsin(1+self.east_gap/self.r_x) \
            if self.clips_east else np.pi/2

    @property
    def ne_len(self):
        return self.ne_end - self.ne_start

    @property
    def se_start(self):
        return np.pi - np.arcsin(1+self.east_gap/self.r_x) \
            if self.clips_east else np.pi/2

    @property
    def se_end(self):
        return np.pi - np.arccos(1+self.south_gap/self.r_y) \
            if self.clips_south else np.pi

    @property
    def se_len(self):
        return self.se_end - self.se_start

    @property
    def sw_start(self):
        return np.pi + np.arccos(1+self.south_gap/self.r_y) \
            if self.clips_south else np.pi

    @property
    def sw_end(self):
        return np.pi + np.arcsin(1+self.west_gap/self.r_x) \
            if self.clips_west else 3*np.pi/2

    @property
    def sw_len(self):
        return self.sw_end - self.sw_start

    @property
    def nw_start(self):
        return 2*np.pi - np.arcsin(1+self.west_gap/self.r_x) \
            if self.clips_west else 3*np.pi/2

    @property
    def nw_end(self):
        return 2*np.pi - np.arccos(1+self.north_gap/self.r_y) \
            if self.clips_north else 2*np.pi

    @property
    def nw_len(self):
        return self.nw_end - self.nw_start

    @property
    def edge_len(self):
        return self.ne_len + self.se_len + self.sw_len + self.nw_len

    def edge_x_at(self, phi):
        return self.x_center + self.r_x * np.sin(phi)

    def edge_y_at(self, phi):
        return self.y_center + self.r_y * np.cos(phi)

    def ne_rect_at(self, phi):
        return to_int(self.edge_x_at(phi)), \
               to_int(self.edge_y_at(phi)), \
               to_int(self.x_lim-self.edge_x_at(phi)), \
               to_int(self.y_lim-self.edge_y_at(phi))

    def se_rect_at(self, phi):
        return to_int(self.edge_x_at(phi)), 0, \
               to_int(self.x_lim-self.edge_x_at(phi)), \
               to_int(self.edge_y_at(phi))

    def sw_rect_at(self, phi):
        return 0, 0, \
               to_int(self.edge_x_at(phi)), \
               to_int(self.edge_y_at(phi))

    def nw_rect_at(self, phi):
        return 0, to_int(self.edge_y_at(phi)), \
               to_int(self.edge_x_at(phi)), \
               to_int(self.y_lim-self.edge_y_at(phi))

    def export(self, path='edge_mask.mac', resolution=100):
        """
        Generate CrysAlisPRO .mac file containing a mask for specified detector
        which excludes empty sides and corners using "dc rejectrect" commands.
        Please mind that CrysAlis accepts up to ~100 of these commands,
        so resolution should be kept below 100 or even lower.

        :param path: A path to .mac file to be created, default 'edge_mask.mac'.
        :type path: str
        :param resolution: upper limit of commands used, default 100.
        :type resolution: int
        """
        rects = list()
        rects += [self.north_rect] * (1 - self.clips_north)
        rects += [self.east_rect] * (1 - self.clips_east)
        rects += [self.south_rect] * (1 - self.clips_south)
        rects += [self.west_rect] * (1 - self.clips_west)

        resolution -= len(rects)
        res_ne = int(self.ne_len / self.edge_len * resolution)
        res_se = int(self.se_len / self.edge_len * resolution)
        res_sw = int(self.sw_len / self.edge_len * resolution)
        res_nw = int(self.nw_len / self.edge_len * resolution)
        if self.ne_len > 0:
            for phi in np.linspace(self.ne_start, self.ne_end, res_ne+2)[1:-1]:
                rects.append(self.ne_rect_at(phi))
        if self.se_len > 0:
            for phi in np.linspace(self.se_start, self.se_end, res_se+2)[1:-1]:
                rects.append(self.se_rect_at(phi))
        if self.sw_len > 0:
            for phi in np.linspace(self.sw_start, self.sw_end, res_sw+2)[1:-1]:
                rects.append(self.sw_rect_at(phi))
        if self.nw_len > 0:
            for phi in np.linspace(self.nw_start, self.nw_end, res_nw+2)[1:-1]:
                rects.append(self.nw_rect_at(phi))
        with open(path, 'w') as file:
            for rect in rects:
                file.write('dc rejectrect {} {} {} {}\n'.format(*rect))


if __name__ == '__main__':
    m = Mask(2048, 2048, 1000)
    m.export(resolution=100)