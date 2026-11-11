/**
 * 세한메카트로닉스 — 산업전시회 및 로봇 시연 영상 데이터 (F:\전시회 실제 영상 12종 탑재)
 * ============================================================
 * 새로운 동영상이 생길 때마다 아래 배열(SAEHAN_VIDEOS) 맨 위에 항목을 하나씩 추가하거나,
 * `video-manager.html` (동영상 등록 도우미) 파일에서 쉽게 추가·저장할 수 있습니다.
 *
 * [지원하는 동영상 주소(videoUrl) 형식 3가지]
 * 1) 직접 파일 넣기 (소용량 50MB 이하 H.264 MP4 권장):
 *    "assets/videos/파일명.mp4"
 * 2) 유튜브(YouTube) 무료 무제한 업로드 (100MB 이상 대용량 영상에 가장 추천 · 용량 무제한):
 *    "https://youtu.be/영상ID" 또는 "https://www.youtube.com/watch?v=영상ID"
 *    (유튜브 업로드 시 '일부 공개'로 설정하면 유튜브 검색에는 안 나오고 홈페이지에서만 깔끔하게 재생됩니다)
 * 3) 구글 드라이브 / GitHub Releases 무료 대용량 직링크:
 *    "https://drive.google.com/file/d/파일ID/view?usp=sharing"
 *    또는 "https://github.com/jwonrt-beep/sehan/releases/download/videos/파일명.mp4"
 */

window.SAEHAN_VIDEO_CATEGORIES = [
  { id: "all", label: "전체 영상 (12)" },
  { id: "exhibition", label: "산업전시회 · 기업홍보" },
  { id: "welding", label: "로봇 용접 시연" },
  { id: "handling", label: "자동 이송 · 핸들링 · 컷팅" }
];

