import pygame
import math

TWO_PI = 2 * math.pi


class Track:
    def __init__(self, center_x, center_y, radius_x, radius_y, track_width=100):
        self.center_x = center_x
        self.center_y = center_y
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.track_width = track_width

        self.inner_rx = radius_x - track_width
        self.inner_ry = radius_y - track_width
        self.centerline_rx = (radius_x + self.inner_rx) / 2
        self.centerline_ry = (radius_y + self.inner_ry) / 2

        self.start_finish_angle = 0

        # pit lane geometry (bottom section of the oval)
        self.pit_entry_angle = math.pi * 0.30   # ~54°  right-bottom area
        self.pit_exit_angle = math.pi * 0.70    # ~126° left-bottom area
        self.pit_lane_offset = 50               # pixels inside the inner boundary

        self.pit_lane_rx = self.inner_rx - self.pit_lane_offset
        self.pit_lane_ry = self.inner_ry - self.pit_lane_offset

        self._build_pit_points()

    def _build_pit_points(self):
        steps = 40
        self.pit_lane_points = []
        for i in range(steps + 1):
            t = i / steps
            a = self.pit_entry_angle + (self.pit_exit_angle - self.pit_entry_angle) * t
            x = self.center_x + self.pit_lane_rx * math.cos(a)
            y = self.center_y + self.pit_lane_ry * math.sin(a)
            self.pit_lane_points.append((x, y))

    def angle_in_pit_zone(self, angle):
        """Return True if *angle* is between pit entry and pit exit."""
        a = angle % TWO_PI
        return self.pit_entry_angle <= a <= self.pit_exit_angle

    def pit_lane_pos(self, angle):
        """Return (x, y) on the pit lane arc for a given angle."""
        x = self.center_x + self.pit_lane_rx * math.cos(angle)
        y = self.center_y + self.pit_lane_ry * math.sin(angle)
        return x, y

    # ---- drawing ----------------------------------------------------------

    def draw(self, screen):
        # outer boundary
        pygame.draw.ellipse(screen, (100, 100, 100),
            (self.center_x - self.radius_x, self.center_y - self.radius_y,
             self.radius_x * 2, self.radius_y * 2), 5)

        # inner boundary
        pygame.draw.ellipse(screen, (100, 100, 100),
            (self.center_x - self.inner_rx, self.center_y - self.inner_ry,
             self.inner_rx * 2, self.inner_ry * 2), 5)

        # centerline
        points = []
        for i in range(120):
            a = TWO_PI * i / 120
            x = self.center_x + self.centerline_rx * math.cos(a)
            y = self.center_y + self.centerline_ry * math.sin(a)
            points.append((x, y))
        pygame.draw.lines(screen, (60, 60, 60), True, points, 1)

        # start/finish line
        a = self.start_finish_angle
        inner_x = self.center_x + self.inner_rx * math.cos(a)
        inner_y = self.center_y + self.inner_ry * math.sin(a)
        outer_x = self.center_x + self.radius_x * math.cos(a)
        outer_y = self.center_y + self.radius_y * math.sin(a)
        pygame.draw.line(screen, (255, 255, 255), (inner_x, inner_y), (outer_x, outer_y), 3)

        self._draw_pit_lane(screen)

    def _draw_pit_lane(self, screen):
        # pit lane path
        if len(self.pit_lane_points) > 1:
            pygame.draw.lines(screen, (200, 160, 60), False, self.pit_lane_points, 2)

        # entry marker
        a = self.pit_entry_angle
        inner = (self.center_x + self.inner_rx * math.cos(a),
                 self.center_y + self.inner_ry * math.sin(a))
        pit = self.pit_lane_pos(a)
        pygame.draw.line(screen, (0, 200, 0), inner, pit, 2)

        # exit marker
        a = self.pit_exit_angle
        inner = (self.center_x + self.inner_rx * math.cos(a),
                 self.center_y + self.inner_ry * math.sin(a))
        pit = self.pit_lane_pos(a)
        pygame.draw.line(screen, (200, 0, 0), inner, pit, 2)

        # "PIT" label
        mid_angle = (self.pit_entry_angle + self.pit_exit_angle) / 2
        lx, ly = self.pit_lane_pos(mid_angle)
        font = pygame.font.Font(None, 24)
        label = font.render("PIT", True, (200, 160, 60))
        screen.blit(label, (int(lx) - label.get_width() // 2,
                            int(ly) - label.get_height() // 2 - 20))