# 세한메카트로닉스 홈페이지 인수인계

안녕하세요.  
세한메카트로닉스 홈페이지 관리를 **앞으로 맡아주실 분**께 전달드립니다.

아래만 따라 하시면 됩니다.

---

## 먼저 이것만 기억해 주세요

| 항목 | 내용 |
|------|------|
| 홈페이지 | https://www.shm21.kr |
| 코드 저장소 | https://github.com/jwonrt-beep/sehan |
| 반영 방식 | 파일을 고친 뒤 GitHub에 올리면(push), **자동으로** 홈페이지에 반영됩니다 |

로컬 컴퓨터에만 저장하고 GitHub에 올리지 않으면, 실제 사이트에는 안 보입니다.

---

## 1. 당신에게 필요한 준비

1. https://github.com 에서 **무료 계정**을 만드세요. (이미 있으면 그대로 사용)
2. 본인 **GitHub 아이디** 또는 **가입 이메일**을 제게 알려 주세요.
3. 제가 저장소에 **초대**를 보내면, 그 초대를 **수락**해 주세요.

비밀번호나 주민번호 같은 건 필요 없습니다.  
**GitHub 계정**만 있으면 됩니다.

---

## 2. 권한 받는 방법 (초대 수락)

제가 Collaborator 초대를 보낸 뒤:

1. GitHub에 가입한 **이메일**을 확인하거나  
2. https://github.com/jwonrt-beep/sehan 에 들어갔을 때 뜨는 **초대 안내**에서  
3. **Accept invitation (수락)** 을 누르세요.

수락이 끝나면 저장소가 열리고, 그때부터 수정·업로드가 가능합니다.

### 초대가 안 보이면

- GitHub에 **초대한 이메일과 같은 계정**으로 로그인했는지 확인해 주세요.
- 스팸함을 확인해 주세요.
- 그래도 없으면 제게 “초대 다시 보내 달라”고 말씀해 주세요.

---

## 3. 제가 해 드릴 일 / 당신이 해 주실 일

### 제가 하는 일
- 저장소에 당신을 Collaborator로 초대 (Write 또는 Admin)
- (전권일 경우) 도메인 `www.shm21.kr` 관리 계정도 별도 전달
- 질문이 있으면 인수인계 기간 동안 안내

### 당신이 하는 일
- GitHub 가입 → 아이디를 제게 알려주기
- 초대 수락
- 이후 홈페이지 수정·이미지 추가·push

---

## 4. 사이트는 이렇게 고칩니다

```
1. 파일 수정 또는 이미지 추가
2. GitHub main 브랜치에 push
3. 1~3분 뒤 https://www.shm21.kr 에 반영
```

GitHub 사이트에서 **Actions** 메뉴를 보면 배포가 성공했는지 확인할 수 있습니다.

---

## 5. 자주 고치는 파일

| 목적 | 파일 |
|------|------|
| 메인 | `index.html` |
| 제품·설비 사진 | `products.html` + `assets/images/products/panasonic/` |
| 주소·전화 | `locations.html`, 각 페이지 하단(푸터) |
| 문의 | `contact.html` |
| 회사소개 | `company.html` |
| 인증 | `certifications.html` |
| 구축사례 | `cases.html` |
| 공통 디자인 | `css/style.css` |
| 제품 페이지 디자인 | `css/products.css` |

연락처를 바꾸실 때는 **locations.html / contact.html**과 **각 페이지 푸터**를 함께 확인해 주세요.

---

## 6. 제품·갤러리 사진

### 사이트에서 보는 위치
메뉴 **「제품 및 시스템」** → 페이지를 **맨 아래까지** 스크롤  
→ **「실제 설비 및 적용 이미지」** 가 갤러리입니다.

### 파일을 넣는 위치
`assets/images/products/panasonic/`

```
hero.jpg
ts-tm-tl-series.jpg
system-configuration.jpg
co2-mag-mig-system.jpg
tig-system.jpg
positioner-external-axis.jpg
large-multi-robot.jpg
g3-controller-pendant.jpg
remote-tp-viewer.jpg
gallery/
  facility-01.jpg ~ facility-06.jpg
```

**파일 이름을 바꾸면 화면에 안 나옵니다.**  
이미지를 넣은 뒤에는 꼭 GitHub에 push 해 주세요.

---

## 7. 아직 비어 있을 수 있는 이미지

나중에 넣으시면 됩니다.

- 메인: `images/hero-robot.jpg`
- 구축사례(`cases.html`): 시뮬레이션/사례 사진
- 인증(`certifications.html`): 인증서 스캔
- 사업장(`locations.html`): 시설/외관 사진

---

## 8. 도메인(주소)까지 맡으실 경우

GitHub 권한만 있으면 **내용 수정·배포**는 가능합니다.  
`www.shm21.kr` **주소·DNS**까지 관리하시려면, 제가 **도메인 등록 업체 계정**도 함께 전달드리겠습니다.

도메인을 잘못 건드리면 사이트가 안 열릴 수 있으니, DNS 변경 전에는 설정을 캡처해 두시는 걸 권장합니다.

---

## 9. 시작 체크리스트 (당신용)

- [ ] GitHub 가입 완료
- [ ] 아이디/이메일을 제게 전달
- [ ] 초대 수락 완료
- [ ] 저장소가 열리는지 확인
- [ ] 작은 수정 후 push 테스트
- [ ] https://www.shm21.kr 반영 확인
- [ ] (전권) 도메인 로그인 확인

---

궁금한 점이 있으면 편하게 물어봐 주세요.  
이 파일(`docs/HANDOVER.md`)만 보셔도 기본 운영은 가능합니다.
