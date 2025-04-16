class ProjectService:
    def __init__(self, db_service):
        self.db_service = db_service

    def get_project_structure(self, project_id: int) -> dict:
        return self.db_service.get_project_structure(project_id)
