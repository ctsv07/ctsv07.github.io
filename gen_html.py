import glob

from datetime import datetime

SERIES = ['NCAR', 'INDY', 'NHRA']

OWNERS = ['Scooter', 'Mark', 'Evan', 'Jake']

TABLE_ROW="<tr>{}</tr>\n"
BORDER_NORMAL=""
BORDER_STRONG="strong"
TABLE_CELL='<td class="{}">{}</td>'

class Driver:
    def __init__(self, owner, name, number, series):
        self.name = name
        self.number = number
        self.owner = owner
        self.series = series
        self.points = 0
        self.starts = 0

        self.race_points = list()
        self.all_points = 0
        self.cumm_race_place = 0
        self.num_races = 0

    def add_race_results(self, place, points):
        self.points += int(points)
        self.starts += 1

    def calc_race_stats(self, places, points_schedule, series):
        for place in places:
            race_points = int(calc_points(place, points_schedule[series]))
            self.all_points += race_points
            self.race_points.append(race_points)
            self.cumm_race_place += int(place)
            self.num_races += 1
 
class Race:
    def __init__(self, date, series, track, location, race_type):
        self.date = date
        self.date_obj = datetime.strptime(date, '%m/%d/%Y').date()
        self.series = series
        self.track = track
        self.race_type = race_type
        self.location = location
        self.drivers = dict()

    def add_driver(self, name, place):
        self.drivers[name] = place

def load_html_template(temp_dir, file_name):
    template_file = open('templates/' + temp_dir + '/' + file_name, 'r')

    html = template_file.read()

    template_file.close()

    return html

def remove_dir(file_name):
    return file_name.split('/')[1]

def get_series_from_file_name(file_name):
    if '/' in file_name:
        file_name = remove_dir(file_name)

    return file_name.split('_')[0]

def load_drivers(points_schedules):
    drivers = list()

    drivers_files = glob.glob("drivers/*.txt")

    for driver_file_name in drivers_files:
        series = get_series_from_file_name(driver_file_name)
   
        driver_file = open(driver_file_name, "r") 

        for driver_line in driver_file:
            driver_line = driver_line.strip('\n')
            driver_parts = driver_line.split('|')
            driver = Driver(driver_parts[0], driver_parts[1], driver_parts[2], series) 

            driver.calc_race_stats(driver_parts[3:], points_schedules, series)

            drivers.append(driver)

    return drivers

def load_races():
    series = list()
    races = list()

    schedule_files = glob.glob("schedules/*.txt")

    for schedule_file_name in schedule_files:
        series.append(get_series_from_file_name(schedule_file_name))
   
        schedule_file = open(schedule_file_name, "r") 

        for race_line in schedule_file:
            race_line = race_line.strip('\n')
            race_parts = race_line.split('|')

            race = Race(race_parts[0], race_parts[1], race_parts[2], race_parts[3], race_parts[4])
            if race_parts[5] != "":
                race.add_driver(race_parts[5], race_parts[6])
                race.add_driver(race_parts[7], race_parts[8])
                race.add_driver(race_parts[9], race_parts[10])
                #import pdb;pdb.set_trace()
                race.add_driver(race_parts[11], race_parts[12])

            races.append(race)

    races = sorted(races, key=lambda x: x.date_obj)

    return series, races

def load_series_points(points_file_name):
    points = dict()

    points_file = open(points_file_name, "r")

    for points_line in points_file:
        points_line = points_line.strip('\n')
        points_parts = points_line.split('|')
        points[points_parts[0]] = points_parts[1]

    return points

def load_points_schedule():
    points_files = glob.glob("points/*.txt")

    points_schedules = dict()

    for points_file_name in points_files:
        series = get_series_from_file_name(points_file_name)
   
        points_schedules[series] = load_series_points(points_file_name)

    return points_schedules

def calc_points(place, points_schedule):
    if place not in points_schedule:
        return 0

    return points_schedule[place]

def calc_cumm_points(owner, drivers):
    cumm_points = 0
    for driver in drivers:
        if driver.owner == owner:
            cumm_points += driver.points

    return cumm_points

def calc_sum_points(owner, series, drivers):
    sum_points = 0
    for driver in drivers:
        if driver.owner == owner and driver.series == series:
            sum_points += driver.points

    return sum_points

def get_series_drivers(drivers, series):
    series_drivers = list()

    for driver in drivers:
        if driver.series == series:
            series_drivers.append(driver)

    return series_drivers

