import models.model as models

class PatentService:
    def __init__(self):
        pass
    
    def get_patent_by_id(self, id):
        return self.patent_model.find_by_id(id)

    def search_patents(self, query):
        return self.patent_model.search(query)