import ac
import acsys

from collections import deque

from modules.ac_gl_utils import Point
from modules.ac_gl_utils import Quad

BASE_PADDING = 2.0


class Trace:
    """Driver input trace drawable.

    Args:
        cfg (obj:Config): Object for app configuration.
        telemetry (obj:TelemetryData): Instance of TelemetryData.
        color (tuple): r,g,b,a on 0 to 1 scale.
    """
    def __init__(self, cfg, telemetry, color):
        self.cfg = cfg
        self.telemetry = telemetry

        self.time_window = self.cfg.time_window
        self.sample_rate = self.cfg.sample_rate
        self.sample_size = self.time_window * self.sample_rate

        self.color = color
        self.thickness = self.cfg.trace_size
        self.half_thickness = self.thickness / 2

        # Trace line starting point
        self.graph_origin = Point(0 + BASE_PADDING, self.cfg.app_height - BASE_PADDING)
        
        # Trace graph dimensions
        self.graph_height = self.cfg.app_height - 2 * BASE_PADDING
        self.graph_width = self.cfg.app_width - 2 * BASE_PADDING

        # Set up render queue and points deques.
        # self.render_queue is a deque of quads, iterated over to draw.
        # (2*sample_size - 1) deque length because there are:
        # N (sample size) data points and N-1 connecting lines between points
        self.render_queue = deque(maxlen=(2 * self.sample_size - 1))
        
        # self.points is a deque of data points, the current and the lag data point.
        # This is used in calculating the quad connecting the data points.
        self.points = deque(maxlen=2)

    def update(self, data_point):
        """Update trace render queue.

        Args:
            data_point (float): New point to add to the trace.
        """
        if self.telemetry.replay_time_multiplier > 0:
            # Update traces only if sim time multiplier is positive

            # Offset all points by one
            for point in self.points:
                point.x -= self.graph_width / (self.sample_size - 1)

            # Move all quads in render queue left by one unit
            for quad in self.render_queue:
                quad.points[0].x -= self.graph_width / (self.sample_size - 1)
                quad.points[1].x -= self.graph_width / (self.sample_size - 1)
                quad.points[2].x -= self.graph_width / (self.sample_size - 1)
                quad.points[3].x -= self.graph_width / (self.sample_size - 1)

            # Add new point
            p = Point(self.graph_origin.x + self.graph_width,
                      self.graph_origin.y - (data_point * self.graph_height))
            self.points.append(p.copy())

            p_lag = self.points[0]
            # Make connecting quad if previous point exists
            # Checked by seeing if points deque is length of two...
            if len(self.points) != 2:
                pass
            elif (p.x > p_lag.x) == (p.y > p_lag.y):
                # If x and y are both greater or smaller than lag x and y
                p1 = Point(p_lag.x + self.half_thickness,
                           p_lag.y - self.half_thickness)
                p2 = Point(p.x + self.half_thickness,
                           p.y - self.half_thickness)
                p3 = Point(p.x - self.half_thickness,
                           p.y + self.half_thickness)
                p4 = Point(p_lag.x - self.half_thickness,
                           p_lag.y + self.half_thickness)
                # Points of a triangle/quad must be passed in CCW order,
                # as this defines the front facing side.
                # Clockwise is back face, which gets culled.
                conn_quad = Quad(p4, p3, p2, p1)
                self.render_queue.append(conn_quad.copy())
            else:
                p1 = Point(p_lag.x - self.half_thickness,
                           p_lag.y - self.half_thickness)
                p2 = Point(p.x - self.half_thickness,
                           p.y - self.half_thickness)
                p3 = Point(p.x + self.half_thickness,
                           p.y + self.half_thickness)
                p4 = Point(p_lag.x + self.half_thickness,
                           p_lag.y + self.half_thickness)
                conn_quad = Quad(p4, p3, p2, p1)
                self.render_queue.append(conn_quad.copy())

            # Make a square around the data point
            p1 = Point(p.x - self.half_thickness,
                       p.y - self.half_thickness)
            p2 = Point(p.x + self.half_thickness,
                       p.y - self.half_thickness)
            p3 = Point(p.x + self.half_thickness,
                       p.y + self.half_thickness)
            p4 = Point(p.x - self.half_thickness,
                       p.y + self.half_thickness)
            square = Quad(p4, p3, p2, p1)
            self.render_queue.append(square.copy())

        elif self.telemetry.replay_time_multiplier == 0:
            # If sim time is paused, dont update traces, skip.
            pass
        else:
            # If sim time multiplier is negative, clear traces to empty defaults
            self.clear()
            
    def draw(self):
        """Draw trace object"""
        
        ac.glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        
        try:
            for quad in self.render_queue:
                ac.glBegin(acsys.GL.Quads)
                ac.glVertex2f(quad.points[0].x, quad.points[0].y)
                ac.glVertex2f(quad.points[1].x, quad.points[1].y)
                ac.glVertex2f(quad.points[2].x, quad.points[2].y)
                ac.glVertex2f(quad.points[3].x, quad.points[3].y)
                ac.glEnd()
        except Exception as e:
            ac.log("Error: \n{error}".format(error=e))
    
    def clear(self):
        """Clears all data and drawn elements of this trace"""
        
        self.points.clear()
        self.render_queue.clear()
