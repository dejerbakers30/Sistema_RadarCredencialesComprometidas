from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflicto"):
        super().__init__(status.HTTP_409_CONFLICT, detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Acceso denegado"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)
