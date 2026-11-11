/**
 * 세한메카트로닉스 — 동영상 갤러리 및 모달 플레이어 스크립트
 */
(function () {
  "use strict";

  function parseVideoSource(url) {
    if (!url || typeof url !== "string") {
      return { type: "none", src: "" };
    }
    const trimmed = url.trim();

    // 1. YouTube URL detection (watch?v=, youtu.be/, embed/, shorts/)
    const ytMatch = trimmed.match(
      /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
    );
    if (ytMatch && ytMatch[1]) {
      return {
        type: "youtube",
        id: ytMatch[1],
        src: "https://www.youtube.com/embed/" + ytMatch[1] + "?autoplay=1&rel=0",
        thumb: "https://img.youtube.com/vi/" + ytMatch[1] + "/hqdefault.jpg"
      };
    }

    // 2. Google Drive sharing link detection
    const driveMatch = trimmed.match(/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/);
    if (driveMatch && driveMatch[1]) {
      return {
        type: "gdrive",
        id: driveMatch[1],
        src: "https://drive.google.com/file/d/" + driveMatch[1] + "/preview"
      };
    }

    // 3. Direct video file (.mp4, .webm, .mov, or GitHub Releases download link)
    return {
      type: "mp4",
      src: trimmed
    };
  }

  function createVideoCardHTML(item) {
    const parsed = parseVideoSource(item.videoUrl);
    const thumbUrl = item.thumbnail || parsed.thumb || "assets/images/products/panasonic/hero.jpg";
    const badgeText = item.categoryLabel || "전시회 영상";
    const dateText = item.date || "";

    return (
      '<article class="video-card" data-category="' +
      (item.category || "exhibition") +
      '" data-video-id="' +
      item.id +
      '" tabindex="0" role="button" aria-label="' +
      item.title +
      ' 영상 재생">' +
      '  <div class="video-thumb-wrap">' +
      '    <img src="' +
      thumbUrl +
      '" alt="' +
      item.title +
      '" class="video-thumb-img" loading="lazy" onerror="this.style.opacity=\'0.15\'">' +
      '    <div class="video-thumb-overlay">' +
      '      <span class="video-badge">' +
      badgeText +
      "</span>" +
      '      <div class="video-play-circle" aria-hidden="true">' +
      '        <svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor"><path d="M8 5.14v14l11-7-11-7z"/></svg>' +
      "      </div>" +
      (dateText ? '<span class="video-date-tag">' + dateText + "</span>" : "") +
      "    </div>" +
      "  </div>" +
      '  <div class="video-card-body">' +
      '    <h3 class="video-card-title">' +
      item.title +
      "</h3>" +
      '    <p class="video-card-desc">' +
      (item.description || "") +
      "</p>" +
      '    <span class="video-card-action">영상 재생하기 →</span>' +
      "  </div>" +
      "</article>"
    );
  }

  function ensureModalExists() {
    let modal = document.getElementById("sehan-video-modal");
    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "sehan-video-modal";
    modal.className = "video-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.innerHTML =
      '<div class="video-modal-backdrop" data-close-modal="true"></div>' +
      '<div class="video-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="video-modal-title">' +
      '  <div class="video-modal-header">' +
      '    <div>' +
      '      <span class="video-modal-badge" id="video-modal-badge">산업전시회</span>' +
      '      <h3 class="video-modal-title" id="video-modal-title">영상 제목</h3>' +
      "    </div>" +
      '    <button type="button" class="video-modal-close" data-close-modal="true" aria-label="닫기">✕</button>' +
      "  </div>" +
      '  <div class="video-modal-stage" id="video-modal-stage"></div>' +
      '  <div class="video-modal-footer">' +
      '    <p id="video-modal-desc" class="video-modal-desc"></p>' +
      "  </div>" +
      "</div>";

    document.body.appendChild(modal);

    modal.addEventListener("click", function (e) {
      if (e.target && e.target.getAttribute("data-close-modal") === "true") {
        closeVideoModal();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.classList.contains("open")) {
        closeVideoModal();
      }
    });

    return modal;
  }

  function openVideoModal(item) {
    const modal = ensureModalExists();
    const stage = document.getElementById("video-modal-stage");
    const titleEl = document.getElementById("video-modal-title");
    const badgeEl = document.getElementById("video-modal-badge");
    const descEl = document.getElementById("video-modal-desc");

    titleEl.textContent = item.title || "전시회 시연 영상";
    badgeEl.textContent = item.categoryLabel || "산업전시회";
    descEl.textContent = item.description || "";

    const parsed = parseVideoSource(item.videoUrl);

    if (parsed.type === "youtube" || parsed.type === "gdrive") {
      stage.innerHTML =
        '<iframe class="video-modal-iframe" src="' +
        parsed.src +
        '" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
    } else if (parsed.type === "mp4" && parsed.src) {
      stage.innerHTML =
        '<video class="video-modal-player" controls autoplay playsinline preload="metadata" poster="' +
        (item.thumbnail || "") +
        '">' +
        '  <source src="' +
        parsed.src +
        '" type="video/mp4">' +
        "</video>";

      const videoEl = stage.querySelector("video");
      const sourceEl = stage.querySelector("source");
      const showGuide = function () {
        stage.innerHTML =
          '<div class="video-missing-guide">' +
          '  <div class="guide-icon">🎬</div>' +
          '  <h4>동영상 파일 준비 안내</h4>' +
          '  <p>현재 연결된 동영상 경로: <code>' +
          parsed.src +
          "</code></p>" +
          '  <div class="guide-steps">' +
          '    <p><strong>방법 1 (폴더에 직접 넣기):</strong> 컴퓨터의 <code>assets/videos/</code> 폴더 안에 위 파일 이름으로 MP4 동영상을 넣으면 즉시 재생됩니다.</p>' +
          '    <p><strong>방법 2 (유튜브 무제한 무료 연동):</strong> 유튜브에 영상을 올린 뒤 <code>video-manager.html</code> 또는 <code>js/videos-data.js</code>에 유튜브 링크만 붙여넣으면 용량 제한 없이 재생됩니다.</p>' +
          "  </div>" +
          "</div>";
      };
      if (sourceEl) sourceEl.addEventListener("error", showGuide);
      if (videoEl) videoEl.addEventListener("error", showGuide);
    }

    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeVideoModal() {
    const modal = document.getElementById("sehan-video-modal");
    if (!modal) return;
    const stage = document.getElementById("video-modal-stage");
    if (stage) stage.innerHTML = "";
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function bindCardEvents(container, videos) {
    const cards = container.querySelectorAll(".video-card");
    cards.forEach(function (card) {
      const id = card.getAttribute("data-video-id");
      const item = videos.find(function (v) {
        return v.id === id;
      });
      if (!item) return;

      card.addEventListener("click", function () {
        openVideoModal(item);
      });
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openVideoModal(item);
        }
      });
    });
  }

  function initGallery() {
    const videos = window.SAEHAN_VIDEOS || [];
    const categories = window.SAEHAN_VIDEO_CATEGORIES || [];

    // 1. Full Gallery on cases.html (#exhibition-video-grid)
    const fullGrid = document.getElementById("exhibition-video-grid");
    const filterContainer = document.getElementById("exhibition-video-filters");

    if (fullGrid) {
      if (filterContainer && categories.length > 0) {
        filterContainer.innerHTML = categories
          .map(function (cat, idx) {
            return (
              '<button type="button" class="video-filter-btn' +
              (idx === 0 ? " active" : "") +
              '" data-filter="' +
              cat.id +
              '">' +
              cat.label +
              "</button>"
            );
          })
          .join("");

        filterContainer.addEventListener("click", function (e) {
          const btn = e.target.closest(".video-filter-btn");
          if (!btn) return;
          const filter = btn.getAttribute("data-filter");

          filterContainer.querySelectorAll(".video-filter-btn").forEach(function (b) {
            b.classList.toggle("active", b === btn);
          });

          const filtered =
            filter === "all"
              ? videos
              : videos.filter(function (v) {
                  return v.category === filter;
                });

          fullGrid.innerHTML = filtered.map(createVideoCardHTML).join("");
          bindCardEvents(fullGrid, videos);
        });
      }

      fullGrid.innerHTML = videos.map(createVideoCardHTML).join("");
      bindCardEvents(fullGrid, videos);
    }

    // 2. Featured Gallery on index.html (#home-video-grid)
    const homeGrid = document.getElementById("home-video-grid");
    if (homeGrid) {
      const featured = videos.filter(function (v) {
        return v.featured !== false;
      }).slice(0, 3);
      homeGrid.innerHTML = featured.map(createVideoCardHTML).join("");
      bindCardEvents(homeGrid, videos);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGallery);
  } else {
    initGallery();
  }
})();
