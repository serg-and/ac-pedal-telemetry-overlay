import math

# The classes below are used as building blocks for the OpenGL rendering of vector graphics in Assetto Corsa. 
# All classes are based on the two dimensional cartesian coordinate system.

class Point:
    """A point in a 2D cartesian coordinate system.
    
    Each point is described by an X and a Y coordinate.

    Args:
        x (float): x coordinate.
            optional, defaults to 0
        y (float): y coordinate.
            optional, defaults to 0
    """
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def add(self, p):
        """Add value to Point.
        
        Args:
            p (obj:Point/float): Value to add to the Point x,y.
                Can be Point obj to add different values to x and y,
                or a float to add same value to both x and y.
        """
        # Check if p is a Point object
        # If true, add x,y of p to respective x,y of Point
        # If false, add p to both x and y of Point
        if not isinstance(p, Point): p = Point(p, p)
        self.x += p.x
        self.y += p.y

    def subtract(self, p):
        """Subtract value from Point.
        
        Args:
            p (obj:Point/float): Value to subtract from the Point x,y.
                Can be Point obj to subtract different values from x and y,
                or a float to subtract same value from both x and y.
        """
        # Check if p is a Point object
        # If true, subtract x,y of p from respective x,y of Point
        # If false, subtract p from both x and y of Point        
        if not isinstance(p, Point): p = Point(p, p)
        self.x -= p.x
        self.y -= p.y

    def multiply(self, val):
        """Multiply Point by value.
        
        Args:
            p (obj:Point/float): Value to multiply Point x,y with.
                Can be Point obj to multiply different values with x and y,
                or a float to multiply same value with both x and y.
        """ 
        # Check if p is a Point object
        # If true, multiply x,y of p with respective x,y of Point
        # If false, multiply p with both x and y of Point        
        if not isinstance(p, Point): p = Point(p, p)
        self.x *= p.x
        self.y *= p.y

    def divide(self, val):
        """Divide Point by value.
        
        Args:
            p (obj:Point/float): Value to divide Point x,y by.
                Can be Point obj to divide different values with x and y,
                or a float to divide same value with both x and y.
        """
        # Check if p is a Point object
        # If true, multiply x,y of p with respective x,y of Point
        # If false, multiply p with both x and y of Point        
        if not isinstance(p, Point): p = Point(p, p)
        self.x /= p.x
        self.y /= p.y

    def rotate_rad(self, angle, cor=0):
        """Rotate Point in positive counterclockwise direction.
        
        Rotation is done in radians, optionally around a specified 
        center of rotation. If no center of rotation is specified, 
        Point is rotated around origin (0,0).

        Args:
            angle (float): Rotation in radians.
            cor (obj:Point): Center of rotation (x,y).
        """
        # Calculate trig functions only once beforehand.
        c = math.cos(angle)
        s = math.sin(angle)

        self._rotate(c, s, cor)

    def rotate_deg(self, angle, cor=0):
        """Rotate Point in positive counterclockwise direction.

        Rotation is done in degrees, optionally around a specified 
        center of rotation. If no center of rotation is specified,
        Point is rotated around origin (0,0).

        Args:
            angle (float): Degrees of rotation.
            cor (obj:Point): Center of rotation (x,y).
        """
        # Convert degrees to radians
        angle = angle * math.pi / 180

        # Calculate trig functions
        c = math.cos(angle)
        s = math.sin(angle)

        self._rotate(c, s, cor)

    def _rotate(self, c, s, cor=0):
        """Rotate point in positive counterclockwise direction.

        Args:
            c (float): cosine of desired rotation angle.
            s (float): sine of desired rotation angle.
            cor (obj:Point): center of rotation (x,y).
        """
        # Separate calculation of rotation from trig functions
        # because sine and cosine don't change for same rotation angle
        # Wasteful to recalculate mutiple times when rotating e.g. a quad.
        p = Point(self.x, self.y)

        # Subtract center of rotation coords from Point, 
        # to rotate Point around origin (0,0).
        # After rotation is done, add back center of rotation coords.
        p.subtract(cor)

        # Positive Counterclockwise Rotation
        self.x = p.x * c - p.y * s 
        self.y = p.x * s + p.y * c
        self.add(cor)

    def copy(self):
        """Return a copy of object."""
        return Point(self.x, self.y)


class Line:
    """A line in a 2D cartesian coordinate system.
    
    Each line is described by a set of two points.

    Args:
        p1 (obj:Point): Start point of the line.
        p2 (obj:Point): End point of the line.
    """
    def __init__(self, p1=Point(), p2=Point()):
        self.points = [p1, p2]

    def add(self, p):
        """Add value to all points in Line.

        Args:
            p (obj:Point/float): Value to add to points in Line.
                Can be Point obj to add different values to x and y of points,
                or a float to add same value to both x and y of points.
        """
        for point in self.points:
            point.add(p)

    def subtract(self, p):
        """Subtract value from all points in Line.

        Args:
            p (obj:Point/float): Value to subtract from points in Line.
                Can be Point obj to subtract different values from x and y of points,
                or a float to subtract same value from both x and y of points.
        """
        for point in self.points:
            point.subtract(p)

    def multiply(self, p):
        """Multiply all points in Line with value.

        Args:
            p (obj:Point/float): Value to multiply points in Line with.
                Can be Point obj to multiply different values with x and y of points,
                or a float to multiply same value with both x and y of points.
        """        
        for point in self.points:
            point.multiply(p)

    def divide(self, p):
        """Divide all points in Line by value.

        Args:
            p (obj:Point/float): Value to divide points in Line by.
                Can be Point obj to divide x and y of points with different values,
                or a float to divide both x and y of points by the same value.
        """
        for point in self.points:
            point.divide(p)

    def rotate_rad(self, angle, cor=0):
        """Rotate Line in positive counterclockwise direction.

        Rotation is done in radians, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Line is rotated around origin (0,0).

        Args:
            angle (float): Rotation in radians.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Calculate trig functions only once beforehand.
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def rotate_deg(self, angle, cor=0):
        """Rotate Line in positive counterclockwise direction.

        Rotation is done in degrees, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Line is rotated around origin (0,0).

        Args:
            angle (float): Rotation in degrees.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Convert degrees to radians
        angle = angle * math.pi / 180

        # Calculate trig functions
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def copy(self):
        """Return a copy of object."""
        return Line(self.points[0].copy(), self.points[1].copy())


