/**
 * 세한메카트로닉스 — 산업전시회 및 로봇 시연 영상 데이터
 * ============================================================
 * 새로운 동영상이 생길 때마다 아래 배열(SAEHAN_VIDEOS) 맨 위에 항목을 하나씩 추가하거나,
 * `video-manager.html` (동영상 등록 도우미) 파일에서 쉽게 추가·저장할 수 있습니다.
 *
 * [지원하는 동영상 주소(videoUrl) 형식 3가지]
 * 1) 직접 파일 넣기 (소용량 50MB 이하 MP4 권장):
 *    "assets/videos/파일명.mp4"
 * 2) 유튜브(YouTube) 무료 무제한 업로드 (가장 추천 · 용량 무제한):
 *    "https://youtu.be/영상ID" 또는 "https://www.youtube.com/watch?v=영상ID"
 *    (유튜브 업로드 시 '일부 공개'로 설정하면 유튜브 검색에는 안 나오고 홈페이지에서만 깔끔하게 재생됩니다)
 * 3) 구글 드라이브 / GitHub Releases 무료 대용량 직링크:
 *    "https://drive.google.com/file/d/파일ID/view?usp=sharing"
 *    또는 "https://github.com/jwonrt-beep/sehan/releases/download/videos/파일명.mp4"
 */

window.SAEHAN_VIDEO_CATEGORIES = [
  { id: "all", label: "전체 영상" },
  { id: "exhibition", label: "산업전시회" },
  { id: "welding", label: "로봇 용접 시연" },
  { id: "handling", label: "자동 이송 · 조립" },
  { id: "simulation", label: "3D 시뮬레이션" }
];

window.SAEHAN_VIDEOS = [
  {
    id: "exhibit-panasonic-welding-01",
    category: "exhibition",
    categoryLabel: "산업전시회",
    title: "파나소닉 용접 로봇 시스템 전시회 라이브 시연",
    date: "산업전시회 출품",
    description: "Panasonic TM/TL 시리즈 기반 Full Digital 아크 용접 및 포지셔너 동기 제어 전시회 현장 구동 영상입니다.",
    videoUrl: "assets/videos/exhibition-01.mp4",
    thumbnail: "assets/images/products/panasonic/gallery/facility-01.jpg",
    featured: true
  },
  {
    id: "exhibit-multi-robot-02",
    category: "welding",
    categoryLabel: "로봇 용접 시연",
    title: "멀티 로봇 동시 용접 및 포지셔너 연동 시스템",
    date: "현장 시연 · 전시",
    description: "2대 이상의 용접 로봇과 외부축 포지셔너가 동기화되어 대형 워크를 고속·고품질로 용접하는 시연 영상입니다.",
    videoUrl: "assets/videos/exhibition-02.mp4",
    thumbnail: "assets/images/products/panasonic/gallery/facility-02.jpg",
    featured: true
  },
  {
    id: "exhibit-handling-03",
    category: "handling",
    categoryLabel: "자동 이송 · 조립",
    title: "자동 이송 · 적재(팔레타이징) 및 공정 자동화 시연",
    date: "공정 자동화",
    description: "용접 공정 전후 물류 이송, 자동 적재 및 핸들링 로봇 시스템 통합 구동 영상입니다.",
    videoUrl: "assets/videos/exhibition-03.mp4",
    thumbnail: "assets/images/products/panasonic/gallery/facility-03.jpg",
    featured: true
  },
  {
    id: "exhibit-simulation-04",
    category: "simulation",
    categoryLabel: "3D 시뮬레이션",
    title: "도입 전 3D 로봇 동작 · 사이클 타임 시뮬레이션 검증",
    date: "사전 시뮬레이션",
    description: "설비 제작 전 지그 간섭 여부, 로봇 작업 반경 및 최적 사이클 타임을 3D로 사전 검증하는 영상입니다.",
    videoUrl: "assets/videos/exhibition-04.mp4",
    thumbnail: "assets/images/products/panasonic/gallery/facility-04.jpg",
    featured: false
  }
];
