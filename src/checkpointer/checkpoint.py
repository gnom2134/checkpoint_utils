import time
from pathlib import Path
from threading import Thread, current_thread
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
        self.__current_thread = Thread(target=self._run_save_thread, daemon=True)
        self.__thread_writing = False
        self.__reserved_vars = set(self.__dict__.keys())

        for key in kwargs:
            self.__setattr__(key, kwargs[key])
        if not force_restart:
            self._load_from(self.__save_path)
        if enable_autosaving:
            self.__current_thread.start()

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
        if value and not self.__autosaving:
            self.__current_thread = Thread(target=self._run_save_thread, daemon=True)
            self.__current_thread.start()
        elif not value and self.__autosaving:
            self.interrupt()

        self.__autosaving = value

    @property
    def autosave_period(self):
        return self.__autosave_period

    @autosave_period.setter
    def autosave_period(self, value: int):
        self.__autosave_period = value

    def interrupt(self):
        if not self.__autosaving:
            logger.warning("Interrupt is useless if autosaving option is off")
        else:
            self.__current_thread.interrupted = True
            if self.__thread_writing:
                while self.__thread_writing:
                    time.sleep(0.1)

    def save(self):
        if self.__current_thread.is_alive() or self.autosaving:
            logger.warning("Switching to manual save mode. Autosave disabled. It may take a few moments...")
            self.autosaving = False
        self._save_to(self.__save_path)

    def _run_save_thread(self):
        time.sleep(self.__autosave_period)
        while not getattr(current_thread(), "interrupted", False):
            self.__thread_writing = True
            inner_thread = Thread(target=self._save_to, args=[self.__save_path], daemon=False)
            inner_thread.start()
            inner_thread.join()
            self.__thread_writing = False
            time.sleep(self.__autosave_period)

    def _load_from(self, load_path: Path):
        if os.path.exists(load_path):
            with open(load_path, "rb") as file:
                try:
                    savable_other = pickle.load(file)
                except Exception as err:
                    logger.warning(f"Load failed: {err}")
                    return None

            for key in savable_other:
                if key not in self.__reserved_vars:
                    self.__setattr__(key, savable_other[key])

    def _save_to(self, save_path: Path):
        with open(save_path, "wb") as file:
            pickle.dump({s: self.__dict__[s] for s in self.__dict__ if s not in self.__reserved_vars}, file)
        logger.info("Object dumped")
