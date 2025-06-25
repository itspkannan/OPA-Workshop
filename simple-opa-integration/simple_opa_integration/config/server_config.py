from dataclasses import dataclass
import multiprocessing

@dataclass()
class ServerConfig:
    host: str
    port: int
    workers: int = 1
    dev: bool = False
    access_log: bool = False

    def __post_init__(self):
        max_workers = ServerConfig.__cpu_limit()
        self.workers =  max_workers if self.workers > max_workers else self.workers

    @staticmethod
    def __cpu_limit():

        try:
            with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as quota, \
                    open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as period:
                quota_val = int(quota.read())
                period_val = int(period.read())
                if quota_val > 0 and period_val > 0:
                    return max(1, quota_val // period_val)
        except Exception:
            pass
        return multiprocessing.cpu_count()