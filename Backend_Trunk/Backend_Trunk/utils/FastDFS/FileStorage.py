from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client

@deconstructible
class FastDFSStorage(Storage):
    def __init__(self, base_url=None, client_conf=None):
        self.base_url=base_url or settings.DFS_BASE_URL
        self.client_conf=client_conf or settings.DFS_CLIENT_CONF


    def _open(self):
        pass


    def _save(self, filename, content):
        """
        在dfs中保存文件
        :param filename:
        :param content:
        :return:
        """
        client=Fdfs_client(self.client_conf)
        result=client.upload_by_buffer(content.read())
        """
        client.upliad_by_buffer 接收参数是文件bytes字节数据，所以要read（）
        """
        if result.get('Status')!='Upload successed.':
            raise Exception("Upload file error when upload file %s" % filename)
        file_name=result.get("Remote file_id")
        if not file_name:
            raise Exception("Can not get remote file name when upload file %s" % filename)
        return file_name


    def url(self, name):
        """
        返回完整的远程文件的url完整路径
        :param name:
        :return:
        """
        print(self.base_url+name)
        return self.base_url+name


    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件重名的问题或文件已经存在的问题
        所以此处返回False，意味着没有重名，所有的文件都是新上传文件
        :param name:
        :return:
        """
        return False