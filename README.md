# DangMooG 중고장터 프로젝트 API 서버

GIST의 원내 중고장터 플랫폼 '도토릿'의 FastAPI를 사용하여 구현된 백엔드 API 서버입니다. 
<br> 계정, 게시물, 보관함 관리, 채팅기록 다양한 데이터들을 관리하는 역할을 합니다.

## 주요 기능
- **사용자 관리**: 사용자 등록, 로그인, 정보 조회 및 수정 기능을 제공합니다.
- **포스트 관리**: 사용자들이 포스트를 작성, 조회, 수정 및 삭제할 수 있는 기능을 제공합니다.
- **카테고리 관리**: 포스트의 카테고리를 관리할 수 있는 기능을 제공합니다.
- **사진 업로드**: 사용자 및 포스트에 사진을 업로드할 수 있는 기능을 제공합니다.
- **채팅 기능**: 사용자 간의 실시간 채팅 기능을 제공합니다.
- **보관함 기능**: 사용자가 보관함에 아이템을 추가, 삭제할 수 있는 기능을 제공합니다.

## 사용된 기술
- **프레임워크**: FastAPI
- **데이터베이스**: SQLAlchemy를 사용한 MariaDB(MySQL)
- **스키마 유효성 검사 및 직렬화**: Pydantic
- **기타**: JWT (JSON Web Tokens)를 사용한 인증

## 주요 파일 구조
```
dangmooz_back/
├── main.py             # FastAPI 앱의 진입점
├── core/
│   ├── crud.py
│   ├── db.py
│   ├── schema.py
│   └── utils.py
├── models/             # 데이터베이스 모델
│   ├── account.py
│   ├── category.py
│   ├── chat.py
│   ├── liked.py
│   ├── locker.py
│   ├── photo.py
│   └── post.py
├── routers/            # 라우터 모듈
│   ├── account.py
│   ├── category.py
│   ├── chat.py
│   ├── locker.py
│   ├── photo.py
│   └── post.py
├── schemas/            # Pydantic 스키마
│   ├── account.py
│   ├── category.py
│   ├── chat.py
│   ├── chat_photo.py
│   ├── locker.py
│   ├── photo.py
│   └── post.py
├── requirements.txt    # 의존성
├── Dockerfile          # Docker 이미지 빌드 설정
└── docker-compose.yaml # Docker Compose 설정
```

## 데이터베이스 구조
주요 테이블과 각 테이블의 필드는 다음과 같습니다:
### 데이터베이스 구조

#### `post` 테이블
- `post_id`: 포스트 ID (자동 증가, 기본 키)
- `title`: 포스트 제목 (문자열, 255자)
- `price`: 가격 (정수)
- `description`: 설명 (텍스트)
- `representative_photo_id`: 대표 사진 ID (정수, NULL 가능)
- `category_id`: 카테고리 ID (정수, 외래 키, `category` 테이블 참조)
- `status`: 상태 (작은 정수, 0: 판매중, 1: 예약, 2: 판매완료)
- `buyer`: 구매자 ID (정수, NULL 가능)
- `use_locker`: 사물함 사용 여부 (작은 정수, 0: 사용안함, 1: 사용함(미인증), 2: 사용함(인증완료))
- `account_id`: 계정 ID (정수, 외래 키, `account` 테이블 참조)
- `username`: 사용자 이름 (문자열, 100자)
- `liked`: 좋아요 수 (정수, 기본값 0)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `account` 테이블
- `account_id`: 계정 ID (자동 증가, 기본 키)
- `username`: 사용자 이름 (문자열, 255자, 유니크)
- `password`: 비밀번호 (문자, 60자, 바이너리)
- `email`: 이메일 (문자열, 255자, 유니크)
- `profile_url`: 프로필 URL (문자열, 2000자, NULL 가능)
- `available`: 사용 가능 여부 (작은 정수, 기본값 1)
- `jail_until`: 차단 해제 시간 (타임스탬프, NULL 가능)
- `fcm`: FCM 토큰 (텍스트, NULL 가능)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `photo` 테이블
- `photo_id`: 사진 ID (자동 증가, 기본 키)
- `url`: 사진 URL (문자열, 2000자)
- `post_id`: 포스트 ID (정수, NULL 가능, 외래 키, `post` 테이블 참조)
- `category_id`: 카테고리 ID (정수, NULL 가능, 외래 키, `category` 테이블 참조)
- `account_id`: 계정 ID (정수, NULL 가능, 외래 키, `account` 테이블 참조)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)

