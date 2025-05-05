from repository.doccontrol import DocRepository
from repository.user import UserRepository

class DocService:
    def __init__(self):
        self.doc_repository = DocRepository()
        self.user_repository = UserRepository()

    async def get_docs_controls(self, params: dict) -> list[dict]:
        params = await self.user_repository.get_user_info_by_id(params['user_id'])
        params['executor_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['sedo_id']))
        params['boss1_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo']) if params['boss1_sedo'] is not None else None)
        params['boss2_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo']) if params['boss2_sedo'] is not None else None)
        params['boss3_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo']) if params['boss3_sedo'] is not None else None)

        controls = await self.doc_repository.get_doc_controls(params)
        return controls


    async def get_docs_wo_controls(self, params: dict) -> list[dict]:
        params = await self.user_repository.get_user_info_by_id(params['user_id'])
        params['executor_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['sedo_id']))
        params['boss1_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo']) if params['boss1_sedo'] is not None else None)
        params['boss2_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo']) if params['boss2_sedo'] is not None else None)
        params['boss3_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo']) if params['boss3_sedo'] is not None else None)

        controls = await self.doc_repository.get_doc_wo_controls(params)
        return controls


    async def get_boss_names(self, params :dict) -> dict:
        params = await self.user_repository.get_user_info_by_id(params['user_id'])
        print(params)
        result = {
            'boss1': await self.user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo']) if params['boss1_sedo'] is not None else None),
            'boss2': await self.user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo']) if params['boss2_sedo'] is not None else None),
            'boss3': await self.user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo']) if params['boss3_sedo'] is not None else None)
        }
        return result