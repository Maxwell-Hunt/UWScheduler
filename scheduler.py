import pygame
import json
from copy import deepcopy

class Schedule:
    day_mapper = {'M': 0, 'T': 1, 'W': 2, 'Th': 3, 'F': 4}
    def __init__(self):
        self.info = self.load_info()
        self.class_dict = self.get_courses()
        self.schedules = self.generate_schedules()
        self.sort_schedules()

    def load_info(self):
        info = None
        with open("info.json", "r") as f:
            info = json.load(f)
        return info

    def get_courses(self):
        input_message = "Please enter your courses space separated:\n"
        courses = input(input_message).upper().split()
        class_dict = {}
        for course in courses:
            if not course in self.info:
                print("Sorry, one of your courses is not here")
                exit()
            for course_type in self.info[course]:
                class_dict[course + " " + course_type] = self.info[course][course_type]
        return class_dict
            
    def intersects(self, session, schedule):
            for day in session['days']:
                day_index = Schedule.day_mapper[day]
                for items in schedule[day_index]:
                    if (
                        (session['time'][0] <= items['time'][0] and items['time'][0] <= session['time'][1]) or
                        (session['time'][0] <= items['time'][1] and items['time'][1] <= session['time'][1])
                    ):
                        return True
            return False
    
    def generate_schedules(self, schedule=None, class_index=0):
        if class_index >= len(self.class_dict):
            return [schedule]
        
        if schedule == None:
            schedule = [[], [], [], [], []]
        
        schedules = []
        course_type = list(self.class_dict.keys())[class_index]
        for course_session in self.class_dict[course_type]:
            if not self.intersects(course_session, schedule):
                new_schedule = deepcopy(schedule)
                for day in course_session['days']:
                    new_schedule[Schedule.day_mapper[day]].append({'course': course_type, 'time': course_session['time']})
                result = self.generate_schedules(schedule=new_schedule, class_index=class_index + 1)
                schedules.extend(result)
        return schedules

    def sort_schedules(self):
        def get_earliest_start_time(schedule):
            result = 10000000000
            for day in schedule:
                for course in day:
                    result = min(result, course['time'][0])
            return result
        
        self.schedules = sorted(self.schedules, key=get_earliest_start_time, reverse=True)
    
    def get_schedules(self):
        return self.schedules
    
    def print_len(self):
        print("LENGTH: ", len(self.schedules))
    
    def print_first(self):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        if len(self.schedules) == 0:
            print("Sorry, no way to make this schedule: ")
            exit()
        for day, time_table in zip(weekdays, self.schedules[0]):
            print(day)
            print(time_table)


class Calendar:
    WIDTH = 1000
    TOTAL_WIDTH = WIDTH * 1.2
    HEIGHT = 700
    # The calendar goes from 7am to 8pm thereby having in total 780 minutes
    TOTAL_MINUTES = 780
    TITLE_HEIGHT = 30
    TITLE_GAP = 40
    COLORS = ['red', 'orange', 'pink', 'purple', 'grey', 'green', 'blue', 'yellow']
    
    def __init__(self, schedules):
        pygame.init()
        pygame.font.init()
        self.font_big=pygame.font.SysFont('timesnewroman',  20)
        self.font_small=pygame.font.SysFont('timesnewroman', 15)
        self.screen = pygame.display.set_mode((Calendar.TOTAL_WIDTH, Calendar.HEIGHT))
        self.schedules = schedules
        self.schedule_index = 0
        self.right_pressed = False
        self.left_pressed = False
        self.color_map = self.get_color_map()

    def display_dates(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for i in range(5):
            text = self.font_big.render(days[i], True, 'black', 'white')
            text_rect = text.get_rect()
            width_diff = Calendar.TOTAL_WIDTH - Calendar.WIDTH
            text_rect.center = (Calendar.WIDTH / 5 * i + Calendar.WIDTH / 10 + width_diff / 2, Calendar.TITLE_HEIGHT)
            self.screen.blit(text, text_rect)

    @staticmethod
    def mins_to_pixels(mins):
        return mins / Calendar.TOTAL_MINUTES * (Calendar.HEIGHT - Calendar.TITLE_HEIGHT)
    
    def draw_lines(self):
        for i in range(13):
            time_text = str(7 + i if 7 + i <= 12 else (7 + i) % 12) + ":00"
            text = self.font_small.render(time_text, True, 'black', 'white')
            text_rect = text.get_rect()
            
            
            height = Calendar.mins_to_pixels(i * 60) + Calendar.TITLE_HEIGHT + Calendar.TITLE_GAP
            pygame.draw.line(self.screen, 'black', (0, height), (Calendar.TOTAL_WIDTH, height))
            text_rect.center = (50, height)
            self.screen.blit(text, text_rect)

    def get_color_map(self):
        color_index = 0
        color_map = {}
        for day in self.schedules[0]:
            for course in day:
                course_name = course['course'].split()[0]
                if not course_name in color_map:
                    color_map[course_name] = Calendar.COLORS[color_index]
                    color_index += 1
                    color_index %= len(Calendar.COLORS)
        return color_map

    def display_schedule(self):
        for i, day in enumerate(self.schedules[self.schedule_index]):
            for course in day:
                top = Calendar.mins_to_pixels(course['time'][0] - 7 * 60) + Calendar.TITLE_HEIGHT + Calendar.TITLE_GAP
                bottom = Calendar.mins_to_pixels(course['time'][1] - 7 * 60) + Calendar.TITLE_HEIGHT + Calendar.TITLE_GAP
                width = Calendar.WIDTH / 5 * 0.8
                width_diff = Calendar.TOTAL_WIDTH - Calendar.WIDTH
                left = Calendar.WIDTH / 5 * i + (Calendar.WIDTH / 5 - width) / 2 + width_diff / 2
                
                height = bottom - top
                course_name = course['course'].split()[0]
                pygame.draw.rect(self.screen, self.color_map[course_name], pygame.Rect(left, top, width, height))
                text = self.font_small.render(course['course'], True, 'black', self.color_map[course_name])
                text_rect = text.get_rect()
                text_rect.center = (left + width / 2, top + height / 2)
                self.screen.blit(text, text_rect)

    def draw(self):
        self.screen.fill("white")
        self.draw_lines()
        self.display_dates()
        self.display_schedule()

    def go_right(self, keys):
        for key in keys:
            if pygame.key.get_pressed()[key]:
                self.right_pressed = True
            else:
                if self.right_pressed:
                    self.schedule_index += 1
                    self.schedule_index %= len(self.schedules)
                    self.draw()
                self.right_pressed = False

    def go_left(self, keys):
        for key in keys:
            if pygame.key.get_pressed()[key]:
                self.left_pressed = True
            else:
                if self.left_pressed:
                    self.schedule_index -= 1
                    self.schedule_index %= len(self.schedules)
                    self.draw()
                self.left_pressed = False

    def update(self):
        self.go_right([pygame.K_SPACE, pygame.K_RIGHT])
        self.go_left([pygame.K_LEFT])

    def show(self):
        running = True
        self.draw()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.update()
            pygame.display.update()

    def close(self):
        pygame.quit()

if __name__ == '__main__':
    schedule = Schedule()
    schedule.print_len()
    if len(schedule.schedules) == 0:
        print("Sorry this schedule is not possible")
        exit()
    calendar = Calendar(schedule.get_schedules())
    calendar.show()
    calendar.close()