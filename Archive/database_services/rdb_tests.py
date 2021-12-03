from database_services.RDBService import RDBService as RDBService


def t1():

    res = RDBService.get_by_prefix(
        "imdbfixed", "names_basic", "primary_name", "Tom H"
    )
    print("t1 resule = ", res)


def t2():

    res = RDBService.find_by_template(
        "imdbfixed", "name_basics", {"primaryName": "Tom Hanks"}, None
    )
    print("t2 resuls = ", res)

def t3():

    res = RDBService.update_by_template(
        "schedule", "availability", {"timeId": "5"}, {"Id": "1"}
    )

    print("t3 result = ", res)

def t4():

    RDBService.delete_by_template(
        "schedule", "availability", {"Id": "1"}
    )

def t5():

    res = RDBService.find_by_template(
        "schedule", "availability", {"Id": "1"}
    )

    print(res)

t5()


