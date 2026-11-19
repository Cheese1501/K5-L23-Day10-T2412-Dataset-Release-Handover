"use strict";

let state;
let dirty = false;
const drafts = new Map();
const byId = (id) => document.getElementById(id);
const typeLabels = {
  class_swap: "class_swap · Detection ghi sai lớp",
  category_swap: "category_swap · Panoptic ghi sai lớp",
  bbox_drift: "bbox_drift · Box lệch khỏi vật",
  missing_box: "missing_box · Thiếu box detection",
  instance_merge: "instance_merge · Panoptic gộp hai vật"
};

function notice(message, error = false) {
  byId("notice").textContent = message;
  byId("notice").classList.toggle("error", error);
}

async function api(path, body) {
  const options = body === undefined ? {} : {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-Review-Token": state.token},
    body: JSON.stringify(body)
  };
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Không thực hiện được yêu cầu.");
  return result;
}

function option(value, label) {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

function drawBox(viewer, bbox, width, height, category) {
  const box = document.createElement("span");
  box.className = "box " + category;
  const [x, y, w, h] = bbox;
  Object.assign(box.style, {
    left: x / width * 100 + "%", top: y / height * 100 + "%",
    width: w / width * 100 + "%", height: h / height * 100 + "%"
  });
  viewer.append(box);
}

function renderCase(item, isHash) {
  const article = document.createElement("article");
  article.className = "case";
  article.innerHTML = `
    <div class="case-head">
      <div class="line"><h2></h2><span class="saved"></span></div><p class="summary"></p>
    </div>
    <div class="case-body">
      <div class="visual">
        <p class="legend"></p>
        <div class="controls"></div>
        <div class="viewer"></div>
        <div class="image-actions"></div>
      </div>
      <form class="review-form">
        <label><span>Loại lỗi</span><select class="kind"></select></label>
        <label><span>Kết luận của người xem</span><select class="verdict" required></select></label>
        <label>Điều bạn trực tiếp nhìn thấy
          <textarea class="note" minlength="20" required placeholder="Mô tả vật, vị trí và chi tiết giúp bạn kết luận…"></textarea>
          <small>Tối thiểu 20 ký tự. Tên người đang xem được lưu cùng ghi chú.</small>
        </label>
        <label class="seen"><input type="checkbox" required> Tôi đã trực tiếp mở và xem ảnh này.</label>
        <button class="primary" type="submit">Lưu kết quả xem ảnh</button>
      </form>
    </div>`;
  article.querySelector("h2").textContent = item.image + (isHash ? " · Kiểm hash" : "");
  const review = item.review;
  const viewerPrefix = byId("reviewer").value + " — ";
  const otherReviewer = review && (isHash
    ? review.reviewer && !review.reviewer.startsWith(viewerPrefix)
    : review.verdict && !review.note.startsWith(viewerPrefix));
  const saved = review && (isHash ? review.status : review.verdict);
  article.querySelector(".saved").textContent = saved ? "Đã có kết quả · " + saved : "Chờ người xem";
  article.querySelector(".summary").textContent = isHash
    ? "Mở ảnh, kiểm nội dung có nguyên vẹn và ghi lại quan sát."
    : item.reason + " · " + (item.owner || "TV4 phân công")
      + (item.cross ? " · xem chéo " + item.cross : "");
  const viewer = article.querySelector(".viewer");
  const image = document.createElement("img");
  image.src = "/asset/image?id=" + encodeURIComponent(item.image);
  image.alt = "Ảnh " + item.image;
  image.addEventListener("error", () => notice("Không tải được ảnh " + item.image + ".", true));
  viewer.append(image);
  const actions = article.querySelector(".image-actions");
  const original = document.createElement("a");
  original.href = image.src;
  original.target = "_blank";
  original.rel = "noopener";
  original.textContent = "Phóng to ảnh gốc";
  actions.append(original);
  if (!isHash) {
    article.querySelector(".legend").textContent =
      "Detection cam · " + (item.detection.map(d => d.class).join(", ") || "thiếu box tương ứng")
      + "  /  Panoptic xanh · " + item.panoptic.class;
    const mask = document.createElement("img");
    mask.className = "mask";
    mask.src = "/asset/mask?id=" + encodeURIComponent(item.image);
    mask.alt = "";
    mask.hidden = true;
    viewer.append(mask);
    drawBox(viewer, item.panoptic.bbox, item.width, item.height, "pan");
    for (const box of item.detection) drawBox(viewer, box.bbox, item.width, item.height, "det");
    const toggle = document.createElement("label");
    toggle.innerHTML = '<input type="checkbox"> Chồng mask lên ảnh';
    toggle.querySelector("input").addEventListener("change", (event) => mask.hidden = !event.target.checked);
    article.querySelector(".controls").append(toggle);
    const maskLink = document.createElement("a");
    maskLink.href = mask.src;
    maskLink.target = "_blank";
    maskLink.rel = "noopener";
    maskLink.textContent = "Mở mask";
    actions.append(maskLink);
  } else {
    article.querySelector(".legend").textContent = "Ảnh lệch SHA-256 theo rules.json.";
  }

  const form = article.querySelector("form");
  const draftKey = isHash ? "hash|" + item.image : item.key;
  const kind = form.querySelector(".kind");
  if (isHash) {
    kind.closest("label").hidden = true;
  } else {
    for (const type of item.possible_types) kind.append(option(type, typeLabels[type] || type));
    if (review) kind.value = review.type;
  }
  const verdict = form.querySelector(".verdict");
  verdict.append(option("", "Chọn sau khi xem ảnh"));
  if (isHash) {
    verdict.append(option("intact", "Ảnh nguyên vẹn, nội dung hợp lệ"));
    verdict.append(option("damaged", "Ảnh hỏng, cần đưa vào rework"));
  } else {
    verdict.append(option("confirmed", "Xác nhận loại lỗi đã chọn"));
    verdict.append(option("rejected", "Bác bỏ ứng viên, ghi rõ lý do"));
  }
  if (review && !otherReviewer) {
    verdict.value = isHash ? review.status : review.verdict;
    form.querySelector(".note").value = isHash ? review.note : review.note.replace(/^TV\d+ — .*? · /, "");
  }
  if (otherReviewer) {
    const previous = document.createElement("p");
    previous.className = "muted";
    previous.textContent = "Ghi chú đã lưu · " + review.note;
    form.prepend(previous);
  }
  const draft = drafts.get(draftKey);
  if (draft) {
    kind.value = draft.type;
    verdict.value = draft.verdict;
    form.querySelector(".note").value = draft.note;
    form.querySelector(".seen input").checked = draft.seen;
  }
  form.addEventListener("input", () => {
    drafts.set(draftKey, {
      type: kind.value, verdict: verdict.value,
      note: form.querySelector(".note").value,
      seen: form.querySelector(".seen input").checked
    });
    dirty = true;
    byId("merge").disabled = true;
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (otherReviewer && !window.confirm("Đã có kết quả của người khác. Bạn muốn lưu kết luận mới của mình? Bản cũ được giữ trong thư mục sao lưu.")) return;
    const button = form.querySelector("button");
    button.disabled = true;
    try {
      const result = await api("/api/save", {
        kind: isHash ? "hash" : "semantic", image: item.image, key: item.key,
        reviewer: byId("reviewer").value, note: form.querySelector(".note").value,
        type: kind.value, verdict: verdict.value, status: verdict.value,
        seen: form.querySelector(".seen input").checked,
        replace_review: Boolean(otherReviewer),
        revision: isHash ? state.hash_revision : state.review_revision,
        candidate_revision: state.candidate_revision
      });
      drafts.delete(draftKey);
      dirty = drafts.size > 0;
      state = result.state;
      render();
      notice(result.message);
    } catch (error) {
      notice(error.message, true);
      button.disabled = false;
    }
  });
  return article;
}

function render() {
  byId("qc").textContent = state.rules_count + "/" + state.images_count
    + " · " + (state.rate > 0.02 ? "HOLD" : "Trong ngưỡng 2%");
  byId("review-progress").textContent = state.review_complete + "/" + state.cases.length;
  byId("hash-progress").textContent = state.hash_complete + "/" + state.hash_cases.length;
  byId("run-info").textContent = state.run + " · " + state.release_id;
  const current = byId("reviewer").value;
  const queue = byId("queue");
  queue.replaceChildren();
  const all = byId("filter").value === "all";
  const selected = state.cases.filter(c => all || c.owner === current || c.cross === current);
  for (const item of selected) queue.append(renderCase(item, false));
  for (const item of state.hash_cases.filter(c => all || c.owner === current))
    queue.append(renderCase(item, true));
  if (!queue.children.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "Chưa có ca được giao cho vị trí này. Chọn cả nhóm để xem danh sách.";
    queue.append(empty);
  }
  const pending = [];
  if (state.review_complete < state.cases.length) pending.push("kết luận xem ảnh");
  if (state.hash_complete < state.hash_cases.length) pending.push("kiểm ảnh lệch hash");
  if (!state.handover_exists) pending.push("v2 từ TV5");
  pending.push("TV6 xác nhận trace", "TV7 chốt bảo mật", "TV1 kiểm cuối");
  byId("readiness").textContent = "Cần hoàn tất · " + pending.join(" · ") + ".";
  byId("merge").disabled = dirty || state.review_complete !== state.cases.length;
}

async function reload() {
  if (dirty && !window.confirm("Đang có nội dung chưa lưu. Tải lại và bỏ phần đang nhập?")) return;
  try {
    const previous = byId("reviewer").value || "TV1";
    state = await api("/api/state");
    byId("reviewer").replaceChildren();
    for (const [id, name] of Object.entries(state.members))
      byId("reviewer").append(option(id, id + " · " + name));
    byId("reviewer").value = previous;
    byId("reviewer").dataset.previous = previous;
    drafts.clear();
    dirty = false;
    render();
    notice("Dữ liệu đã tải. Chọn kết luận sau khi bạn trực tiếp xem ảnh.");
  } catch (error) {
    notice("Không kết nối được công cụ. " + error.message, true);
  }
}

for (const id of ["reviewer", "filter"]) {
  byId(id).addEventListener("change", (event) => {
    if (dirty && !window.confirm("Đang có nội dung chưa lưu. Đổi màn hình và bỏ phần đang nhập?")) {
      event.target.value = event.target.dataset.previous;
      return;
    }
    event.target.dataset.previous = event.target.value;
    drafts.clear();
    dirty = false;
    if (state) render();
  });
}
byId("filter").dataset.previous = "mine";
byId("reviewer").dataset.previous = "TV1";
byId("refresh").addEventListener("click", reload);
byId("merge").addEventListener("click", async () => {
  try {
    const result = await api("/api/merge", {});
    state = result.state;
    render();
    notice(result.message);
  } catch (error) {
    notice(error.message, true);
  }
});
byId("check").addEventListener("click", async () => {
  const button = byId("check");
  button.disabled = true;
  try {
    const result = await api("/api/check", {});
    byId("output").hidden = false;
    byId("output").textContent = result.output;
    notice(result.exit_code === 0 ? "Bộ kiểm bàn giao đã đạt." : "Bộ kiểm còn mục cần xử lý.");
  } catch (error) {
    notice(error.message, true);
  } finally {
    button.disabled = false;
  }
});
window.addEventListener("beforeunload", event => {
  if (dirty) {
    event.preventDefault();
    event.returnValue = "";
  }
});
reload();
