from datetime import datetime, timedelta
from math import asin, sin, acos, cos, atan2, tan, radians, degrees, sqrt, pi
import operator

# lots of help from http://www.movable-type.co.uk/scripts/latlong.html

EARTHS_RADIUS = 6371 * 1000.0 # meters


class Coordinates:
    def __init__(self, latitude, longitude):
        self.latitude  = latitude
        self.longitude = longitude

    latitude = property(operator.attrgetter('_latitude'))
    @latitude.setter
    def latitude(self, lat):
        if not isinstance(lat, (int, float, complex)): raise Exception('latitude is not a number')
        if not -90 <= lat <= 90: raise Exception('latitude must be between -90 and 90')
        self._latitude = lat

    longitude = property(operator.attrgetter('_longitude'))
    @longitude.setter
    def longitude(self, lon):
        if not isinstance(lon, (int, float, complex)): raise Exception('longitude is not a number')
        if not -180 <= lon <= 180: raise Exception('latitude must be between -180 and 180')
        self._longitude = lon

    def pp(self):
        print("Latitude: ", self.latitude)
        print("Longitude: ", self.longitude)


class Course:
    '''
    Speed: m/s
    Bearing: clockwise degrees from north
    '''

    def __init__(self, bearing, speed, coordinates, timestamp):
        self.bearing     = bearing
        self.speed       = speed
        self.coordinates = coordinates
        self.timestamp   = timestamp

    bearing = property(operator.attrgetter('_bearing'))
    @bearing.setter
    def bearing(self, b):
        if not isinstance(b, (int, float, complex)): raise Exception('bearing is not a number')
        if not 0 <= b < 360: raise Exception('bearing must be greater or equal to 0 and less than 360')
        self._bearing = b

    speed = property(operator.attrgetter('_speed'))
    @speed.setter
    def speed(self, s):
        if not isinstance(s, (int, float, complex)): raise Exception('bearing is not a number')
        self._speed = s

    coordinates = property(operator.attrgetter('_coordinates'))
    @coordinates.setter
    def coordinates(self, c):
        if not isinstance(c, Coordinates): raise Exception('coordinates must be Coordinates class')
        self._coordinates = c

    timestamp = property(operator.attrgetter('_timestamp'))
    @timestamp.setter
    def timestamp(self, t):
        if not isinstance(t, datetime): raise Exception('timestamp must be datetime')
        self._timestamp = t

    def predicted_coordinates(self, timestamp=None):
        if not timestamp: timestamp = datetime.now()
        distance = self.speed * (timestamp - self.timestamp).total_seconds() # meters
        angular_distance = distance / EARTHS_RADIUS

        brng = radians(self.bearing)
        lat1 = radians(self.coordinates.latitude)
        lon1 = radians(self.coordinates.longitude)

        lat2 = asin(sin(lat1) * cos(angular_distance) + cos(lat1) * sin(angular_distance) * cos(brng))
        lon2 = lon1 + atan2(sin(brng) * sin(angular_distance) * cos(lat1), cos(angular_distance) - sin(lat1) * sin(lat2))

        predicted_latitude = round(degrees(lat2), 8)
        predicted_longitude = round(degrees(lon2), 8)

        return Coordinates(predicted_latitude, predicted_longitude)


class Craft:
    '''
    Hmmmmm.....
    '''

    def __init__(self):
        self.courses = []

    def append_course(self, course):
        if not isinstance(course, Course): raise Exception('course must be Course class')
        self.courses.append(course)

    def latest_course(self):
        self.courses[-1]

    def predicted_coordinates(self, timestamp=None):
        return latest_course.predicted_coordinates(timestamp)


def calculate_bearing(coordinates1, coordinates2):
    lat1 = coordinates1.latitude
    lon1 = coordinates1.longitude
    lat2 = coordinates2.latitude
    lon2 = coordinates2.longitude

    y = sin(lon2 - lon1) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1)

    return degrees(atan2(y, x))


def calculate_antipodes(coordinates):
    if not isinstance(coordinates, Coordinates): raise Exception('coordinates must be Coordinates class')

    latitude = -coordinates.latitude
    if coordinates.longitude < 0:
        longitude = 180 - abs(coordinates.longitude)
    else:
        longitude = -(180 - abs(coordinates.longitude))

    return Coordinates(latitude, longitude)


