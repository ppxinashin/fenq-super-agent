"""
启动MinIO事件监听器
"""
import src.rag.minio.minio_event

if __name__ == "__main__":
    src.rag.minio.minio_event.start_event_listener()