#### `category` 테이블
- `category_id`: 카테고리 ID (자동 증가, 기본 키)
- `category_name`: 카테고리 이름 (문자열, 255자)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `liked` 테이블
- `liked_id`: 좋아요 ID (자동 증가, 기본 키)
- `post_id`: 포스트 ID (정수, 외래 키, `post` 테이블 참조)
- `account_id`: 계정 ID (정수, 외래 키, `account` 테이블 참조)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)

#### `locker` 테이블
- `locker_id`: 사물함 ID (자동 증가, 기본 키)
- `name`: 사물함 이름 (문자열, 10자, 유니크)
- `status`: 상태 (작은 정수, 기본값 1)
- `account_id`: 계정 ID (정수, NULL 가능, 외래 키, `account` 테이블 참조)
- `post_id`: 포스트 ID (정수, NULL 가능, 외래 키, `post` 테이블 참조)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `locker_auth` 테이블
- `locker_auth_id`: 사물함 인증 ID (자동 증가, 기본 키)
- `post_id`: 포스트 ID (정수, 외래 키, `post` 테이블 참조)
- `locker_id`: 사물함 ID (정수, 외래 키, `locker` 테이블 참조)
- `password`: 비밀번호 (문자열, 10자)
- `photo_url`: 사진 URL (문자열, 2000자)
- `is_over`: 완료 여부 (작은 정수, 기본값 0)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `room` 테이블
- `room_id`: 방 ID (문자열, 36자, 기본 키)
- `post_id`: 포스트 ID (정수, 외래 키, `post` 테이블 참조)
- `buyer_id`: 구매자 ID (정수, 외래 키, `account` 테이블 참조)
- `seller_id`: 판매자 ID (정수, 외래 키, `account` 테이블 참조)
- `status`: 상태 (작은 정수, NULL 가능)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)
- `update_time`: 수정 시간 (타임스탬프, 기본값 현재 시간, 수정 시 현재 시간으로 업데이트)

#### `message` 테이블
- `message_id`: 메시지 ID (자동 증가, 기본 키)
- `room_id`: 방 ID (문자열, 36자, 외래 키, `room` 테이블 참조)
- `is_from_buyer`: 구매자로부터 온 메시지 여부 (작은 정수)
- `content`: 메시지 내용 (문자열, 255자)
- `read`: 읽음 여부 (작은 정수, 기본값 0)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)

#### `m_photo` 테이블
- `m_photo_id`: 메시지 사진 ID (자동 증가, 기본 키)
- `url`: 사진 URL (문자열, 2000자)
- `message_id`: 메시지 ID (정수, 외래 키, `message` 테이블 참조)
- `account_id`: 계정 ID (정수, 외래 키, `account` 테이블 참조)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)

#### `blame` 테이블
- `blame_id`: 신고 ID (자동 증가, 기본 키)
- `content`: 신고 내용 (텍스트)
- `blamer_id`: 신고자 ID (정수)
- `create_time`: 생성 시간 (타임스탬프, 기본값 현재 시간)


## 실행 방법

1. 레포지토리를 클론합니다:
    ```bash
    git clone https://github.com/Reelect/DangMooG_server
    cd dangmooz_back
    ```

2. 가상 환경을 만들고 활성화합니다:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate`
    ```

3. 필요한 패키지를 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```

4. 서버를 실행합니다:
    ```bash
    uvicorn app:fastapi_app --reload
    ```

5. 브라우저에서 `http://127.0.0.1:8000/docs`로 이동하여 API 문서를 확인합니다.

## Docker 사용

1. **docker-compose에 환경변수를 세팅해주세요.**


2. **Docker 이미지를 빌드하고 Docker Compose로 컨테이너 실행해주면 됩니다**:
   ```bash
   docker-compose up --build
   ```
3. 설정한 포트 정보에 맞춰서 배포 상황을 확인할 수 있습니다.
