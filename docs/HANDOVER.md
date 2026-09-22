# 세한메카트로닉스 홈페이지 — 인수인계 안내

이 문서는 **다음 관리자**가 바로 이어받을 수 있도록 쉽게 정리한 것입니다.

---

## 한 줄 요약

이 홈페이지는 **GitHub에 코드를 올리고 → 자동으로 www.shm21.kr 에 반영**되는 방식입니다.  
수정하려면 **GitHub 저장소 권한**이 필요하고, 도메인까지 관리하려면 **도메인 계정**도 필요합니다.

---

## 1. 새 관리자가 꼭 받아야 할 것

### A. 계정·권한 (전권에 필요)

| 무엇을 | 왜 필요한지 | 지금 담당자가 할 일 |
|--------|-------------|---------------------|
| **GitHub 저장소 권한** | 글·사진 수정 후 홈페이지에 반영 | 아래 저장소에 Admin 또는 Write 초대 |
| **도메인 계정** | www.shm21.kr 주소 유지·DNS 변경 | 도메인 등록 업체 로그인 정보 전달 |
| **DNS 접근** | GitHub Pages와 도메인 연결 | 도메인 계정에서 DNS 설정 가능해야 함 |

**저장소 주소**
- https://github.com/jwonrt-beep/sehan

**홈페이지 주소**
- https://www.shm21.kr

### B. 자료 (있으면 함께)

- 제품·설비·인증서·사업장 사진 원본
- 카탈로그 PDF 원본 (`downloads/catalog.pdf` 로 올려 둠)
- 회사 연락처·주소가 바뀌면 알려줄 최신 정보

---

## 2. 이 사이트는 어떻게 동작하나요?

```
1. 컴퓨터에서 HTML / 이미지 수정
2. GitHub에 push (업로드)
3. GitHub Actions가 자동으로 배포
4. 1~3분 뒤 www.shm21.kr 에 반영
```

⚠️ **로컬 폴더에만 이미지를 넣고 push 안 하면, 홈페이지에는 안 보입니다.**  
(예전에 갤러리 404가 난 이유가 이것입니다.)

---

## 3. 수정은 어디에 하나요?

| 바꾸고 싶은 것 | 여는 파일 |
|----------------|-----------|
| 메인 화면 | `index.html` |
| 회사소개 | `company.html` |
| 사업영역 | `business.html` |
| **제품·설비 사진** | `products.html` + 아래 이미지 폴더 |
| 스마트팩토리 | `smartfactory.html` |
| 구축사례 | `cases.html` |
| 인증서 | `certifications.html` |
| 사업장·주소·전화 | `locations.html` |
| 문의 폼 | `contact.html` |
| 공통 디자인 | `css/style.css` |
| 제품 페이지 디자인 | `css/products.css` |

모든 페이지 하단(푸터)에도 회사명·전화·이메일이 있습니다.  
연락처를 바꾸면 **각 페이지 푸터**와 **locations.html / contact.html**을 함께 확인하세요.

---

## 4. 제품 이미지 (어디 넣고, 어디서 보나)

### 보는 곳
메뉴 **「제품 및 시스템」** → 페이지를 아래로 스크롤  
→ **「실제 설비 및 적용 이미지」** 가 갤러리입니다.

### 넣는 곳 (파일명 그대로)

```
assets/images/products/panasonic/
├── hero.jpg                         ← 상단 큰 사진
├── ts-tm-tl-series.jpg              ← 로봇 라인업
├── system-configuration.jpg         ← 시스템 구성도
├── co2-mag-mig-system.jpg
├── tig-system.jpg
├── positioner-external-axis.jpg
├── large-multi-robot.jpg
├── g3-controller-pendant.jpg
├── remote-tp-viewer.jpg
└── gallery/
    ├── facility-01.jpg
    ├── facility-02.jpg
    ├── facility-03.jpg
    ├── facility-04.jpg
    ├── facility-05.jpg
    └── facility-06.jpg
```

파일 이름을 바꾸면 화면에 안 나옵니다.  
이미지가 없으면 깨진 아이콘 대신 **그 칸만 자동으로 숨깁니다.**

---

## 5. 아직 비어 있는 이미지 (나중에 넣으면 좋음)

| 페이지 | 필요한 것 |
|--------|-----------|
| 메인 (`index.html`) | `images/hero-robot.jpg` |
| 구축사례 (`cases.html`) | 시뮬레이션/사례 사진 4곳 (지금은 텍스트만) |
| 인증 (`certifications.html`) | 인증서 스캔 이미지 7곳 |
| 사업장 (`locations.html`) | 시흥·천안 외관/시설 사진 |

---

## 6. 배포하는 방법 (가장 쉬운 흐름)

### Cursor / VS Code + Git 을 쓰는 경우
1. 파일 수정 또는 이미지 추가
2. 변경 사항 커밋
3. `main` 브랜치에 push
4. GitHub → Actions 메뉴에서 Deploy 성공 확인
5. 사이트 새로고침 (필요하면 강력 새로고침)

### 명령어 예시
```bash
git add .
git commit -m "수정 내용 간단히 적기"
git push origin main
```

---

## 7. 인수인계 체크리스트

새 관리자가 직접 확인:

- [ ] GitHub 저장소 clone / push 가능
- [ ] `main` push 후 Actions 배포 성공
- [ ] https://www.shm21.kr 접속 확인
- [ ] 제품 페이지·갤러리 사진 보임
- [ ] 도메인 DNS 변경 가능 (전권일 때)
- [ ] 연락처·주소 수정 위치 파악 (`locations.html`, 푸터)

---

## 8. 관련 문서

- `README.md` — 사이트 구조 요약
- `docs/SITE_PLAN.md` — 초기 기획·사이트맵
- `docs/HANDOVER_MESSAGE.txt` — 카톡/메일로 그대로 붙여넣을 짧은 문구
- `.github/workflows/deploy.yml` — 자동 배포 설정

---

## 9. 자주 하는 실수

1. **이미지만 폴더에 넣고 push 안 함** → 사이트에 안 보임  
2. **파일명 오타** (예: `facility-2.jpg` vs `facility-02.jpg`) → 안 보임  
3. **잘못된 폴더**에 넣음 (예: `assets/images/products/` 에만 넣고 `panasonic/` 아래가 아님)  
4. **헤더「세한통상」** — 의도적으로 제거해 두었음. 다시 넣지 않아도 됨  

---

문의·인수인계 시 이 파일(`docs/HANDOVER.md`)만 전달해도 기본은 충분합니다.  
**전권**을 넘기려면 반드시 **GitHub 권한 + 도메인 계정**을 함께 넘겨 주세요.
