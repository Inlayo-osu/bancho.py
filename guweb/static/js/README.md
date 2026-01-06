# Vanilla JavaScript Architecture

순수 HTML, CSS, JavaScript로 최적화된 프론트엔드 구조입니다.

## 구조

```
static/js/
├── core/
│   ├── api.js          # API 클라이언트
│   ├── utils.js        # 유틸리티 함수
│   ├── components.js   # 재사용 컴포넌트
│   └── store.js        # 상태 관리
└── pages/
    ├── home.js         # 홈 페이지
    ├── profile.js      # 프로필 페이지
    ├── beatmap.js      # 비트맵 페이지
    └── leaderboard.js  # 리더보드 페이지
```

## 사용법

### 1. 기본 HTML 구조

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/static/css/style-new.css">
    <link rel="stylesheet" href="/static/css/components/components-optimized.css">
</head>
<body>
    <div id="profile-app" data-user-id="123" data-mode="0">
        <!-- 컨텐츠 -->
    </div>

    <!-- Core scripts -->
    <script src="/static/js/core/api.js"></script>
    <script src="/static/js/core/utils.js"></script>
    <script src="/static/js/core/store.js"></script>
    <script src="/static/js/core/components.js"></script>
    
    <!-- Page script -->
    <script src="/static/js/pages/profile.js"></script>
</body>
</html>
```

### 2. API 사용

```javascript
// GET 요청
const data = await api.get('/v1/get_profile_data', { id: 123 });

// POST 요청
const result = await api.post('/v1/submit_score', { score: 1000 });
```

### 3. 유틸리티 함수

```javascript
// 포맷팅
Utils.formatNumber(1234567);  // "1,234,567"
Utils.formatPP(1234.56);      // "1,235pp"
Utils.formatAcc(98.765);      // "98.77%"
Utils.formatPlaytime(3600);   // "1h 0m"
Utils.getModsString(72);      // "HDDT"

// DOM 조작
Utils.setLoading(element, true);
Utils.createElement('div', 'my-class', 'content');
```

### 4. 컴포넌트

```javascript
// Toast 알림
toast.success('프로필 업데이트 완료!');
toast.error('에러가 발생했습니다');
toast.warning('경고 메시지');
toast.info('정보 메시지');

// Modal
const modal = new ModalComponent();
modal.open('<h2>제목</h2><p>내용</p>');
modal.close();

// Loading
const spinner = LoadingComponent.show(container);
LoadingComponent.hide(spinner);

// Tabs
const tabs = new TabsComponent(document.getElementById('tabs'));
```

### 5. 상태 관리

```javascript
// 세션 정보
const isLoggedIn = sessionStore.state.authenticated;
const user = sessionStore.state.user;

// 상태 변경
sessionStore.setState({ authenticated: true, user: userData });

// 상태 구독
sessionStore.subscribe('authenticated', (newValue, oldValue) => {
    console.log('인증 상태 변경:', newValue);
});
```

## 특징

✅ **Zero Dependencies** - 외부 라이브러리 없음
✅ **모듈화** - 코어 기능과 페이지 로직 분리
✅ **최적화** - Lazy loading, Debounce, IntersectionObserver
✅ **타입 안전** - JSDoc 주석으로 타입 힌트
✅ **재사용성** - 컴포넌트 시스템
✅ **반응형** - 모바일 최적화
✅ **성능** - RequestAnimationFrame, 효율적인 DOM 조작
✅ **접근성** - Semantic HTML, ARIA

## 페이지별 초기화

각 페이지는 자동으로 초기화됩니다:

```javascript
// profile.js
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('profile-app');
    if (container) {
        const userId = parseInt(container.dataset.userId);
        window.profilePage = new ProfilePage(userId);
    }
});
```

## 성능 최적화

- **이미지 지연 로딩**: `loading="lazy"` 속성
- **Debouncing**: 검색, 스크롤 이벤트
- **IntersectionObserver**: 스크롤 애니메이션
- **RequestAnimationFrame**: 부드러운 애니메이션
- **이벤트 위임**: 동적 요소 처리
- **메모리 관리**: 이벤트 리스너 정리

## 브라우저 지원

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 마이그레이션

기존 Vue 2 코드를 단계적으로 교체:

1. Core scripts를 base.html에 추가
2. 페이지별로 순수 JS로 재작성
3. 기존 Vue 코드 제거
