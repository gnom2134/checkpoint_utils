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
        every_n_seconds: int = 900,
        enable_autosaving: bool = True,
        force_restart: bool = False,
        **kwargs,
    ):
        self._save_path = save_to
        self._autosaving = [enable_autosaving]
        self._save_every_N_seconds = every_n_seconds
        self._thread_interrupted = [False]
        self._reserved_vars = {}
        self._reserved_vars = set(self.__dict__.keys())
        for key in kwargs:
            self.__setattr__(key, kwargs[key])
        if not force_restart:
            self._load_from(self._save_path)
        if enable_autosaving:
            Thread(target=self._run_save_thread, daemon=True).start()

    def interrupt(self):
        # TODO: Make it instant
        if not self._autosaving[0]:
            logger.warning("Interrupt is useless if autosaving option is off")
        else:
            self._thread_interrupted[0] = True

    def set_autosave(self, enable_autosaving):
        # TODO: Fix potential error with several threads writing checkpoints
        if enable_autosaving and not self._autosaving[0]:
            Thread(target=self._run_save_thread, daemon=True).start()
        elif not enable_autosaving and self._autosaving[0]:
            self.interrupt()

        self._autosaving[0] = enable_autosaving

    def save(self):
        self._save_to(self._save_path)

    def _run_save_thread(self):
        time.sleep(self._save_every_N_seconds)
        while not self._thread_interrupted[0]:
            inner_thread = Thread(target=self._save_to, args=[self._save_path], daemon=False)
            inner_thread.start()
            inner_thread.join()
            time.sleep(self._save_every_N_seconds)

    def __setattr__(self, key, value):
        if hasattr(self, "_reserved_vars") and key in self._reserved_vars:
            raise AttributeError(f"{key} is a reserved field, please use another name")
        else:
            super(SavableParams, self).__setattr__(key, value)

    def _load_from(self, load_path: Path):
        if os.path.exists(load_path):
            with open(load_path, "rb") as file:
                try:
                    savable_other = pickle.load(file)
                except Exception as err:
                    logger.warning(f"Load failed: {err}")
                    return None

            for key in savable_other.__dict__:
                if key not in self._reserved_vars:
                    self.__setattr__(key, savable_other.__dict__[key])

    def _save_to(self, save_path: Path):
        with open(save_path, "wb") as file:
            pickle.dump(self, file)
        logger.info("Object dumped")
