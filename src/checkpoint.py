import time
from pathlib import Path
from threading import Thread
import pickle
import os
import logging


logger = logging.getLogger(__name__)


class SavableParams:
    def __init__(
        self,
        save_to: Path,
        autosave_period: int = 900,
        enable_autosaving: bool = True,
        force_restart: bool = False,
        **kwargs,
    ):
        self.__save_path = save_to
        self.__autosaving = enable_autosaving
        self.__autosave_period = autosave_period
        self.__thread_interrupted = False
        self.__reserved_vars = set(self.__dict__.keys())

        for key in kwargs:
            self.__setattr__(key, kwargs[key])
        if not force_restart:
            self._load_from(self.__save_path)
        if enable_autosaving:
            Thread(target=self._run_save_thread, daemon=True).start()

    @property
    def save_path(self):
        return self.__save_path

    @save_path.setter
    def save_path(self, value: Path):
        self.__save_path = value

    @property
    def autosaving(self):
        return self.__autosaving

    @autosaving.setter
    def autosaving(self, value: bool):
        # TODO: Fix potential error with several threads writing checkpoints
        if value and not self.__autosaving:
            Thread(target=self._run_save_thread, daemon=True).start()
        elif not value and self.__autosaving:
            self.interrupt()

        self.__autosaving = value

    @property
    def autosave_period(self):
        return self.__autosave_period

    @autosave_period.setter
    def autosave_period(self, value: int):
        self.__autosave_period = value

    @property
    def _thread_interrupted(self):
        return self.__thread_interrupted

    def interrupt(self):
        # TODO: Make it instant
        if not self.__autosaving:
            logger.warning("Interrupt is useless if autosaving option is off")
        else:
            self.__thread_interrupted = True

    def save(self):
        self._save_to(self.__save_path)

    def _run_save_thread(self):
        time.sleep(self.__autosave_period)
        while not self.__thread_interrupted:
            inner_thread = Thread(target=self.save, daemon=False)
            inner_thread.start()
            inner_thread.join()
            time.sleep(self.__autosave_period)

    def _load_from(self, load_path: Path):
        if os.path.exists(load_path):
            with open(load_path, "rb") as file:
                try:
                    savable_other = pickle.load(file)
                except Exception as err:
                    logger.warning(f"Load failed: {err}")
                    return None

            for key in savable_other.__dict__:
                if key not in self.__reserved_vars:
                    self.__setattr__(key, savable_other.__dict__[key])

    def _save_to(self, save_path: Path):
        with open(save_path, "wb") as file:
            pickle.dump(self, file)
        logger.info("Object dumped")
        print("Dumped")
