from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models.models import User, EmailVerification, EmailSendLog
from app.models.schemas import (
    UserCreate, UserCreateSimple, UserLogin, UserResponse, Token, 
    SendVerificationCodeRequest, VerifyCodeRequest, SendVerificationCodeResponse,
    CreditResponse, CreditDeductionRequest
)
from app.utils.auth import verify_password, get_password_hash, create_access_token, verify_token
from app.utils.email import send_verification_email, generate_verification_code
from app.utils.credits import check_user_credits, deduct_user_credits
from app.config import settings

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    print("🟢 [TEST] Test endpoint called successfully!")
    return {"status": "ok", "message": "Backend is working", "timestamp": "2024-01-25"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def check_email_send_cooldown(db: Session, email: str) -> int:
    """检查邮箱发送冷却时间，返回剩余秒数"""
    cooldown_time = datetime.utcnow() - timedelta(seconds=settings.email_send_cooldown_seconds)
    recent_send = db.query(EmailSendLog).filter(
        and_(
            EmailSendLog.email == email,
            EmailSendLog.sent_at > cooldown_time
        )
    ).first()
    
    if recent_send:
        elapsed = datetime.utcnow() - recent_send.sent_at
        remaining = settings.email_send_cooldown_seconds - int(elapsed.total_seconds())
        return max(0, remaining)
    return 0

def get_valid_verification_code(db: Session, email: str) -> EmailVerification:
    """获取有效的验证码记录"""
    return db.query(EmailVerification).filter(
        and_(
            EmailVerification.email == email,
            EmailVerification.expires_at > datetime.utcnow(),
            EmailVerification.used == False,
            EmailVerification.attempts < settings.max_verification_attempts
        )
    ).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/send-verification-code", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: SendVerificationCodeRequest, 
    db: Session = Depends(get_db)
):
    """发送邮箱验证码"""
    print(f"Received request to send verification code to: {request.email}")
    
    # 检查邮箱是否已被注册
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        print(f"Email {request.email} already registered")
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册"
        )
    
    # 检查发送冷却时间
    cooldown_remaining = check_email_send_cooldown(db, request.email)
    if cooldown_remaining > 0:
        print(f"Email {request.email} is in cooldown period: {cooldown_remaining} seconds remaining")
        return SendVerificationCodeResponse(
            success=False,
            message=f"发送过于频繁，请等待 {cooldown_remaining} 秒后重试",
            cooldown_seconds=cooldown_remaining
        )
    
    # 生成验证码
    code = generate_verification_code(settings.verification_code_length)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.verification_code_expire_minutes)
    print(f"Generated verification code for {request.email}: {code}")
    
    # 删除该邮箱之前的验证码记录
    db.query(EmailVerification).filter(EmailVerification.email == request.email).delete()
    
    # 保存新的验证码记录
    verification = EmailVerification(
        email=request.email,
        code=code,
        expires_at=expires_at
    )
    db.add(verification)
    
    # 记录发送日志
    send_log = EmailSendLog(email=request.email)
    db.add(send_log)
    
    db.commit()
    
    # 发送邮件
    print(f"Attempting to send verification email to {request.email}")
    email_sent = await send_verification_email(request.email, code)
    print(f"Email sending result for {request.email}: {email_sent}")
    
    if email_sent:
        return SendVerificationCodeResponse(
            success=True,
            message=f"验证码已发送到 {request.email}，请查收邮件"
        )
    else:
        return SendVerificationCodeResponse(
            success=False,
            message="邮件发送失败，请重试"
        )

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """验证邮箱验证码"""
    verification = get_valid_verification_code(db, request.email)
    
    if not verification:
        raise HTTPException(
            status_code=400,
            detail="验证码不存在、已过期或已达到最大尝试次数"
        )
    
    # 增加尝试次数
    verification.attempts += 1
    
    if verification.code != request.code:
        db.commit()
        remaining_attempts = settings.max_verification_attempts - verification.attempts
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=400,
                detail="验证码错误次数过多，请重新获取验证码"
            )
        raise HTTPException(
            status_code=400,
            detail=f"验证码错误，还可尝试 {remaining_attempts} 次"
        )
    
    # 验证成功，标记为已使用
    verification.used = True
    db.commit()
    
    return {"success": True, "message": "验证码验证成功"}

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册（需要邮箱验证码）"""
    print(f"🟡 [REGISTER] 开始注册流程: {user.email}")
    
    try:
        # 检查用户名是否已存在
        print(f"🟡 [REGISTER] 检查用户名是否存在...")
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            print(f"🔴 [REGISTER] 用户名已存在: {user.username}")
            raise HTTPException(
                status_code=400,
                detail="用户名已被注册"
            )
        
        # 检查邮箱是否已被注册
        print(f"🟡 [REGISTER] 检查邮箱是否存在...")
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            print(f"🔴 [REGISTER] 邮箱已存在: {user.email}")
            raise HTTPException(
                status_code=400,
                detail="邮箱已被注册"
            )
        
        # 验证邮箱验证码
        print(f"🟡 [REGISTER] 验证邮箱验证码...")
        verification = get_valid_verification_code(db, user.email)
        
        if not verification:
            print(f"🔴 [REGISTER] 验证码不存在或已过期: {user.email}")
            raise HTTPException(
                status_code=400,
                detail="验证码不存在、已过期或已达到最大尝试次数。请重新获取验证码。"
            )
        
        # 增加尝试次数
        verification.attempts += 1
        
        if verification.code != user.verification_code:
            db.commit()
            remaining_attempts = settings.max_verification_attempts - verification.attempts
            print(f"🔴 [REGISTER] 验证码错误: {user.email}, 剩余尝试次数: {remaining_attempts}")
            if remaining_attempts <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="验证码错误次数过多，请重新获取验证码"
                )
            raise HTTPException(
                status_code=400,
                detail=f"验证码错误，还可尝试 {remaining_attempts} 次"
            )
        
        # 验证成功，标记为已使用
        verification.used = True
        
        print(f"🟡 [REGISTER] 创建新用户...")
        # 创建新用户
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            email_verified=True,  # 邮箱已验证
            credits=100  # 新用户默认100积分
        )
        
        print(f"🟡 [REGISTER] 保存用户到数据库...")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"🟢 [REGISTER] 用户注册成功: ID={db_user.id}, Email={db_user.email}")
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            is_active=db_user.is_active,
            credits=db_user.credits,
            email_verified=db_user.email_verified,
            created_at=db_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔴 [REGISTER] 注册失败: {str(e)}")
        print(f"🔴 [REGISTER] 错误类型: {type(e)}")
        import traceback
        print(f"🔴 [REGISTER] 堆栈跟踪: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@router.post("/register-simple", response_model=UserResponse)
async def register_user_simple(user: UserCreateSimple, db: Session = Depends(get_db)):
    """简单用户注册（仅开发环境使用，无需验证码）"""
    print(f"⚠️ [REGISTER-SIMPLE] 使用简单注册模式（仅开发环境）")
    
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已被注册
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="邮箱已被注册"
        )
    
    # 创建用户（跳过邮箱验证）
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        email_verified=True,  # 直接设为已验证
        credits=50  # 给测试用户50积分
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    print(f"🟡 [REGISTER-SIMPLE] 简单注册完成: {user.email}")
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        is_active=db_user.is_active,
        credits=db_user.credits,
        email_verified=db_user.email_verified,
        created_at=db_user.created_at
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# 积分相关功能
@router.get("/credits", response_model=CreditResponse)
async def get_user_credits(current_user: User = Depends(get_current_user)):
    """获取用户当前积分"""
    return CreditResponse(
        success=True,
        message=f"当前积分：{current_user.credits}",
        current_credits=current_user.credits
    )

@router.post("/credits/check", response_model=CreditResponse)
async def check_credits_sufficient(
    request: CreditDeductionRequest,
    current_user: User = Depends(get_current_user)
):
    """检查积分是否足够"""
    sufficient = check_user_credits(current_user, request.cost)
    return CreditResponse(
        success=sufficient,
        message=f"积分{'足够' if sufficient else '不足'}，当前积分：{current_user.credits}，需要积分：{request.cost}",
        current_credits=current_user.credits
    )

@router.post("/credits/deduct", response_model=CreditResponse)
async def deduct_credits(
    request: CreditDeductionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """扣除用户积分（下载时调用）"""
    if not check_user_credits(current_user, request.cost):
        raise HTTPException(
            status_code=400,
            detail=f"积分不足，当前积分：{current_user.credits}，需要积分：{request.cost}"
        )
    
    success = deduct_user_credits(db, current_user, request.cost)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="积分扣除失败"
        )
    
    return CreditResponse(
        success=True,
        message=f"成功扣除{request.cost}积分，剩余积分：{current_user.credits}",
        current_credits=current_user.credits
    )