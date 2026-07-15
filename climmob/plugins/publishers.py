from pyutilib.component.core import implements

from climmob.plugins import SingletonPlugin, IPublisher


class ClimMobPublisher(SingletonPlugin):
    implements(IPublisher)
    destination_name = "climmob"
    label = "ClimMob"
    disabled = True
    index = 0

    def get_destination_name(self):
        return self.destination_name

    def get_label(self):
        return self.label

    def publish(self, settings, request, path, project_id, crop_name):
        print(
            f"ClimmobPublisher: Publishing project {project_id} to {self.get_destination_name()}"
        )


class GenesysPublisher(SingletonPlugin):
    implements(IPublisher)
    destination_name = "genesys"
    label = "Genesys"
    disabled = False

    def get_destination_name(self):
        return self.destination_name

    def get_label(self):
        return self.label

    def publish(self, settings, request, path, project_id, crop_name):
        print(
            f"GenesysPublisher: Publishing project {project_id} to {self.get_destination_name()}"
        )
