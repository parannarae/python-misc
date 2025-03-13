import requests
import concurrent.futures

from datetime import date, datetime, timedelta
from typing import Any, Callable, List, Optional, Tuple

from data_template import DataTemplate
from log_util import get_logger

##############################
# Configurations
##############################

##### Parallelism configuration
NUMBER_OF_PROCESSES = 8
#####

##### API configuration
HOST_URL = 'http://localhost:8080/storyline-service'
ACCESS_TOKEN = 'some.access.token'
#####

##### Input data configuration
DATA_TEMPLATE_FILENAME = 'data_sample.txt'  # file containing POST body data template
DEPENDENT_IDS = [411, 412, 413, 414, 415, 416, 417, 418, 419, 420]
START_DATE =  date(2000, 3, 1)
DAYS_TO_ITERATE = 300   # simulated site size (days are used instead of multiple sites to minimize data preparation)
#####

##############################
# End of Configurations
##############################


# set thread to maximum (declaratively set the value defined in Python implementation)
#   ref: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
NUMBER_OF_THREADS = NUMBER_OF_PROCESSES + 4

API_HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": 'application/json',
}


logger = get_logger(__name__)


# Note: Only top level function can be passed to ProcessPool due to limitation of pickle (i.e. wrapper function cannot apply to functions called by ProcessPoolExecutor)
#   ref: https://stackoverflow.com/questions/72766345/attributeerror-cant-pickle-local-object-in-multiprocessing/72776044#72776044
def log_process_time(func: Callable) -> None:
    """Decorator to log processing time of a `func`

    Args:
        func (Callable): function to log
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        logger.info(f"{func.__name__} is executed for {(end - start).total_seconds() * 1000:.3f}ms")

        return result

    return wrapper


def create_storyline(dependent_id: int, target_date: date) -> Optional[int]:
    """Call Api to create Storyline.

    None would be returned if API call is failed.
    """
    url = f"{HOST_URL}/v3/internal/storylines"
    response = requests.post(
        url = url,
        headers = API_HEADERS,
        json = {
            "date": target_date.strftime('%Y-%m-%d'),
            "dependentId": dependent_id,
        }
    )

    storyline_id = None
    if response.status_code == 201:
        storyline_id = response.json()['data']['id']

    return storyline_id


def create_stories(storyline_id:int, json: Any) -> Tuple[int, float]:
    """Call API to create stories under `storyline_id`.

    Return a tuple containing status code and a processing time in second.
    """
    # add redundancy (log_process_time) due to ProcessPoolExecutor limitation
    start = datetime.now()

    url = f"{HOST_URL}/v3/internal/storylines/{storyline_id}/stories/create-bulk"

    response = requests.post(
        url = url,
        headers = API_HEADERS,
        json = json
    )

    end = datetime.now()

    return response.status_code, (end - start).total_seconds()


def create_storyline_data(dependent_id: int, target_date: date, data_template: DataTemplate) -> Tuple[Optional[int], float]:
    """Call create storyline and stories API in sequence.

    Return a tuple containing storyline_id (None if failed on creating) and
    stories creation time in second.
    """
    storyline_id = create_storyline(dependent_id, target_date)
    process_time = None

    if storyline_id:
        code, process_time = create_stories(
            storyline_id = storyline_id,
            json = data_template.get_json(
                dependent_id = dependent_id,
                target_date = target_date.strftime('%Y-%m-%d')
            )
        )

        if code != 201:
            logger.info(f"Fail on creating stories for storyline (id:{storyline_id})")
    else:
        logger.info(f"Fail on creating storyline for dependent ({dependent_id}) at {target_date}")

    return storyline_id, process_time


def run_process(target_date: date, data_template: DataTemplate) -> List[Tuple[Optional[int], float]]:
    """Create storyline for all dependents at `target_date`.

    Return a list containing tuple of created storyline id (None if failed on
    creating) and stories creation time in second.

    Return value example:
        [(1, 0.53), (2, 0.50), (3, 0.49)]
    """
    logger.info(f"===Running threads to create storyline at {target_date}===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
        futures = [executor.submit(create_storyline_data, dependent_id, target_date, data_template) for dependent_id in DEPENDENT_IDS]

        result = [f.result() for f in concurrent.futures.as_completed(futures)]

    return result


def __extract_result(results: List[List[Tuple[int, float]]]) -> Tuple[List[List[int]], List[float]]:
    """From `result` extract a nested list of storyline ids, and a flat list of process time.

    Return value example:
        ([1, 2, 3], [0.53, 0.50, 0.49])
    """
    # keep the original structure of nested list such that it can be clean up with multi-process
    storyline_ids = []
    # make a flat list with not None data only
    stories_creation_time = []
    # results contains List[List[Tuple]] (one nested result per process)
    for result in results:
        ids_in_process = []
        for item in result:
            if item[0] is not None:
                ids_in_process.append(item[0])
            if item[1] is not None:
                stories_creation_time.append(item[1])

        storyline_ids.append(ids_in_process)

    return storyline_ids, stories_creation_time


@log_process_time
def main() -> List[List[int]]:
    logger.info("=====Starting main=====")
    date_list = [START_DATE + timedelta(days=i) for i in range(DAYS_TO_ITERATE)]
    data_template = DataTemplate(DATA_TEMPLATE_FILENAME)

    with concurrent.futures.ProcessPoolExecutor(max_workers=NUMBER_OF_PROCESSES) as executor:
        futures = [executor.submit(run_process, target_date, data_template) for target_date in date_list]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    number_of_storylines = DAYS_TO_ITERATE * len(DEPENDENT_IDS)
    logger.info(f"Finished creating {number_of_storylines} storylines")

    storyline_ids, stories_creation_time_list = __extract_result(results)

    average_time_str = 'N/A'
    if len(stories_creation_time_list) > 0:
        # calculate average time in ms
        average_time_str = f'{sum(stories_creation_time_list) / number_of_storylines * 1000:.3f}'

    logger.info(
        f"Average time on the creating stories API: {average_time_str}ms"
    )

    return storyline_ids


def delete_storyline(id: int) -> Optional[int]:
    """Delete storyline having `id` and its associated data.

    Return `id` if it failed to delete.
    """
    url = f"{HOST_URL}/v3/internal/storylines/{id}/unsafe-delete"
    response = requests.post(
        url = url,
        headers = API_HEADERS
    )

    if response.status_code != 204:
        return id


def run_delete_process(storyline_ids: List[int]) -> List[int]:
    """Run `delete_storyline` using threads.

    Returns list of storyline ids failed on deletion.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
        futures = [executor.submit(delete_storyline, id) for id in storyline_ids]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    return [id for id in results if id is not None]


@log_process_time
def clean_up(storyline_ids_list:List[List[int]]) -> None:
    """Delete storylines with id in `storyline_ids_list`
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
        futures = [executor.submit(run_delete_process, lst) for lst in storyline_ids_list]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # results is a list containing list of ids returned from each process
    logger.info(f"All storylines are deleted except ids: {[item for result in results for item in result]}")


if __name__ == '__main__':
    # for i in range(5):
    #     logger.info(f"==========Iteration: {i}==========")
    results = main()
    # clean up created storylines
    logger.info(f"=====Deleting storylines=====")
    clean_up(results)
