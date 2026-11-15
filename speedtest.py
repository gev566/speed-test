#!/usr/bin/env python3
"""Замер скорости скачивания: N последовательных запросов к одному адресу."""

import argparse
import sys
import time
import urllib.error
import urllib.request

CHUNK_SIZE = 64 * 1024  # читаем ответ кусками по 64 КБ, чтобы не держать весь файл в памяти


def download_once(url: str, timeout: float) -> tuple[float, int]:
    """Скачивает адрес один раз. Возвращает (время в секундах, число байт)."""
    request = urllib.request.Request(url, headers={"User-Agent": "speed-test/1.0"})
    started = time.perf_counter()
    size = 0
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:  # пустой кусок — ответ прочитан полностью
                break
            size += len(chunk)
    elapsed = time.perf_counter() - started
    return elapsed, size


def main() -> int:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания.")
    parser.add_argument("url", help="адрес, который скачиваем (например, тяжёлая картинка)")
    parser.add_argument("-n", "--count", type=int, default=10, help="число запросов (по умолчанию 10)")
    parser.add_argument("-t", "--timeout", type=float, default=30.0, help="таймаут одного запроса в секундах")
    args = parser.parse_args()

    if args.count < 1:
        parser.error("число запросов должно быть не меньше 1")

    total_time = 0.0
    total_bytes = 0

    for number in range(1, args.count + 1):
        try:
            elapsed, size = download_once(args.url, args.timeout)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
            print(f"Запрос {number} не удался: {error}", file=sys.stderr)
            return 1
        total_time += elapsed
        total_bytes += size
        print(f"Запрос {number:>2}: {elapsed:.3f} с, {size / 1_000_000:.2f} МБ")

    if total_bytes == 0 or total_time == 0:
        print("Сервер не вернул данных — скорость посчитать нельзя.", file=sys.stderr)
        return 1

    average_time = total_time / args.count
    megabits_per_second = total_bytes * 8 / total_time / 1_000_000
    megabytes_per_second = total_bytes / total_time / 1_000_000

    print()
    print(f"Запросов:              {args.count}")
    print(f"Среднее время запроса: {average_time:.3f} с")
    print(f"Скачано всего:         {total_bytes / 1_000_000:.2f} МБ ({total_bytes} байт)")
    print(f"Скорость скачивания:   {megabits_per_second:.2f} Мбит/с ({megabytes_per_second:.2f} МБ/с)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
