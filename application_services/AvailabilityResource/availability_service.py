from application_services.BaseApplicationResource import BaseApplicationResource
from database_services.RDBService import RDBService as RDBService

class AvailabilityResource(BaseApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_by_template(cls, template, limit=None, offset=None):
        res = RDBService.find_by_template("schedule", "availability", template, limit, offset)
        res_with_links = AvailabilityResource.get_links(res)
        return res_with_links

    @classmethod
    def create(cls, resource_data):
        id = RDBService.get_max_id("schedule", "availability")
        resource_data["Id"] = str(int(id) + 1)
        res = RDBService.create("schedule", "availability", resource_data)
        return res

    @classmethod
    def update(cls, resource_data, where_id):
        RDBService.update_by_template("schedule", "availability", resource_data, where_id)

    @classmethod
    def delete_by_template(cls, template):
        RDBService.delete_by_template("schedule", "availability", template)

    # TODO: Implementation
    @classmethod
    def get_links(cls, resource_data):
        for r in resource_data:
            time_id = r.get("timeId")

            links = []

            time_slot_link = {"rel": "timeSlot", "href": "api/timeSlot/" + str(time_id)}

            links.append(time_slot_link)

            r["links"] = links

        return resource_data