class Course :
    """
        Class of a course containing day, time, "content", room,
        staff, group, week, duration, color parameters
    """
    def __init__(self,
                 par_day : str,
                 par_time : list[str],
                 par_module : str,
                 par_room : str,
                 par_prof : str,
                 par_group : str,
                 par_week : int,
                 par_note : str,
                 par_color : str) -> None:
        """
            Constructor of the class

            - Args :
                - parDay (str)
                - parTime (list[str])
                - parModule (str)
                - parRoom (str)
                - parProf (str)
                - parGroup (str)
                - parWeek (int)
                - parNote (str)
                - parColor (str)

            - Returns :
                - None
        """
        self.day_content = int(par_day)
        self.time_content = par_time
        self.module_content = par_module
        self.room_content = par_room
        self.prof_content = par_prof
        self.group_content = par_group
        self.week_content = par_week
        self.color_content = par_color
        self.note_content = par_note

        self.duration = self.d_time()
        self.start_minutes = self.to_minutes()
        self.end_minutes = self.start_minutes + self.duration

        self.same_time = []


    def __str__(self) -> str:
        """
            Display the course in a string
            
            - Args :
                - None

            - Returns :
                - display (str)
        """
        st = ''
        for e in self.same_time :
            st += ' ' + str(e)

        display = str(self.week_content)\
            + ' ' + str(self.day_content)\
            + ' [' + self.time_content[0]\
            + ':' + self.time_content[1]\
            + '] - [' + str(self.start_minutes)\
            + ':' + str(self.end_minutes)\
            + '] - ' + str(self.duration)\
            + ', ' + self.module_content\
            + ' ' + self.room_content\
            + ' ' + self.prof_content\
            + ' ' + self.group_content

        if len(self.same_time) != 0 :
            display += ', incompatible with :' + st

        return display


    def d_time(self) -> int :
        """
            Calculate the duration of the course
            
            - Args :
                - None

            - Returns :
                - dt (int)
        """
        d1 = (int((self.time_content[1].split(':'))[0]) - int((self.time_content[0].split(':'))[0]))
        d2 = ((int((self.time_content[1].split(':'))[1]) - int((self.time_content[0].split(':'))[1])))
        d1 *= 60
        dt = d1 + d2
        return dt


    def to_minutes(self) -> int:
        """
            Convert time content in minutes
            
            - Args :
                - None

            - Returns :
                - (int)
        """
        hr = (self.time_content[0]).split(':')
        return (int(hr[0])*60) + int(hr[-1])


    def is_compatible(self, hr2) -> bool:
        """
            Check if the parameter course overlap or is overlapped by the current course
            
            - Args :
                - hr2 (Course)
            
            - Returns :
                - (boolean)
        """
        if (self.week_content == hr2.week_content) and (self.day_content == hr2.day_content) :
            if ((self.start_minutes <= hr2.start_minutes < self.end_minutes) \
                or (self.start_minutes < hr2.end_minutes <= self.end_minutes)):
                return False

            if ((hr2.start_minutes <= self.start_minutes < hr2.end_minutes) \
                or (hr2.start_minutes < self.end_minutes <= hr2.end_minutes)):
                return False

            if (hr2.start_minutes == self.start_minutes) and (hr2.end_minutes == self.end_minutes):
                return False

        return True


    def start_before(self, course2) -> bool :
        """
            Check if the current course start before the parameter course

            - Args :
                - course2 (Course)
            
            - Returns :
                - (boolean)
        """
        if self.day_content < course2.day_content :
            return True

        if (course2.day_content == self.day_content) \
            and (self.start_minutes < course2.start_minutes) :
            return True

        return False


    def __eq__(self, course2) -> bool :
        """
            Check if the current course is equal to the parameter course

            - Args :
                - course2 (Course)

            - Returns :
                - (boolean)
        """
        if self.group_content == course2.group_content :
            if self.module_content == course2.module_content :
                if self.week_content == course2.week_content :
                    if self.prof_content == course2.prof_content :
                        if self.day_content == course2.day_content :
                            if self.time_content == course2.time_content :
                                if self.room_content == course2.room_content :
                                    return True
        return False


    def merge(self, course2) -> None :
        """
            Merge the current course with the parameter course

            - Args :
                - course2 (Course)

            - Returns :
                - None
        """
        if course2.prof_content not in self.prof_content :
            self.prof_content += ', ' + course2.prof_content
        if course2.room_content not in self.room_content :
            self.room_content += ', ' + course2.room_content
        if course2.group_content not in self.group_content :
            self.group_content += ', ' + course2.group_content
        if course2.note_content not in self.note_content and course2.note_content != '- - -' :
            self.note_content += ' -- ' + course2.note_content
