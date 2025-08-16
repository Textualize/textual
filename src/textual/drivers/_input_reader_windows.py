import ctypes
import msvcrt
import sys
import threading
from concurrent.futures import Future
from ctypes.wintypes import BOOL, DWORD, HANDLE, LPDWORD, LPVOID
from queue import Queue
from typing import Iterator

from textual.constants import DEBUG

__all__ = ("InputReader",)


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.CancelSynchronousIo.argtypes = (HANDLE,)  # hThread
kernel32.CancelSynchronousIo.restype = BOOL

kernel32.OpenThread.argtypes = (
    DWORD,  # dwDesiredAccess
    BOOL,  # bInheritHandle
    DWORD,  # dwThreadId
)
kernel32.OpenThread.restype = HANDLE

kernel32.ReadFile.argtypes = (
    HANDLE,  # hFile
    LPVOID,  # lpBuffer
    DWORD,  # nNumberOfBytesToRead
    LPDWORD,  # lpNumberOfBytesRead
    LPVOID,  # lpOverlapped
)
kernel32.ReadFile.restype = BOOL


kernel32.CloseHandle.argtypes = (HANDLE,)  # hObject
kernel32.CloseHandle.restype = BOOL

THREAD_TERMINATE = 1
ERROR_NOT_FOUND = 1168
ERROR_OPERATION_ABORTED = 995


def _debug_log(msg: str) -> None:
    if DEBUG:
        with open("input_reader_windows.log", "at") as f:
            print(msg, file=f)


def _read_file_thread(
    ready: Future[int],
    queue: Queue[Future[bytes] | None],
) -> None:
    _debug_log("(_read_file_thread) Enter")

    # Perform initialization and notify the main thread when ready
    try:
        file_handle: int = msvcrt.get_osfhandle(sys.__stdin__.fileno())
        thread_handle: int = kernel32.OpenThread(
            THREAD_TERMINATE, False, threading.current_thread().native_id
        )
        if thread_handle == 0:
            raise ctypes.WinError(ctypes.get_last_error())
    except Exception as e:
        _debug_log(f"(_read_file_thread) Initialization exception: {e=}")
        ready.set_exception(e)
        return
    else:
        ready.set_result(thread_handle)

    # Loop read until receiving None
    try:
        num_bytes = 1024
        buffer = ctypes.create_string_buffer(num_bytes)
        num_bytes_read = DWORD()
        while (result := queue.get()) is not None:
            success = kernel32.ReadFile(
                file_handle, buffer, num_bytes, ctypes.byref(num_bytes_read), None
            )
            if success:
                result.set_result(buffer.raw[: num_bytes_read.value])
            else:
                result.set_exception(ctypes.WinError(ctypes.get_last_error()))
    except Exception as e:
        _debug_log(f"(_read_file_thread) Main loop exception: {e=}")
    finally:
        kernel32.CloseHandle(thread_handle)

    _debug_log("(_read_file_thread) normal exit")


class InputReader:
    """Read input from stdin."""

    def __init__(self, timeout: float = 0.1) -> None:
        """

        Args:
            timeout: Seconds to block for input.
        """
        self.timeout = timeout
        self._closed: bool = False

        ready: Future[int] = Future()
        self._queue: Queue[Future[bytes] | None] = Queue()
        self._worker: threading.Thread = threading.Thread(
            target=_read_file_thread, args=(ready, self._queue)
        )
        self._worker.start()
        self._worker_thread_handle = ready.result()

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        if not self._closed:
            _debug_log(
                f"(InputReader.close) ThreadId: {threading.current_thread().native_id}"
            )
            self._closed = True
            self._queue.put(None)
            self._worker.join()

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""
        _debug_log(
            f"(InputReader.__iter__) Enter (ThreadId: {threading.current_thread().native_id})"
        )
        try:
            while not self._closed:
                result: Future[bytes] = Future()
                self._queue.put(result)
                try:
                    data = result.result(timeout=self.timeout)
                except TimeoutError:
                    while not result.done():
                        success = kernel32.CancelSynchronousIo(
                            self._worker_thread_handle
                        )
                        if not success and ctypes.get_last_error() != ERROR_NOT_FOUND:
                            error = ctypes.WinError(ctypes.get_last_error())
                            _debug_log(
                                f"(InputReader.__iter__) CancelSynchronousIo error: {error}"
                            )
                            raise error
                    try:
                        data = result.result()
                    except OSError as e:
                        if e.winerror == ERROR_OPERATION_ABORTED:
                            data = bytes()
                        else:
                            _debug_log(f"(InputReader.__iter__) ReadFile error: {e}")
                            raise  # TODO: check EOF
                yield data
        except Exception as e:
            _debug_log(f"(InputReader.__iter__) Exception: {e}")
            raise
        else:
            _debug_log(f"(InputReader.__iter__) normal exit")
