# 주식회사 세한메카트로닉스 공식 홈페이지

**ONE STOP TOTAL SOLUTION** — 산업용 로봇 자동화 시스템 전문기업

공식 회사소개형 홈페이지. 광고 랜딩이 아닌 신뢰감 있는 제조업·산업자동화 기업 소개 사이트입니다.

- **운영 주소:** https://www.shm21.kr  
- **코드 저장소:** https://github.com/jwonrt-beep/sehan  
- **인수인계 안내:** [docs/HANDOVER.md](docs/HANDOVER.md) ← 다음 관리자는 여기부터

## 사이트 구조

```
세한홈페이지/
├── index.html            # 메인
├── company.html          # 회사소개
├── business.html         # 사업영역
├── products.html         # 제품 및 시스템 (Panasonic 용접로봇)
├── smartfactory.html     # 스마트팩토리
├── cases.html            # 구축사례 / 시뮬레이션
├── certifications.html   # 인증 및 파트너
├── locations.html        # 사업장 / 연락처
├── contact.html          # 문의
├── css/
│   ├── style.css         # 공통 디자인
│   └── products.css      # 제품 페이지 전용
├── assets/images/products/panasonic/   # 제품·설비 이미지
├── images/               # 메인 히어로 등
├── downloads/            # 카탈로그 PDF
├── docs/
│   ├── HANDOVER.md       # 인수인계 (쉬운 설명)
│   ├── HANDOVER_MESSAGE.txt
│   └── SITE_PLAN.md
└── .github/workflows/deploy.yml   # GitHub Pages 자동 배포
```

## 배포 방법

`main` 브랜치에 push 하면 GitHub Actions가 GitHub Pages로 자동 배포합니다.

```bash
git add .
git commit -m "변경 내용"
git push origin main
```

## 로컬에서 미리보기

```bash
python -m http.server 8080
# http://localhost:8080
```

## 수정 시 참고

- **연락처·주소:** `locations.html`, `contact.html`, 각 페이지 푸터
- **제품 이미지:** `assets/images/products/panasonic/` (파일명 고정, push 필수)
- **갤러리:** 제품 페이지 하단 「실제 설비 및 적용 이미지」
- **인증·구축사례:** 아직 이미지 슬롯이 비어 있을 수 있음 → `docs/HANDOVER.md` 참고

## 디자인 방향

- 메인 컬러: 네이비, 블루, 화이트, 그레이
- 과한 애니메이션·광고 문구 배제
- 반응형: 모바일 네비게이션 토글
