import aiohttp
import asyncio
import aiolimiter
from time import time

class WebError(Exception):
    pass

# Initialize rate limiter
limiter = aiolimiter.AsyncLimiter(2000)

async def fetchone(url: str):
    return (await fetch_all([url]))[0]

async def fetch(session: aiohttp.ClientSession, url: str, retries: int = 8, delay: int = 1, timeout: int = 15):
    for _ in range(retries):
        async with limiter:  # Apply rate limiting
            try:
                async with session.get(url, timeout=timeout) as response:
                    content = await response.text()
                    if "Bad Gateway" in content or "something went wrong" in content:
                        raise WebError
                    return content
            except (aiohttp.ClientConnectorError, WebError, asyncio.TimeoutError) as e:
                print(f"Error fetching {url}: {e}")
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
    return None

async def fetch_all(urls: list[str]) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
    
async def fetch_all_and_process(urls, callback, disable_counter=False, progress_str: str = "", **kwargs) -> list:
    n = len(urls)
    st = time()
    if n == 0:
        return None
    
    nb_task_done = 0
    async def counter(coro):
        result = await coro
        nonlocal nb_task_done
        nb_task_done += 1
        print(f"{progress_str}{nb_task_done: 5}/{n} ({nb_task_done/n:.0%})")
        t = time() - st
        print(f"Time since start: {int(t)//60} min {int(t)%60}")

        remaining_sec = int(t/nb_task_done * (n-nb_task_done))
        hour = remaining_sec // 3600
        min = (remaining_sec - hour * 3600) // 60
        sec = remaining_sec - hour * 3600 - min * 60
        print(f"Estimated Remaining Time: {hour}h {min}min {sec}sec")
        print()
        return result

    async with aiohttp.ClientSession() as session:
        tasks = [callback(fetch(session, url), url=url, **kwargs) for url in urls]
        if not disable_counter:
            tasks = [counter(task) for task in tasks]
        return await asyncio.gather(*tasks)