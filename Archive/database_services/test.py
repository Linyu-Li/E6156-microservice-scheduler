from database_services.RDBService import RDBService


def t1():

    res = RDBService.get_by_prefix(
        "imdbfixed", "names_basic", "primary_name", "Tom H"
    )
    print("t1 resule = ", res)


def t2():

    res = RDBService.find_by_template(
        "schedule", "timeSlot", {"Id": "5"}, None
    )
    print("t2 resuls = ", res)


def t3():

    res = RDBService.create(
        "schedule", "timeSlot",
            {
                "Id": "6",
                "Year": "2020",
                "Month": "12",
                "Day": "11",
                "StartTime": "12:00",
                "EndTime": "15:00"
            })
    print("t3: res = ", res)

#t2()
t2()