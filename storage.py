import os
import shutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileStorage:
    def __init__(self, base_dir='uploads'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def _generate_path(self, file_name):
        """生成文件存储路径，按年月组织目录结构"""
        now = datetime.now()
        year_dir = os.path.join(self.base_dir, str(now.year))
        month_dir = os.path.join(year_dir, f"{now.month:02d}")
        os.makedirs(month_dir, exist_ok=True)
        
        # 生成唯一文件名
        base_name, ext = os.path.splitext(file_name)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        new_name = f"{base_name}_{timestamp}{ext}"
        return os.path.join(month_dir, new_name)
    
    def save_file(self, source_path, file_name=None):
        """
        保存文件到存储系统
        :param source_path: 源文件路径
        :param file_name: 可选，指定文件名
        :return: 存储后的文件路径
        """
        try:
            if file_name is None:
                file_name = os.path.basename(source_path)
                
            target_path = self._generate_path(file_name)
            
            # 使用缓冲区复制大文件
            with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst, length=1024*1024)  # 1MB buffer
                
            logger.info(f"File saved successfully: {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def delete_file(self, file_path):
        """
        从存储系统中删除文件
        :param file_path: 文件路径
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted successfully: {file_path}")
                
                # 尝试删除空目录
                dir_path = os.path.dirname(file_path)
                while dir_path != self.base_dir:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        dir_path = os.path.dirname(dir_path)
                    else:
                        break
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise
