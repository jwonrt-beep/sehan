# 주식회사 세한메카트로닉스 공식 홈페이지

**ONE STOP TOTAL SOLUTION** — 산업용 로봇 자동화 시스템 전문기업 (세한통상)

공식 회사소개형 홈페이지. 광고 랜딩이 아닌 신뢰감 있는 제조업·산업자동화 기업 소개 사이트입니다.

## 사이트 구조

```
세한홈페이지/
├── index.html            # 메인
├── company.html          # 회사소개 (개요·연혁·대표·경영이념·조직도·임직원)
├── business.html         # 사업영역
├── products.html         # 제품 및 시스템
├── smartfactory.html     # 스마트팩토리
├── cases.html            # 구축사례 / 시뮬레이션
├── certifications.html   # 인증 및 파트너
├── locations.html        # 사업장 / 연락처
├── contact.html          # 문의
├── css/
│   └── style.css         # 디자인 시스템 (네이비·블루·화이트·그레이)
├── docs/
│   └── SITE_PLAN.md      # 기획·사이트맵·섹션 구성
└── (기존 solutions/, maintenance.html, education.html, cases-detail.html 등 유지 가능)
```

## 실행 방법

`index.html`을 브라우저로 열거나, 로컬 서버로 실행합니다.

```bash
python -m http.server 8080
# http://localhost:8080 접속
```

## 수정 시 참고

- **회사정보·사업장·연락처**: 각 페이지의 푸터와 locations.html, contact.html 내 텍스트를 직접 수정. 시점에 따라 주소·전화·팩스·이메일이 다를 수 있으므로 관리자가 쉽게 찾아 수정할 수 있도록 블록 단위로 구성되어 있음.
- **인증서·연혁·구축사례**: certifications.html, company.html(연혁), cases.html — 이미지 경로와 텍스트만 교체하면 됨. 인증서 이미지는 `.cert-card .thumb` 영역에 넣으면 됨.
- **이미지**: 메인 비주얼, 사업장 사진, 시뮬레이션 캡처, 인증서 스캔 등은 placeholder. 실제 이미지로 교체 시 경로만 수정.

## 디자인 방향

- 메인 컬러: 네이비, 블루, 화이트, 그레이 계열.
- 과한 애니메이션·광고 문구 배제, 차분한 기업 문체.
- 반응형: 모바일에서 네비게이션 토글, 카드·그리드 자동 조정.
