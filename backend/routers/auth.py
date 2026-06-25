#routers/auth.py — 认证路由,基于 FastAPI 框架的标准化、生产级的用户身份认证与授权（Auth）系统
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import timedelta

from database import get_db
from models import User
from schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    ApiResponse,
    RegisterResponseData,
    LoginResponseData,
    UserInfo,
)
from auth_utils import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    return user


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    
    # 1. 数据清洗：统一转小写并去除首尾空格（解决 Admin 和 admin 被视为两人的隐患）
    clean_username = request.username.strip().lower()
    clean_email = request.email.strip().lower()

    # 2. 合并查询：一次数据库 IO 同时检查用户名和邮箱
    # 查出 username 和 email 是为了下面能精准提示到底是哪个重复了
    existing_user = db.query(User.username, User.email).filter(
        or_(
            User.username == clean_username,
            User.email == clean_email
        )
    ).first()

    # 3. 精准拦截：使用 409 Conflict 状态码，语义更准确
    if existing_user:
        if existing_user.username == clean_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被注册")
        if existing_user.email == clean_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已被注册")

    # 4. 创建新用户（注意：使用清洗后的 clean_username 和 clean_email）
    new_user = User(
        username=clean_username,
        email=clean_email,
        password_hash=hash_password(request.password)
    )

    db.add(new_user)

    # 5. 提交事务并增加“并发兜底”机制
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()  # 发生数据库冲突时，必须回滚事务，否则后续数据库操作会报错
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="注册失败，用户名或邮箱已被占用"
        )

    # 6. 返回成功响应
    return ApiResponse(
        code=200,  # 如果你的业务规范规定成功就是 200，这里保持 200 即可
        message="注册成功",
        data=RegisterResponseData(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at
        ).model_dump()
    )


# 1. 提取常量：避免硬编码，方便后续统一修改 (7天 = 60 * 60 * 24 * 7)
ACCESS_TOKEN_EXPIRE_SECONDS = 604800 

@router.post("/login", response_model=ApiResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    
    # 2. 数据清洗：与注册接口保持一致，转小写并去空格
    clean_username = request.username.strip().lower()
    
    # 3. 查询用户 (这里查完整 User 对象是正确的，因为需要 password_hash)
    user = db.query(User).filter(User.username == clean_username).first()

    # 4. 验证密码 (不暴露具体错误字段，防枚举攻击，保持你的优秀写法)
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            # 可选：如果是标准 OAuth2，可以加上 headers={"WWW-Authenticate": "Bearer"}
        )

    # 5. 生成 Token 
    # 注意：请确保你的 create_access_token 内部使用的过期时间也是 ACCESS_TOKEN_EXPIRE_SECONDS
    access_token = create_access_token(
        user_id=user.id, 
        username=user.username,
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS) # 根据你的函数签名调整
    )

    # 6. 返回响应
    return ApiResponse(
        code=200,
        message="登录成功",
        data=LoginResponseData(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_SECONDS, # 使用常量，保持前后端一致
            user=UserInfo(
                id=user.id, 
                username=user.username, 
                email=user.email
            )
        ).model_dump()
    )


@router.get("/me", response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        code=200,
        message="success",
        # 直接传入 Pydantic 实例，无需 .model_dump()
        data=UserInfo(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            created_at=current_user.created_at
        ) 
    )


@router.post("/logout", response_model=ApiResponse)
def logout(current_user: User = Depends(get_current_user)):
    return ApiResponse(code=200, message="登出成功", data=None)