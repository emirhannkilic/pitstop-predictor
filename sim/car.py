import pygame
import math

TWO_PI = 2 * math.pi
PIT_STOP_TIME = 3.0
PIT_LANE_SPEED_FACTOR = 0.35


class Car:
    def __init__(self, angle, speed, center_x, center_y, radius_x, radius_y, color, car_id, driving_style):
        self.angle = angle
        self.speed = speed
        self.center_x = center_x
        self.center_y = center_y
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.color = color
        self.car_id = car_id
        self.driving_style = driving_style

        self.lap_count = 0
        self.tire_wear = 0.0
        self.base_speed = speed
        self.laps_since_pit = 0

        if self.driving_style == "aggressive":
            self.wear_rate = 0.009
        elif self.driving_style == "conservative":
            self.wear_rate = 0.004
        else:  # normal
            self.wear_rate = 0.006

        self.x = 0
        self.y = 0
        self.traffic_factor = 1.0
        self.sc_factor = 1.0

        # pit state
        self.in_pit = False
        self.wants_pit = False
        self.pit_timer = 0.0
        self.pit_phase = "racing"  # racing | pit_in | pit_stop | pit_out

    def update(self, dt, track=None):
        old_angle = self.angle

        if self.pit_phase == "racing":
            self._update_racing(dt, old_angle, track)
        elif self.pit_phase == "pit_in":
            self._update_pit_in(dt, track)
        elif self.pit_phase == "pit_stop":
            self._update_pit_stop(dt, track)
        elif self.pit_phase == "pit_out":
            self._update_pit_out(dt, track)

    # --- racing (normal) ---------------------------------------------------

    def _update_racing(self, dt, old_angle, track):
        self.tire_wear += self.wear_rate * dt
        self.tire_wear = min(self.tire_wear, 1.0)

        self.tire_factor = 1 - 0.30 * self.tire_wear
        current_speed = self.base_speed * self.tire_factor * self.traffic_factor * self.sc_factor
        self.angle = (self.angle + current_speed * dt) % TWO_PI

        self.x = self.center_x + self.radius_x * math.cos(self.angle)
        self.y = self.center_y + self.radius_y * math.sin(self.angle)

        if old_angle > 5.0 and self.angle < 1.0:
            self.lap_count += 1
            self.laps_since_pit += 1

        if self.wants_pit and track and old_angle < self.angle:
            if old_angle < track.pit_entry_angle <= self.angle:
                self.in_pit = True
                self.wants_pit = False
                self.pit_phase = "pit_in"

    # --- pit_in: driving entry -> pit box at reduced speed -----------------

    def _update_pit_in(self, dt, track):
        speed = self.base_speed * PIT_LANE_SPEED_FACTOR
        self.angle = (self.angle + speed * dt) % TWO_PI

        if track:
            mid = (track.pit_entry_angle + track.pit_exit_angle) / 2
            self.x, self.y = track.pit_lane_pos(self.angle)
            if self.angle >= mid:
                self.angle = mid
                self.x, self.y = track.pit_lane_pos(mid)
                self.pit_phase = "pit_stop"
                self.pit_timer = PIT_STOP_TIME

    # --- pit_stop: stationary, changing tires ------------------------------

    def _update_pit_stop(self, dt, track):
        self.pit_timer -= dt
        if track:
            mid = (track.pit_entry_angle + track.pit_exit_angle) / 2
            self.x, self.y = track.pit_lane_pos(mid)

        if self.pit_timer <= 0:
            self.tire_wear = 0.0
            self.laps_since_pit = 0
            self.pit_phase = "pit_out"

    # --- pit_out: driving pit box -> exit at reduced speed -----------------

    def _update_pit_out(self, dt, track):
        speed = self.base_speed * PIT_LANE_SPEED_FACTOR
        self.angle = (self.angle + speed * dt) % TWO_PI

        if track:
            self.x, self.y = track.pit_lane_pos(self.angle)
            if self.angle >= track.pit_exit_angle:
                self.angle = track.pit_exit_angle
                self.x = self.center_x + self.radius_x * math.cos(self.angle)
                self.y = self.center_y + self.radius_y * math.sin(self.angle)
                self.in_pit = False
                self.pit_phase = "racing"

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)