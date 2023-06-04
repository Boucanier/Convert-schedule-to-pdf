class Course :
    """
        Class of a course containing day, time, "content", room, staff, group, week, duration, color parameters
    """
    def __init__(self, parDay : str, parTime : list[str], parModule : str, parRoom : str, parProf : str, parGroup : str, parWeek : int, parNote : str, parColor : str) -> None:
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
        """
        self.dayContent = int(parDay)
        self.timeContent = parTime
        self.moduleContent = parModule
        self.roomContent = parRoom
        self.profContent = parProf
        self.groupContent = parGroup
        self.weekContent = parWeek
        self.colorContent = parColor
        self.noteContent = parNote

        self.duration = self.dTime()
        self.startMinutes = self.toMinutes()
        self.endMinutes = self.startMinutes + self.duration

        self.sameTime = []

    def __str__(self) -> str:
        """
            Display the course in a string

            - Returns :
                - display (str)
        """
        st = ''
        for e in self.sameTime :
            st += ' ' + str(e)
        display = str(self.weekContent) + ' ' + str(self.dayContent) + ' [' + self.timeContent[0] + ':' + self.timeContent[1] + '] - [' + str(self.startMinutes) + ':' + str(self.endMinutes) + '] - ' + str(self.duration) + ', ' \
            + self.moduleContent + ' ' + self.roomContent + ' ' + self.profContent + ' ' + self.groupContent
        if len(self.sameTime) != 0 :
            display += ', incompatible with :' + st
        return display

    def dTime(self) -> int :
        """
            Calculate the duration of the course
            
            - Returns :
                - dt (int)
        """
        d1 = (int((self.timeContent[1].split(':'))[0]) - int((self.timeContent[0].split(':'))[0]))
        d2 = ((int((self.timeContent[1].split(':'))[1]) - int((self.timeContent[0].split(':'))[1])))
        d1 *= 60
        dt = d1 + d2
        return dt

    def toMinutes(self) -> int:
        """
            Convert time content in minutes
            
            - Returns :
                - (int)
        """
        hr = (self.timeContent[0]).split(':')
        return (int(hr[0])*60) + int(hr[-1])
    
    def isCompatible(self, hr2) -> bool:
        """
            Check if the parameter course overlap or is overlapped by the current course
            
            - Args :
                - hr2 (Course)
            
            - Returns :
                - (boolean)
        """
        if (self.weekContent == hr2.weekContent) and (self.dayContent == hr2.dayContent) :
            if ((self.startMinutes <= hr2.startMinutes < self.endMinutes) or (self.startMinutes < hr2.endMinutes <= self.endMinutes)):
                return False
            if ((hr2.startMinutes <= self.startMinutes < hr2.endMinutes) or (hr2.startMinutes < self.endMinutes <= hr2.endMinutes)):
                return False
            if (hr2.startMinutes == self.startMinutes) and (hr2.endMinutes == self.endMinutes):
                return False
        return True
    
    def startBefore(self, course2) -> bool :
        """
            Check if the current course start before the parameter course

            - Args :
                - course2 (Course)
            
            - Returns :
                - (boolean)
        """
        if self.dayContent < course2.dayContent :
            return True
        elif (course2.dayContent == self.dayContent) and (self.startMinutes < course2.startMinutes) :
            return True
        return False

    def __eq__(self, course2) :
        """
            Check if the current course is equal to the parameter course

            - Args :
                - course2 (Course)

            - Returns :
                - (boolean)
        """
        if self.groupContent == course2.groupContent :
            if self.moduleContent == course2.moduleContent :
                if self.weekContent == course2.weekContent :
                    if self.profContent == course2.profContent :
                        if self.dayContent == course2.dayContent :
                            if self.timeContent == course2.timeContent :
                                if self.roomContent == course2.roomContent :
                                    return True
        return False