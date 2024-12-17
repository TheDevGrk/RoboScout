from multiprocessing.pool import ThreadPool
import data


pool = ThreadPool(processes=1)


pool.apply_async(data.refreshData())

