class ProviderError(RuntimeError):
    def __init__(self, message, code, http_status=None, finish_reason=None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.finish_reason = finish_reason
