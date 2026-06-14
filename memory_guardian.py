from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil


DEFAULT_TASK_NAME = "MemoryBoost"
DEFAULT_THRESHOLD = 90.0      # 内存占用率阈值
DEFAULT_RELEASE = 80.0        # 低于该值后允许再次触发
DEFAULT_INTERVAL = 5          # 轮询间隔（秒）
DEFAULT_COOLDOWN = 120        # 触发后的冷却时间（秒）

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "memory_guardian.log"


def setup_logging() -> None:
    """初始化日志配置"""
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        encoding="utf-8",
    )


def memory_percent() -> float:
    """获取当前系统内存占用率"""
    return float(psutil.virtual_memory().percent)


def run_task(task_name: str) -> bool:
    """
    运行 Windows 计划任务。

    返回：
        True  : 任务启动成功
        False : 任务启动失败
    """
    try:
        result = subprocess.run(
            ["schtasks", "/run", "/tn", task_name],
            capture_output=True,
            text=True,
            shell=False,
        )

        if result.returncode == 0:
            logging.info("Triggered task: %s", task_name)
            return True

        logging.warning(
            "Failed to trigger task=%s rc=%s stdout=%r stderr=%r",
            task_name,
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )
        return False

    except Exception as e:
        logging.exception("Exception when triggering task %s: %s", task_name, e)
        return False


def main() -> int:
    if os.name != "nt":
        print("该脚本仅支持 Windows 系统运行。")
        return 2

    parser = argparse.ArgumentParser(description="内存守护进程")

    parser.add_argument(
        "--task",
        default=DEFAULT_TASK_NAME,
        help="计划任务名称"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="触发阈值（内存占用率）"
    )

    parser.add_argument(
        "--release",
        type=float,
        default=DEFAULT_RELEASE,
        help="重新布防阈值"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help="轮询间隔（秒）"
    )

    parser.add_argument(
        "--cooldown",
        type=int,
        default=DEFAULT_COOLDOWN,
        help="冷却时间（秒）"
    )

    args = parser.parse_args()

    setup_logging()

    logging.info(
        "Started memory guardian: task=%s threshold=%.1f release=%.1f interval=%ss cooldown=%ss",
        args.task,
        args.threshold,
        args.release,
        args.interval,
        args.cooldown,
    )

    # 是否处于已布防状态
    armed = True

    # 上一次触发时间戳
    last_trigger_ts = 0.0

    while True:
        try:
            mem = memory_percent()
            now = time.time()

            # 内存下降到 release 以下时重新布防
            # 这样下一次达到 threshold 时才允许再次触发
            if mem <= args.release:
                if not armed:
                    logging.info("Re-armed at memory=%.1f%%", mem)
                armed = True

            # 触发条件：
            # 1. 已布防
            # 2. 内存超过阈值
            # 3. 不处于冷却期
            if (
                armed
                and mem >= args.threshold
                and (now - last_trigger_ts) >= args.cooldown
            ):
                logging.info(
                    "Threshold reached: memory=%.1f%% >= %.1f%%",
                    mem,
                    args.threshold,
                )

                ok = run_task(args.task)

                if ok:
                    # 触发成功后记录时间并解除布防
                    last_trigger_ts = now
                    armed = False
                else:
                    # 即使触发失败也进入短暂冷却
                    # 避免疯狂调用任务和刷日志
                    last_trigger_ts = now

            time.sleep(args.interval)

        except KeyboardInterrupt:
            logging.info("Stopped by user.")
            return 0

        except Exception as e:
            logging.exception("Loop error: %s", e)

            # 发生异常后等待一段时间再继续运行
            time.sleep(max(1, args.interval))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
