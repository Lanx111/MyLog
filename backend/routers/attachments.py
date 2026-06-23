"""附件上传与删除 API 路由。"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from schemas import ApiResponse
from crud import create_attachment, get_attachment, delete_attachment
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api", tags=["attachments"])

# 上传文件存储根目录
UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# 文件类型白名单
ALLOWED_IMAGE = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_ATTACHMENT = {
    "text/markdown", "text/plain", "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip", "application/x-zip-compressed",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10 MB


def _classify(mime: str) -> str:
    """根据 MIME 类型返回 'image' 或 'attachment'。"""
    if mime in ALLOWED_IMAGE:
        return "image"
    return "attachment"


def _validate_file(filename: str, mime: str, size: int):
    """校验文件类型和大小，不通过则抛出 HTTPException。"""
    if mime in ALLOWED_IMAGE:
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(400, "图片文件不能超过 5 MB")
    elif mime in ALLOWED_ATTACHMENT:
        if size > MAX_ATTACHMENT_SIZE:
            raise HTTPException(400, "附件文件不能超过 10 MB")
    else:
        raise HTTPException(400, f"不支持的文件类型: {mime}")


@router.post("/posts/{post_id}/attachments")
def upload_attachment(
    post_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """为指定日志上传一个附件 (multipart/form-data)。仅日志作者可上传。"""
    from crud import get_post

    post = get_post(db, post_id)
    if not post:
        raise HTTPException(404, "日志不存在")
    if post.user_id != current_user.id:
        raise HTTPException(403, "无权为该日志上传附件")

    # 校验
    mime = file.content_type or "application/octet-stream"
    _validate_file(file.filename or "unknown", mime, file.size or 0)

    # 保存文件
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    stored_name = uuid.uuid4().hex + ext
    file_path = UPLOADS_DIR / stored_name

    content = file.file.read()
    file_path.write_bytes(content)
    actual_size = len(content)

    file_type = _classify(mime)
    att = create_attachment(
        db, post_id,
        filename=file.filename or "unknown",
        stored_name=stored_name,
        file_path=str(file_path),
        file_size=actual_size,
        file_type=file_type,
        mime_type=mime,
    )
    return ApiResponse(data=att.to_dict(), message="附件上传成功")


@router.delete("/attachments/{attachment_id}")
def remove_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除附件。仅附件所属日志的作者可以删除。"""
    from crud import get_post

    # 先查出附件以便做权限校验
    att = get_attachment(db, attachment_id)
    if not att:
        raise HTTPException(404, "附件不存在")

    post = get_post(db, att.post_id)
    if not post or post.user_id != current_user.id:
        raise HTTPException(403, "无权删除该附件")

    success, _ = delete_attachment(db, attachment_id)
    if not success:
        raise HTTPException(500, "删除失败")
    return ApiResponse(message="附件已删除")
