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
ERROR_BROKEN_PIPE = 109
ERROR_NOT_FOUND = 1168
ERROR_OPERATION_ABORTED = 995


def _debug_log(msg: str) -> None:
    if DEBUG:
        thread_id = threading.current_thread().native_id
        with open("input_reader_windows.log", "at") as f:
            print(f"[Thread-{thread_id}]", msg, file=f)


def _read_file_thread(
    fd: int,
    ready: Future[int],
    queue: Queue[Future[bytes] | None],
) -> None:
    _debug_log("(_read_file_thread) enter")

    # Perform initialization and notify the main thread when ready
    try:
        file_handle: int = msvcrt.get_osfhandle(fd)
        thread_id: int = threading.current_thread().native_id
        thread_handle: int = kernel32.OpenThread(THREAD_TERMINATE, False, thread_id)
        if thread_handle == 0:
            raise ctypes.WinError(ctypes.get_last_error())
    except Exception as e:
        _debug_log(f"(_read_file_thread) initialization error: {e}")
        ready.set_exception(e)
        return
    else:
        _debug_log("(_read_file_thread) initialized")
        ready.set_result(thread_handle)

    # Loop read until receiving None
    try:
        while (result := queue.get()) is not None:
            num_bytes = 1024
            buffer = ctypes.create_string_buffer(num_bytes)
            num_bytes_read = DWORD()
            success = kernel32.ReadFile(
                file_handle, buffer, num_bytes, ctypes.byref(num_bytes_read), None
            )
            if success:
                result.set_result(buffer.raw[: num_bytes_read.value])
            else:
                result.set_exception(ctypes.WinError(ctypes.get_last_error()))
    except Exception as e:
        _debug_log(f"(_read_file_thread) exit on error: {e}")
    else:
        _debug_log("(_read_file_thread) exit normally")
    finally:
        kernel32.CloseHandle(thread_handle)


class InputReader:
    """Read input from stdin."""

    def __init__(self, timeout: float = 0.1) -> None:
        """

        Args:
            timeout: Seconds to block for input.
        """
        self._fileno = sys.__stdin__.fileno()
        self.timeout = timeout
        self._close_lock = threading.Lock()
        self._closed: bool = False

        ready: Future[int] = Future()
        self._queue: Queue[Future[bytes] | None] = Queue()
        self._worker_thread: threading.Thread = threading.Thread(
            target=_read_file_thread, args=(self._fileno, ready, self._queue)
        )
        self._worker_thread.start()
        self._worker_thread_handle = ready.result()

    def close(self) -> None:
        """Close the reader (will exit the iterator)."""
        with self._close_lock:
            if not self._closed:
                _debug_log("(InputReader.close) closing")
                self._closed = True
                self._queue.put(None)
                self._worker_thread.join()
                _debug_log("(InputReader.close) closed")

    def __iter__(self) -> Iterator[bytes]:
        """Read input, yield bytes."""
        _debug_log("(InputReader.__iter__) enter")
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
                        if not success:
                            error_code: int = ctypes.get_last_error()
                            if error_code != ERROR_NOT_FOUND:
                                error = ctypes.WinError(error_code)
                                _debug_log(
                                    f"(InputReader.__iter__) CancelSynchronousIo error: {error}"
                                )
                                raise
                    try:
                        data = result.result()
                    except OSError as e:
                        if e.winerror == ERROR_OPERATION_ABORTED:
                            data = bytes()
                        elif e.winerror == ERROR_BROKEN_PIPE:  # EOF
                            break
                        else:
                            _debug_log(f"(InputReader.__iter__) ReadFile error: {e}")
                            raise
                yield data
        except Exception as e:
            _debug_log(f"(InputReader.__iter__) exit on error: {e}")
        else:
            _debug_log(f"(InputReader.__iter__) exit normally")
