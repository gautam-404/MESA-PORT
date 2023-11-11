# istarmap.py for Python 3.8+
import multiprocessing.pool as mpp


def istarmap(self, func, iterable, chunksize=1):
    """
    starmap-version of imap

    Parameters
    ----------
    func : callable
        The function to apply to the items of the iterable.
    iterable : iterable
        The iterable to apply the function to.
    chunksize : int, optional
        The number of items to send to the worker processes at once.
        Default is 1.

    Returns
    -------
    generator
        A generator that yields the results of applying the function to
        the items of the iterable.

    Raises
    ------
    ValueError
        If chunksize is less than 1.

    Notes
    -----
    This method is similar to the built-in `itertools.starmap`, but
    uses a pool of worker processes to apply the function in parallel.

    """
    self._check_running()
    if chunksize < 1:
        raise ValueError(
            "Chunksize must be 1+, not {0:n}".format(
                chunksize))

    task_batches = mpp.Pool._get_tasks(func, iterable, chunksize)
    result = mpp.IMapIterator(self)
    self._taskqueue.put(
        (
            self._guarded_task_generation(result._job,
                                          mpp.starmapstar,
                                          task_batches),
            result._set_length
        ))
    return (item for chunk in result for item in chunk)


mpp.Pool.istarmap = istarmap