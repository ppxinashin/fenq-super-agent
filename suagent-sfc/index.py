import subprocess


def main_handler(event, context):
    """
使用系统自带的curl命令进行HTTP请求测试

当`eventName=cos:ObjectCreated:Put`时，从event里合成链接，并进行回调测试，如果为200，就返回给用户，否则报错

```json
{
  "Records": [
    {
      "event": {
        "eventName": "cos:ObjectCreated:Put",
        "eventTime": "2025-11-04T10:30:00Z"
      },
      "cos": {
        "cosBucket": {
          "name": "your-bucket-name"
        },
        "cosObject": {
          "key": "documents/example.pdf",
          "size": 1024000,
          "meta": {
            "Content-Type": "application/pdf"
          }
        }
      }
    }
  ]
}
```
    """
    try:
        # 解析事件数据
        if 'Records' not in event or len(event['Records']) == 0:
            raise ValueError("事件数据格式错误：缺少 Records 字段")
        
        record = event['Records'][0]
        
        # 检查事件类型
        event_name = record.get('event', {}).get('eventName', '')
        if event_name != 'cos:ObjectCreated:Put':
            return {
                'statusCode': 200,
                'body': {
                    'message': f'忽略非 Put 事件: {event_name}'
                }
            }
        
        # 提取 COS 信息
        cos_info = record.get('cos', {})
        bucket_info = cos_info.get('cosBucket', {})
        object_info = cos_info.get('cosObject', {})
        
        bucket_name = bucket_info.get('name', '')
        object_key = object_info.get('key', '')
        object_size = object_info.get('size', 0)
        content_type = object_info.get('meta', {}).get('Content-Type', '')
        
        if not bucket_name or not object_key:
            raise ValueError("无法获取 bucket 名称或对象 key")
        
        # 从 bucket 名称中提取 region（格式通常为: bucket-appid）
        # COS 链接格式: https://{bucket}.cos.{region}.myqcloud.com/{key}
        # 注意：这里需要根据实际的 bucket 配置来构造正确的链接
        # 地区从context获取
        region = context.get("tencentcloud_region", 'ap-singapore')
        
        # 合成 COS 对象访问链接 样例 https://suagent-xxx.cos.ap-singapore.myqcloud.com/documents/example.pdf
        cos_url = f"https://{bucket_name}.cos.{region}.myqcloud.com/{object_key}"
        
        # 进行回调测试
        print(f"正在测试链接: {cos_url}")
        
        # 使用 curl 命令进行 HEAD 请求
        # -I 或 --head: 只获取响应头
        # -s: 静默模式
        # -o /dev/null: 丢弃输出内容
        # -w "%{http_code}": 只输出 HTTP 状态码
        # --connect-timeout: 连接超时
        # --max-time: 最大执行时间
        result = subprocess.run(
            ['curl', '-I', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
             '--connect-timeout', '5', '--max-time', '10', cos_url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        status_code = result.stdout.strip()
        
        # 检查响应状态码
        if status_code == '200':
            return {
                'statusCode': 200,
                'body': {
                    'message': '上传成功',
                    'url': cos_url,
                    'object_key': object_key,
                    'content_type': content_type,
                    'object_size': object_size,
                    'bucket_name': bucket_name,
                    'event_time': record.get('event', {}).get('eventTime', '')
                }
            }
        else:
            raise Exception(f"回调测试失败，HTTP 状态码: {status_code}")
    
    except subprocess.TimeoutExpired as e:
        error_msg = f"网络请求超时: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': {
                'message': error_msg
            }
        }
    
    except subprocess.SubprocessError as e:
        error_msg = f"curl 执行错误: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': {
                'message': error_msg
            }
        }
    
    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': {
                'message': error_msg
            }
        }