def get_series_owner_drivers(drivers, series, owner):
    series_drivers = list()

    for driver in drivers:
        if driver.series == series and driver.owner == owner:
            series_drivers.append(driver)

    return series_drivers

def get_driver(drivers, series, name):
    for driver in drivers:
        if driver.series == series and driver.name == name:
            return driver

def gen_drivers(drivers):
    drivers_html = ''
    owners_html = ''
    owner_row_html = load_html_template('drivers', 'owner_row_template.html')
    drivers_template_html = load_html_template('drivers', 'drivers_template.html')

    for owner in OWNERS:
        owners_html += owner_row_html.replace('%OWNER%', owner)

    for series in SERIES:
        series_row = ''
        series_row += TABLE_CELL.format(BORDER_STRONG, series)
        for owner in OWNERS:
            owner_drivers = get_series_owner_drivers(drivers, series, owner)

            for index, driver in enumerate(owner_drivers):
                # If last item in list, add strong border line
                if index == len(owner_drivers) - 1:
                    series_row += TABLE_CELL.format(BORDER_STRONG, driver.name)
                else:
                    series_row += TABLE_CELL.format(BORDER_NORMAL, driver.name)

        series_row = TABLE_ROW.format(series_row)
        drivers_html += series_row

    drivers_template_html = drivers_template_html.replace('%OWNERS%', owners_html)    
    drivers_template_html = drivers_template_html.replace('%DRIVERS%', drivers_html)    

    return drivers_template_html


def gen_driver_result_cells(race, points_schedule):
    driver_results_html = ''
    driver_result_html = load_html_template('races', 'driver_result_row_template.html')

    for driver_name in race.drivers:
        driver = get_driver(drivers, race.series, driver_name)
        place = race.drivers[driver_name]
        points = calc_points(place, points_schedule[race.series])
        driver.add_race_results(place, points)

        cumm_points = calc_cumm_points(driver.owner, drivers)

        temp_html = driver_result_html
        temp_html = temp_html.replace('%DRIVER_NAME%', driver_name)
        temp_html = temp_html.replace('%DRIVER_PLACE%', place)
        temp_html = temp_html.replace('%DRIVER_POINTS%', str(points))
        temp_html = temp_html.replace('%OWNER_CUMM_POINTS%', str(cumm_points))

        driver_results_html += temp_html

    return driver_results_html

def gen_race_row(race, points_schedule):
    race_html = load_html_template('races', 'race_row_template.html')

    race_html = race_html.replace('%RACE_DATE%', race.date) 
    race_html = race_html.replace('%RACE_SERIES%', race.series) 
    race_html = race_html.replace('%RACE_TRACK%', race.track) 
    race_html = race_html.replace('%RACE_LOCATION%', race.location) 
    race_html = race_html.replace('%RACE_TYPE%', race.race_type) 

    driver_results_html = gen_driver_result_cells(race, points_schedule)

    race_html = race_html.replace('%DRIVER_RESULTS%', driver_results_html) 

    return race_html

def gen_races(series, races, points_schedule, drivers):
    races_html = ''

    for race in races:
        races_html += gen_race_row(race, points_schedule)

    return races_html

def gen_summary_header():
    summary_header = load_html_template('summary', 'summary_header_template.html')
    summary_row = ''
    summary_html = ''

    for series in SERIES:
        summary_row = summary_header.replace('%SERIES%', series)
        summary_html += summary_row

    return summary_html
        
def gen_summary(drivers):
    summary_html = load_html_template('summary', 'summary_template.html')
    summary_data = ''

    owner_points = dict()
    owner_rows = dict()

    summary_html = summary_html.replace('%SUMMARY_HEADER%', gen_summary_header())

    for owner in OWNERS:
        total_owner_points = 0
        summary_row = TABLE_CELL.format(BORDER_STRONG, owner)
        for series in SERIES:
            owner_drivers = get_series_owner_drivers(drivers, series, owner)
            sum_points = calc_sum_points(owner, series, owner_drivers)
            total_owner_points += sum_points 
            summary_row += TABLE_CELL.format(BORDER_NORMAL, sum_points)
        summary_row += TABLE_CELL.format(BORDER_STRONG, total_owner_points)
        summary_row = TABLE_ROW.format(summary_row)

        # Keep two separate dictionaries: one with the owner total points and
        # another with the HTML row. Sort by total points and add HTML by point
        # total.
        owner_points[owner] = total_owner_points
        owner_rows[owner] = summary_row

    # Sort from highest point total to lowest
    owner_points = dict(sorted(owner_points.items(), key=lambda item: item[1], reverse=True))

    for owner in owner_points:
        summary_data += owner_rows[owner]

    summary_html = summary_html.replace('%SUMMARY_DATA%', summary_data)

    return summary_html