def calculate_intersection(course1, course2):
    if not (isinstance(course1, Course) and isinstance(course2, Course)): raise Exception('courses must be Course class')

    lat1 = radians(course1.coordinates.latitude)
    lon1 = radians(course1.coordinates.longitude)
    brng1 = radians(course1.bearing)
    lat2 = radians(course2.coordinates.latitude)
    lon2 = radians(course2.coordinates.longitude)
    brng2 = radians(course2.bearing)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    angular_dist12 = 2 * asin(sqrt(sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2))
    if angular_dist12 == 0: raise Exception('Angular Distance is 0')

    initial_bearings = acos(( sin(lat2) - sin(lat1) * cos(angular_dist12)) / (sin(angular_dist12) * cos(lat1))) or 0
    final_bearings = acos((sin(lat1) - sin(lat2) * cos(angular_dist12)) / (sin(angular_dist12) * cos(lat2)))

    if sin(lon2 - lon1) > 0:
        bearing = initial_bearings
        back_bearing = 2 * pi - final_bearings
    else:
        bearing = 2 * pi - initial_bearings
        back_bearing = final_bearings

    angle1 = abs((brng1 - bearing + pi) % (2 * pi) - pi)
    angle2 = abs((back_bearing - brng2 + pi) % (2 * pi) - pi)

    if (sin(angle1) == 0) and (sin(angle2) == 0): raise Exception('Infinite intersections')

    angle3 = acos(-cos(angle1) * cos(angle2) + sin(angle1) * sin(angle2) * cos(angular_dist12))

    angular_dist13 = atan2(sin(angular_dist12) * sin(angle1) * sin(angle2), cos(angle2) + cos(angle1) * cos(angle3))

    lat3 = asin( sin(lat1) * cos(angular_dist13) + cos(lat1) * sin(angular_dist13) * cos(brng1))
    dlon13 = atan2(sin(brng1) * sin(angular_dist13) * cos(lat1), cos(angular_dist13) - sin(lat1) * sin(lat3))
    lon3 = lon1 + dlon13

    intersection = Coordinates(degrees(lat3), degrees(lon3))
    course1_relative_bearing = course1.bearing - calculate_bearing(course1.coordinates, intersection)

    if course1_relative_bearing > 300 or course1_relative_bearing < 60:
        return intersection
    else:
        return calculate_antipodes(intersection)


def calculate_distance(coordinates1, coordinates2):
    lat1 = radians(coordinates1.latitude)
    lon1 = radians(coordinates1.longitude)
    lat2 = radians(coordinates2.latitude)
    lon2 = radians(coordinates2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(EARTHS_RADIUS * c, 1)


def calculate_min_distance(course1, course2, timeframe, start_time=None):
    # I will rewrite this function once I work out the math
    if not start_time: start_time = datetime.now()
    minimum_distance = calculate_distance(course1.predicted_coordinates(start_time), course2.predicted_coordinates(start_time))

    for i in range(0, timeframe):
        timestamp = start_time + timedelta(seconds=i)
        distance = calculate_distance(course1.predicted_coordinates(timestamp), course2.predicted_coordinates(timestamp))
        minimum_distance = min(minimum_distance, distance)

    return minimum_distance


def arrival_time(coordinates1, coordinates2, speed, leave_time):
    distance_to_coords = calculate_distance(coordinates1, coordinates2)
    time_to_coords = distance_to_coords / speed
    return leave_time + timedelta(seconds=time_to_coords)


def calculate_min_distance_alt(course1, course2):
    intersection = calculate_intersection(course1, course2)

    course1_arrival = arrival_time(course1.coordinates, intersection, course1.speed, course1.timestamp)
    course2_arrival = arrival_time(course2.coordinates, intersection, course2.speed, course2.timestamp)

    course1_at_course1_arrival = course1.predicted_coordinates(course2_arrival)
    course2_at_course1_arrival = course2.predicted_coordinates(course1_arrival)

    return min(calculate_distance(course1_at_course1_arrival, intersection), calculate_distance(course2_at_course1_arrival, intersection))


course1 = Course(bearing=89, speed=2.5, coordinates=Coordinates(0, -0.005), timestamp=datetime(2017, 1, 1, 0, 0, 0))
course2 = Course(bearing=271, speed=2.6, coordinates=Coordinates(0, 0.005), timestamp=datetime(2017, 1, 1, 0, 0, 0))

starting_distance = calculate_distance(course1.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)), course2.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)))
min_distance_next_600_seconds = calculate_min_distance(course1, course2, 600, datetime(2017, 1, 1, 0, 0, 0))

print("Initial distance:", starting_distance)
print("Minimum distance next 10 minutes:", min_distance_next_600_seconds)


course1 = Course(bearing=90, speed=2.57, coordinates=Coordinates(0, 0), timestamp=datetime(2017, 1, 1, 0, 0, 0))
course2 = Course(bearing=270, speed=2.57, coordinates=Coordinates(10, 10), timestamp=datetime(2017, 1, 1, 0, 0, 0))

bearing = calculate_bearing(course1.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)), course2.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)))

print("Bearing: ", bearing)


course1 = Course(bearing=108.55, speed=2.57, coordinates=Coordinates(51.8853, 0.2545), timestamp=datetime(2017, 1, 1, 0, 0, 0))
course2 = Course(bearing=32.44, speed=2.57, coordinates=Coordinates(49.0034, 2.5735), timestamp=datetime(2017, 1, 1, 0, 0, 0))

intersection = calculate_intersection(course1, course2)

print("Intersection latitude: ", intersection.latitude)
print("Intersection longitude: ", intersection.longitude)


course1 = Course(bearing=225, speed=2.5, coordinates=Coordinates(0, 0.01), timestamp=datetime(2017, 1, 1, 0, 0, 0))
course2 = Course(bearing=135, speed=2.55, coordinates=Coordinates(0, -0.01), timestamp=datetime(2017, 1, 1, 0, 0, 0))

starting_distance = calculate_distance(course1.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)), course2.predicted_coordinates(datetime(2017, 1, 1, 0, 0, 0)))
print("Initial distance:", starting_distance)

min_distance_next_3600_seconds = calculate_min_distance(course1, course2, 3600, datetime(2017, 1, 1, 0, 0, 0))
print("Minimum distance next 60 minutes:", min_distance_next_3600_seconds)

min_distance = calculate_min_distance_alt(course1, course2)
print("Minimum distance alt calculation:", min_distance)
