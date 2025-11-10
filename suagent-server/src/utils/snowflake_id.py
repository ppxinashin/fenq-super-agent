import time
 
 
class Snowflake:
    # 定义Snowflake算法的各个参数
    def __init__(self, worker_id: int, datacenter_id: int, sequence: int = 0):
        # 计算位数
        self._worker_id_bits = 5
        self._datacenter_id_bits = 5
        self._sequence_bits = 12
 
        # 定义位偏移量
        self._worker_id_shift = self._sequence_bits
        self._datacenter_id_shift = self._sequence_bits + self._worker_id_bits
 
        # 计算最大ID
        self._max_worker_id = ~(-1 << self._worker_id_bits)
        self._max_datacenter_id = ~(-1 << self._datacenter_id_bits)
        self._max_sequence = ~(-1 << self._sequence_bits)
 
        # 初始化参数
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.last_timestamp = -1
 
    # 生成下一个唯一ID
    def generate_id(self):
        # 获取当前时间戳
        timestamp = int(time.time() * 1000)
 
        # 如果当前时间小于上次生成ID的时间戳，则抛出异常
        if timestamp < self.last_timestamp:
            raise ValueError("Invalid system clock!")
 
        # 如果当前时间戳与上次时间戳相同，则自增序列号
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self._max_sequence
            # 如果序列号等于0，则需要进入下一毫秒重新生成ID
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0
 
        # 保存最后生成ID的时间戳
        self.last_timestamp = timestamp
 
        # 生成最终的唯一ID
        unique_id = ((timestamp << self._datacenter_id_shift) |
                     (self.datacenter_id << self._worker_id_shift) |
                     self.worker_id << self._sequence_bits |
                     self.sequence)
        return unique_id
 
    # 阻塞到下一个毫秒，直到获得新的时间戳
    def _wait_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp
    
def generate_snowflake_id(worker_id: int, datacenter_id: int) -> int:
    snowflake = Snowflake(worker_id=worker_id, datacenter_id=datacenter_id)
    return snowflake.generate_id()
 
 
# 测试方法
if __name__ == '__main__':
    snowflake = Snowflake(worker_id=1, datacenter_id=1)
    for _ in range(10):
        unique_id = snowflake.generate_id()
        print(unique_id)