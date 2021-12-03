from application_services.BaseApplicationResource import BaseApplicationResource
from database_services.RDBService import RDBService as RDBService

class TimeSlotResource(BaseApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_by_template(cls, template):
        res = RDBService.find_by_template("schedule", "timeSlot", template)
        return res

    @classmethod
    def create(cls, resource_data):
        id = RDBService.get_max_id("schedule", "timeSlot")
        resource_data["Id"] = id + 1
        res = RDBService.create("schedule", "timeSlot", resource_data)
        return res

    @classmethod
    def delete_by_template(cls, template):
        RDBService.delete_by_template("schedule", "timeSlot", template)

    @classmethod
    def update(cls, resource_data, where_id):
        RDBService.update_by_template("schedule", "timeSlot", resource_data, where_id)

    # TODO: Implementation
    @classmethod
    def get_links(cls, resource_data):
        pass