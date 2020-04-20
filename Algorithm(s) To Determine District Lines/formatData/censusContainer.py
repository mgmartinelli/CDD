from exportData.exportData import save_data_to_file_with_description
from geographyHelper import polygonFromMultipleGeometries
from censusData import censusBlock


class CensusContainer:
    def __init__(self):
        self.children = []
        self.geometry = None
        self.population = None

    def updateBlockContainerData(self):
        self.geometry = polygonFromMultipleGeometries(self.children)
        self.population = censusBlock.populationFromBlocks(self.children)

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children):
        if len(children) != len(set(children)):
            save_data_to_file_with_description(data=self,
                                               census_year='',
                                               state_name='',
                                               description_of_info='ErrorCase-DuplicateChildren')
            raise RuntimeError("Children contains duplicates: {0}".format(self))

        self.__children = children
        self.updateBlockContainerData()