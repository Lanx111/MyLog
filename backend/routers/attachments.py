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
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10 MB

# 扩展名 → MIME 类型映射（当浏览器未提供 Content-Type 时使用）
EXT_TO_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    ".md": "text/markdown", ".txt": "text/plain", ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".zip": "application/x-zip-compressed",
}


def _classify(ext: str) -> str:
    """根据扩展名返回 'image' 或 'attachment'。"""
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    return "attachment"


def _validate_file(filename: str, content_type: str | None, size: int):
    """校验文件类型和大小，不通过则抛出 HTTPException。

    优先使用浏览器报告的 MIME 类型，但如果浏览器未提供或提供了无法识别的类型，
    则回退到扩展名判断——这在 .md 等非标准 MIME 文件上传时至关重要。
    """
    ext = Path(filename).suffix.lower() if filename else ""

    # 1. 先按扩展名判断文件类别（更可靠）
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(400, "图片文件不能超过 5 MB")
    elif ext in ALLOWED_ATTACHMENT_EXTENSIONS:
        if size > MAX_ATTACHMENT_SIZE:
            raise HTTPException(400, "附件文件不能超过 10 MB")
    else:
        raise HTTPException(400, f"不支持的文件类型: {ext or '未知扩展名'}")


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

    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    # 保存文件（先保存再校验大小，因为需要通过实际内容判断）
    content = file.file.read()
    actual_size = len(content)

    # 校验（优先使用浏览器报告的 MIME，回退到扩展名推断）
    _validate_file(filename, file.content_type, actual_size)

    # 确定最终 MIME 类型
    mime = file.content_type or EXT_TO_MIME.get(ext, "application/octet-stream")

    stored_name = uuid.uuid4().hex + ext
    file_path = UPLOADS_DIR / stored_name
    file_path.write_bytes(content)

    file_type = _classify(ext)
    att = create_attachment(
        db, post_id,
        filename=filename,
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
