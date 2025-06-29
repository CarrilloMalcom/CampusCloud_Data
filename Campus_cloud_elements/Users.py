from Campus_cloud_elements.Subject import Subject
class User:
    def __init__(self, name, id_num, password, semester, mail):
        self.__name__=name
        self.__id__=id_num
        self.__password__=password
        self.__semester__=semester
        self.__mail__=mail
        self.__classes__=[]
        
    def addClass(self, subject, credits):
        new_subject= Subject(input("Inserte nombre de la materia"), input("Inserte numero de creditos"))
        self.__classes__.append(new_subject)

    def calcAverage_PAPA(self):
        #Agregar despues
        pass

    def calcAverage_PAPI(self):
        #Agregar despues
        pass