window.SAEHAN_VIDEOS = [
  {
    id: "exhibit-company-intro",
    category: "exhibition",
    categoryLabel: "산업전시회 · 기업홍보",
    title: "[금속산업대전] 세한메카트로닉스 기업 및 파나소닉 용접로봇 소개",
    date: "금속산업대전 출품",
    description: "금속산업대전 전시회 현장에서 소개된 (주)세한메카트로닉스의 파나소닉 산업용 로봇 자동화 시스템 및 레이저·용접 기술 인터뷰 영상입니다.",
    videoUrl: "assets/videos/exhibit-company-intro.mp4",
    thumbnail: "assets/videos/thumbs/exhibit-company-intro.jpg",
    featured: true
  },
  {
    id: "panasonic-full-digital",
    category: "exhibition",
    categoryLabel: "산업전시회 · 신기술",
    title: "Panasonic Global Full Digital 용접 로봇 시스템",
    date: "Full Digital 시리즈",
    description: "용접 전원부와 로봇 컨트롤러가 하나로 융합된 파나소닉 글로벌 풀 디지털(Full Digital) 용접 로봇 시스템 시연 영상입니다.",
    videoUrl: "assets/videos/panasonic-full-digital.mp4",
    thumbnail: "assets/videos/thumbs/panasonic-full-digital.jpg",
    featured: true
  },
  {
    id: "panasonic-super-active",
    category: "exhibition",
    categoryLabel: "산업전시회 · 신기술",
    title: "Panasonic Super Active (Slag-less) 초저스패터 용접 기술",
    date: "Super Active 기술",
    description: "와이어 송급 제어와 디지털 파형 제어를 결합해 스패터와 슬래그를 획기적으로 줄인 Super Active 용접 시연 영상입니다.",
    videoUrl: "assets/videos/panasonic-super-active.mp4",
    thumbnail: "assets/videos/thumbs/panasonic-super-active.jpg",
    featured: true
  },
  {
    id: "welding-sawp-sus-mig",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "S-AWP 스테인리스(SUS) MIG 로봇 용접 시연",
    date: "SUS-MIG 공정",
    description: "스테인리스(SUS) 소재에 최적화된 S-AWP MIG 로봇 용접 실제 아크 및 비드 형성 구동 영상입니다.",
    videoUrl: "assets/videos/welding-sawp-sus-mig.mp4",
    thumbnail: "assets/videos/thumbs/welding-sawp-sus-mig.jpg",
    featured: false
  },
  {
    id: "welding-laser-robot",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "산업용 로봇 레이저 용접 자동화 시연",
    date: "레이저 용접",
    description: "고속·고정밀 로봇 경로 제어를 통한 산업용 레이저 용접 시연 영상입니다.",
    videoUrl: "assets/videos/welding-laser-robot.mp4",
    thumbnail: "assets/videos/thumbs/welding-laser-robot.jpg",
    featured: false
  },
  {
    id: "welding-touch-sensing",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "터치센싱(Touch Sensing) 기반 용접선 자동 보정 시연",
    date: "터치센싱 적용",
    description: "용접 전 와이어 터치센싱으로 워크의 위치 오차를 자동 감지·보정하여 정밀 용접을 수행하는 현장 영상입니다.",
    videoUrl: "assets/videos/welding-touch-sensing.mp4",
    thumbnail: "assets/videos/thumbs/welding-touch-sensing.jpg",
    featured: false
  },
  {
    id: "welding-sync-rotation",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "자동차 부품 11자형 지그 협조회전 로봇 용접",
    date: "포지셔너 협조제어",
    description: "11자형 회전 지그(포지셔너)와 로봇이 동기 회전하며 자동차 부품을 연속 용접하는 구축 사례 영상입니다.",
    videoUrl: "assets/videos/welding-sync-rotation.mp4",
    thumbnail: "assets/videos/thumbs/welding-sync-rotation.jpg",
    featured: false
  },
  {
    id: "welding-sus-mig-case",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "SUS-MIG 로봇 용접 현장 양산 라인 구축 사례",
    date: "현장 양산 적용",
    description: "전용 지그와 집진 부스가 결합된 SUS-MIG 로봇 용접 양산 설비 가동 영상입니다.",
    videoUrl: "assets/videos/welding-sus-mig-case.mp4",
    thumbnail: "assets/videos/thumbs/welding-sus-mig-case.jpg",
    featured: false
  },
  {
    id: "handling-press-transfer",
    category: "handling",
    categoryLabel: "자동 이송 · 핸들링",
    title: "프레스 공정 자동 이송 · 로딩 로봇 시스템",
    date: "프레스 자동화",
    description: "프레스 설비와 연동하여 소재 투입 및 배출을 고속으로 자동화한 핸들링 로봇 가동 영상입니다.",
    videoUrl: "assets/videos/handling-press-transfer.mp4",
    thumbnail: "assets/videos/thumbs/handling-press-transfer.jpg",
    featured: false
  },
  {
    id: "handling-cnc-automation",
    category: "handling",
    categoryLabel: "자동 이송 · 핸들링",
    title: "CNC 가공기 2대 연동 로봇 핸들링 자동화 (2대 1기종)",
    date: "공작기계 텐딩",
    description: "1대의 로봇이 2대의 CNC 가공기에 공작물을 자동으로 탈·부착하는 무인 가공 자동화 사례입니다.",
    videoUrl: "assets/videos/handling-cnc-automation.mp4",
    thumbnail: "assets/videos/thumbs/handling-cnc-automation.jpg",
    featured: false
  },
  {
    id: "handling-palletizing",
    category: "handling",
    categoryLabel: "자동 이송 · 적재",
    title: "중량 포대 자동 적재(팔레타이징) 로봇 시스템",
    date: "팔레타이징",
    description: "컨베이어로 이송되는 사료·원료 포대를 전용 그리퍼로 파지하여 팔레트에 고속 정렬 적재하는 시스템입니다.",
    videoUrl: "assets/videos/handling-palletizing.mp4",
    thumbnail: "assets/videos/thumbs/handling-palletizing.jpg",
    featured: false
  },
  {
    id: "handling-plasma-cutting",
    category: "handling",
    categoryLabel: "플라즈마 컷팅 자동화",
    title: "PLC 및 터치센서 연동 로봇 플라즈마 컷팅 자동화",
    date: "플라즈마 절단",
    description: "터치센서 위치 감지 후 로봇이 3차원 궤적을 따라 정밀 플라즈마 절단(Cutting)을 수행하는 시연 영상입니다.",
    videoUrl: "assets/videos/handling-plasma-cutting.mp4",
    thumbnail: "assets/videos/thumbs/handling-plasma-cutting.jpg",
    featured: false
  }
];