class Triangle:
    """A triangle in a 2D cartesian coordinate system.

    Each triangle is described by a set of three points.

    Args:
        p1 (obj:Point): First point of Triangle.
        p2 (obj:Point): Second point of Triangle.
        p3 (obj:Point): Third point of Triangle.
    """
    def __init__(self, 
                 p1=Point(), 
                 p2=Point(), 
                 p3=Point()):
        self.points = [p1, p2, p3]

    def add(self, p):
        """Add value to all points in Triangle.

        Args:
            p (obj:Point/float): Value to add to points in Triangle.
                Can be Point obj to add different values to x and y of points,
                or a float to add same value to both x and y of points.
        """
        for point in self.points:
            point.add(p)

    def subtract(self, p):
        """Subtract value from all points in Triangle.

        Args:
            p (obj:Point/float): Value to subtract from points in Triangle.
                Can be Point obj to subtract different values from x and y of points,
                or a float to subtract same value from both x and y of points.
        """
        for point in self.points:
            point.subtract(p)

    def multiply(self, p):
        """Multiply all points in Triangle with value.

        Args:
            p (obj:Point/float): Value to multiply points in Triangle with.
                Can be Point obj to multiply different values with x and y of points,
                or a float to multiply same value with both x and y of points.
        """   
        for point in self.points:
            point.multiply(p)

    def divide(self, p):
        """Divide all points in Triangle by value.

        Args:
            p (obj:Point/float): Value to divide points in Triangle by.
                Can be Point obj to divide x and y of points with different values,
                or a float to divide both x and y of points by the same value.
        """
        for point in self.points:
            point.divide(p)

    def rotate_rad(self, angle, cor=0):
        """Rotate Triangle in positive counterclockwise direction.

        Rotation is done in radians, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Triangle is rotated around origin (0,0).

        Args:
            angle (float): Rotation in radians.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Calculate trig functions only once beforehand.
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def rotate_deg(self, angle, cor=0):
        """Rotate Triangle in positive counterclockwise direction.

        Rotation is done in degrees, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Triangle is rotated around origin (0,0).

        Args:
            angle (float): Rotation in degrees.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Convert degrees to radians
        angle = angle * math.pi / 180

        # Calculate trig functions
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def copy(self):
        """Return a copy of object."""
        return Triangle(self.points[0].copy(),
                        self.points[1].copy(),
                        self.points[2].copy())


class Quad:
    """A quad in a 2D cartesian coordinate system.

    Each quad is described by a set of four points.

    Args:
        p1 (obj:Point): First point of Quad.
        p2 (obj:Point): Second point of Quad.
        p3 (obj:Point): Third point of Quad.
        p4 (obj:Point): Fourth point of Quad
    """
    def __init__(self, 
                 p1=Point(), 
                 p2=Point(), 
                 p3=Point(),
                 p4=Point()):
        self.points = [p1, p2, p3, p4]

    def add(self, p):
        """Add value to all points in Quad.

        Args:
            p (obj:Point/float): Value to add to points in Quad.
                Can be Point obj to add different values to x and y of points,
                or a float to add same value to both x and y of points.
        """
        for point in self.points:
            point.add(p)

    def subtract(self, p):
        """Subtract value from all points in Quad.

        Args:
            p (obj:Point/float): Value to subtract from points in Quad.
                Can be Point obj to subtract different values from x and y of points,
                or a float to subtract same value from both x and y of points.
        """
        for point in self.points:
            point.subtract(p)

    def multiply(self, p):
        """Multiply all points in Quad with value.

        Args:
            p (obj:Point/float): Value to multiply points in Quad with.
                Can be Point obj to multiply different values with x and y of points,
                or a float to multiply same value with both x and y of points.
        """   
        for point in self.points:
            point.multiply(p)

    def divide(self, p):
        """Divide all points in Quad by value.

        Args:
            p (obj:Point/float): Value to divide points in Quad by.
                Can be Point obj to divide x and y of points with different values,
                or a float to divide both x and y of points by the same value.
        """
        for point in self.points:
            point.divide(p)

    def rotate_rad(self, angle, cor=0):
        """Rotate Quad in positive counterclockwise direction.

        Rotation is done in radians, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Quad is rotated around origin (0,0).

        Args:
            angle (float): Rotation in radians.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Calculate trig functions only once beforehand.
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def rotate_deg(self, angle, cor=0):
        """Rotate Quad in positive counterclockwise direction.

        Rotation is done in degrees, optionally around a specified
        center of rotation. If no center of rotation is specified,
        the Quad is rotated around origin (0,0).

        Args:
            angle (float): Rotation in degrees.
            cor (obj:Point): Center of rotation (x,y)
        """
        # Convert degrees to radians
        angle = angle * math.pi / 180

        # Calculate trig functions
        c = math.cos(angle)
        s = math.sin(angle)

        for points in self.points:
            points._rotate(c, s, cor)

    def copy(self):
        """Return a copy of object."""
        return Quad(self.points[0].copy(),
                    self.points[1].copy(),
                    self.points[2].copy(),
                    self.points[3].copy())
