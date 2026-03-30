SERIES = ['NCAR', 'INDY', 'NHRA']

OWNERS = ['Scooter', 'Mark', 'Evan', 'Jake']

F_DRIVER = "{:>15}"
F_DRIVER_RACE = "    " + F_DRIVER + " | {:>2} | {:>2} | {:>3}"
F_RACE = "\n{:>10} ({:>4}) {:<50}"
F_OWNER = "{:>7}"
F_POINTS = "{:>5}"
F_POINTS_AVERAGE = "{:>5.0f}"
F_SERIES = F_OWNER + F_DRIVER + F_POINTS + F_POINTS + F_POINTS_AVERAGE
F_SERIES_HEAD = F_OWNER + F_DRIVER + F_POINTS + F_POINTS + F_POINTS

class Driver:
    def __init__(self, name, owner, series):
        self.name = name
        self.owner = owner
        self.series = series
        self.points = 0
        self.cumm_place = 0
        self.starts = 0

    def add_race_results(self, place, points):
        self.points += int(points)
        self.cumm_place += int(place)
        self.starts += 1

class Race:
    def __init__(self, date, series, track, race_type):
        self.date = date
        self.series = series
        self.track = track
        self.race_type = race_type
        self.drivers = dict()

    def add_driver(self, name, place):
        self.drivers[name] = place

def load_drivers():
    driver_file = open("drivers.txt", "r")

    drivers = dict()

    for driver_line in driver_file:
       driver_line = driver_line.strip('\n')
       driver_parts = driver_line.split('|')
       driver = Driver(driver_parts[2], driver_parts[1], driver_parts[0]) 

       drivers[driver.name] = driver

    return drivers

def load_races():
    races_file = open("schedule.txt", "r")

    races = list()

    for race_line in races_file:
       race_line = race_line.strip('\n')
       race_parts = race_line.split('|')

       race = Race(race_parts[0], race_parts[1], race_parts[2], race_parts[4])
       if race_parts[5] != "":
           race.add_driver(race_parts[5], race_parts[6])
           race.add_driver(race_parts[7], race_parts[8])
           race.add_driver(race_parts[9], race_parts[10])
           #import pdb;pdb.set_trace()
           race.add_driver(race_parts[11], race_parts[12])

       races.append(race)

    return races

def load_series_points(series):
    points = dict()

    points_file = open(series + "_points.txt", "r")

    for points_line in points_file:
        points_line = points_line.strip('\n')
        points_parts = points_line.split('|')
        points[points_parts[0]] = points_parts[1]

    return points

def load_points():
    points = dict()

    for series in SERIES:
        points[series] = load_series_points(series)

    return points

def calc_points(place, point_schedule):
    if place not in point_schedule:
        return 0

    return point_schedule[place]

def calc_cumm_points(owner, drivers):
    cumm_points = 0
    for driver_name in drivers:
        if drivers[driver_name].owner == owner:
            cumm_points += drivers[driver_name].points

    return cumm_points

def calc_sum_points(owner, series, drivers):
    sum_points = 0
    for driver_name in drivers:
        driver = drivers[driver_name]
        if driver.owner == owner and driver.series == series:
            sum_points += drivers[driver_name].points

    return sum_points

def get_series_drivers(drivers, series):
    series_drivers = list()

    for driver_name in drivers:
        if drivers[driver_name].series == series:
            series_drivers.append(drivers[driver_name])

    return series_drivers

def print_schedule(races, point_schedule, drivers):
    for race in races:
        if len(race.drivers) == 0:
            continue

        print(F_RACE.format(race.date, race.series, race.track))
        for driver_name in race.drivers:
            #import pdb;pdb.set_trace()
            driver = drivers[driver_name]
            place = race.drivers[driver_name]
            points = calc_points(place, point_schedule[race.series])
            driver.add_race_results(place, points)

            cumm_points = calc_cumm_points(driver.owner, drivers)

            print(F_DRIVER_RACE.format(driver_name, place, points, cumm_points))
        
def print_summary(drivers):
    print(F_OWNER.format(""), end="")
    for series in SERIES:
        print(F_POINTS.format(series), end="")
    print(F_POINTS.format("TOT"))

    for owner in OWNERS:
        total_owner_points = 0
        print(F_OWNER.format(owner), end="")
        for series in SERIES:
            sum_points = calc_sum_points(owner, series, drivers)
            total_owner_points += sum_points 
            print(F_POINTS.format(sum_points), end="")
        print(F_POINTS.format(total_owner_points))


def print_series(drivers):
    for series in SERIES:
        print("")
        print(series)
        print(F_SERIES_HEAD.format("Owner", "Driver", "Pts", "Sts", "P/S"))
        series_drivers = get_series_drivers(drivers, series)
        series_drivers = sorted(series_drivers, key=lambda x: x.points, reverse=True)
        for driver in series_drivers:
            avg_points_per_start = 0.0
            if driver.starts > 0:
                avg_points_per_start = driver.points/driver.starts
            print(F_SERIES.format(driver.owner, driver.name, driver.points, driver.starts, avg_points_per_start))

drivers = load_drivers()
races = load_races()
points = load_points()

print_schedule(races, points, drivers)

print("")
print_summary(drivers)

print_series(drivers)