def gen_driver_points_chart_render(driver):
    render_chart_template = load_html_template('series', 'render_chart_template.html')
    return render_chart_template.replace('%DRIVER%', 'D' + driver.number);

def gen_driver_points_array(driver):
    chart_data_template = load_html_template('series', 'chart_data_template.html')
    chart_data_template = chart_data_template.replace('%DRIVER%', 'D' + driver.number)
    driver_points_array = ''
    max_points = 0

    for points in driver.race_points:
        driver_points_array += '{value: ' + str(points) + '},'
        if points > max_points:
            max_points = points

    # remove last comma
    driver_points_array = driver_points_array[:-1]
        
    chart_data_template = chart_data_template.replace('%POINTS_HISTORY_DATA%', driver_points_array)

    return chart_data_template, max_points

def gen_series_driver_row(driver_row, driver):
    avg_points_per_start = 0.0
    points_per_race = 0
    avg_finish = 0

    # Avoid divide by zero if there are races started by driver.
    if driver.starts > 0:
        avg_points_per_start = driver.points/driver.starts

    # Avoid divide by zero if there are no races completed yet.
    if driver.num_races > 0:
        points_per_race = driver.all_points/driver.num_races
        avg_finish = driver.cumm_race_place/driver.num_races

    driver_row = driver_row.replace('%OWNER%', driver.owner)
    driver_row = driver_row.replace('%DRIVER%', driver.name)
    driver_row = driver_row.replace('%DRIVER_NUMBER%', driver.number)
    driver_row = driver_row.replace('%START_POINTS%', str(driver.points))
    driver_row = driver_row.replace('%STARTS%', str(driver.starts))
    driver_row = driver_row.replace('%POINTS_PER_START%', "{:.0f}".format(avg_points_per_start))

    driver_row = driver_row.replace('%ALL_POINTS%', str(driver.all_points))
    driver_row = driver_row.replace('%NUM_RACES%', str(driver.num_races))
    driver_row = driver_row.replace('%POINTS_PER_RACE%', "{:.0f}".format(points_per_race))
    driver_row = driver_row.replace('%AVG_FINISH%', "{:.0f}".format(avg_finish))

    return driver_row

def gen_series(drivers):
    series_template = load_html_template('series', 'series_template.html')
    driver_row_template = load_html_template('series', 'series_driver_template.html')

    for series in SERIES:
        drivers_html = ''
        drivers_points_array = ''
        drivers_points_render_chart = ''
        max_points = 0
        series_html = series_template

        series_html = series_html.replace('%SERIES%', series)
        series_drivers = get_series_drivers(drivers, series)
        series_drivers = sorted(series_drivers, key=lambda x: (-x.points, -x.starts))
        for driver in series_drivers:
            driver_row = driver_row_template

            driver_row = gen_series_driver_row(driver_row, driver)
            drivers_points_render_chart += gen_driver_points_chart_render(driver)
            temp_array, max_driver_points = gen_driver_points_array(driver)

            drivers_points_array += temp_array

            if max_driver_points > max_points:
                max_points = max_driver_points

            drivers_html += driver_row
        
        series_html = series_html.replace('%DRIVER_SERIES_DATA%', drivers_html)
        series_html = series_html.replace('%DRIVER_POINTS_RENDER%', drivers_points_render_chart)
        series_html = series_html.replace('%DRIVER_POINTS_HISTORY_DATA%', drivers_points_array)
        series_html = series_html.replace('%MAX_POINTS%', str(max_points))

        series_html_file = open(series + "_drivers.html", "w")
        series_html_file.write(series_html)
        series_html_file.close()

# Load data elements
series, races = load_races()
points_schedules = load_points_schedule()
drivers = load_drivers(points_schedules)

# Generate index sections
races_html = gen_races(series, races, points_schedules, drivers)
summary_html = gen_summary(drivers)
drivers_html = gen_drivers(drivers)

# Update index template
index_template = load_html_template('index', 'index_template.html')
index_template = index_template.replace('%DRIVERS_TABLE%', drivers_html)
index_template = index_template.replace('%SUMMARY_TABLE%', summary_html)
index_template = index_template.replace('%RACES_TABLE%', races_html)

index_file = open("index.html", "w")
index_file.write(index_template)
index_file.close()

# Generate series pages
gen_series(drivers)
