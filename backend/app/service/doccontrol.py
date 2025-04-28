from repository.doccontrol import DocRepository
from repository.user import UserRepository

class DocService:
    def __init__(self):
        self.doc_repository = DocRepository()

    async def get_docs_controls(self, params: dict) -> list[dict]:
        user_repository = UserRepository()
        params['executor_name'] = await user_repository.get_user_fio_by_sedo_id(int(params['executor_sedo_id']))
        params['boss1_name'] = await user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo_id']))
        params['boss2_name'] = await user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo_id']))
        params['boss3_name'] = await user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo_id']))



        controls = await self.doc_repository.get_doc_controls(params)
        return controls