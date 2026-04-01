import threadpool


def thread_pool_task_waiting(func, func_var_list):
    task_pool = threadpool.ThreadPool(20)
    requests = threadpool.makeRequests(func, func_var_list)
    [task_pool.putRequest(req) for req in requests]
    task_pool.wait()

    task_pool.dismissWorkers(20)


def thread_pool_task_waiting_main(func, func_var_list):
    task_pool = threadpool.ThreadPool(20)
    requests = threadpool.makeRequests(func, func_var_list)
    [task_pool.putRequest(req) for req in requests]
    task_pool.wait()

    task_pool.dismissWorkers(20)
