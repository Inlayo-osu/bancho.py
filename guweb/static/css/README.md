# Inlayo UI - 단일화된 CSS 구조

## 개요
모든 CSS 스타일이 하나의 통합 파일로 단일화되었습니다.

## 파일 구조

### 메인 스타일시트
- **`main.css`** - 모든 스타일이 포함된 단일 파일
  - CSS 변수 (색상, 간격, 타이포그래피 등)
  - 기본 레이아웃
  - 네비게이션 바
  - 버튼 컴포넌트
  - 카드 컴포넌트  
  - 홈페이지 스타일
  - 유틸리티 클래스
  - 반응형 디자인

### 외부 의존성
- **`bulma.css`** - Bulma CSS 프레임워크 (그리드 시스템용)
- **Font Awesome** - 아이콘 라이브러리

## 사용법

### HTML에서 로드
```html
<link rel="stylesheet" href="/static/css/bulma.css" />
<link rel="stylesheet" href="/static/css/main.css" />
```

### 디자인 시스템

#### 색상
```css
--primary-color: #3b82f6
--accent-pink: #ec4899
--accent-purple: #a855f7
--bg-primary: #0f172a
--text-primary: #f1f5f9
```

#### 버튼
```html
<button class="ui-button ui-button-primary">Primary</button>
<button class="ui-button ui-button-pink">Pink</button>
<button class="ui-button ui-button-secondary">Secondary</button>
```

#### 카드
```html
<div class="card">
  <div class="card-header">제목</div>
  <p>내용</p>
</div>

<div class="stat-card">
  <div class="stat-card-value">1,234</div>
  <div class="stat-card-label">플레이어</div>
</div>
```

#### 유틸리티
```html
<div class="flex flex-center gap-md">...</div>
<div class="grid grid-2">...</div>
<p class="text-center text-primary">...</p>
```

## 장점

1. **빠른 로딩** - 단일 CSS 파일로 HTTP 요청 감소
2. **쉬운 유지보수** - 모든 스타일이 한 곳에 통합
3. **일관성** - 통일된 디자인 시스템
4. **최적화** - 중복 코드 제거
5. **간편성** - 추가 import 불필요

## 반응형 디자인

- **데스크톱**: 기본 스타일
- **태블릿** (< 1024px): 그리드 조정
- **모바일** (< 768px): 단일 컬럼, 간격 축소

## 업데이트 내역

### 2026-01-06
- ✅ 모든 CSS를 main.css로 통합
- ✅ base.html에서 단일 CSS 파일 로드
- ✅ 페이지별 CSS import 제거
- ✅ 현대적인 디자인 시스템 적용
- ✅ 애니메이션 및 효과 추가

## 주의사항

- `bulma.css`는 그리드 시스템을 위해 유지
- 페이지별 추가 스타일이 필요한 경우 `main.css`에 추가
- CSS 변수를 사용하여 테마 쉽게 변경 가능
