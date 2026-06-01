const menuData = {
  Coffee: [
    { id:  1, name: "아메리카노", price: 1500, image: "images/아메리카노.png" },
    { id:  2, name: "카페라떼", price: 2000, image:"images/카페라떼.png" },
    { id:  3, name: "바닐라라떼", price: 2500, image:"images/바닐라라떼.png" },
    { id:  4, name: "연유라떼", price: 2300, image:"images/연유라떼.png" },
    { id:  5, name: "카라멜마끼아또", price: 2800, image:"images/카라멜마끼아또.png" },
    { id:  6, name: "카페모카", price: 2600, image:"images/카페모카.png" }
  ],
  Tea: [
    { id:  7, name: "복숭아아이스티", price: 3500, image:"images/복숭아아이스티.png" },
    { id:  8, name: "유자티", price: 2200, image:"images/유자티.png" },
    { id:  9, name: "레몬티", price: 2300, image:"images/레몬티.png" },
    { id: 10, name: "캐모마일티", price: 2000, image:"images/캐모마일티.png" },
    { id: 11, name: "페퍼민트티", price: 2000, image:"images/페퍼민트티.png" },
    { id: 12, name: "얼그레이티", price: 2500, image:"images/얼그레이티.png" },
  ],
  "Ade/Juice": [
    { id: 13, name: "자몽에이드", price: 2800, image:"images/자몽에이드.png" },
    { id: 14, name: "레몬에이드", price: 2800, image:"images/레몬에이드.png" },
    { id: 15, name: "청포도에이드", price: 3000, image:"images/청포도에이드.png" },
    { id: 16, name: "딸기주스", price: 2600, image:"images/딸기주스.png" },
    { id: 17, name: "오렌지주스", price: 2900, image:"images/오렌지주스.png" },
    { id: 18, name: "망고주스", price: 2900, image: "images/망고주스.png" }
  ],
  Beverage: [
    { id: 19, name: "초코라떼", price: 2700, image:"images/초코라떼.png" },
    { id: 20, name: "말차라떼", price: 2800, image:"images/말차라떼.png" },
    { id: 21, name: "고구마라떼", price: 2800, image:"images/고구마라떼.png" },
    { id: 22, name: "딸기라떼", price: 2900, image:"images/딸기라떼.png" },
    { id: 23, name: "바나나라떼", price: 3000, image:"images/바나나라떼.png" },
    { id: 24, name: "블랙펄라떼", price: 2200, image: "images/블랙펄라떼.png" }
  ],
  Blended: [
    { id: 25, name: "딸기스무디", price: 3200, image:"images/딸기스무디.png" },
    { id: 26, name: "망고스무디", price: 3200, image:"images/망고스무디.png" },
    { id: 27, name: "블루베리스무디", price: 3500, image:"images/블루베리스무디.png" },
    { id: 28, name: "요거트스무디", price: 3500, image:"images/요거트스무디.png" },
    { id: 29, name: "초코프라페", price: 3600, image:"images/초코프라페.png" },
    { id: 30, name: "밀크쉐이크", price: 3500, image:"images/밀크쉐이크.png" }
  ]
};

/** 옵션에서 HOT 없이 Only Iced만 노출하는 메뉴 */
const ICED_ONLY_MENUS = new Set([
  "딸기스무디",
  "망고스무디",
  "블루베리스무디",
  "요거트스무디",
  "초코프라페",
  "밀크쉐이크",
  "블랙펄라떼",
  "딸기라떼",
  "자몽에이드",
  "레몬에이드",
  "청포도에이드",
  "딸기주스",
  "오렌지주스",
  "망고주스",
  "복숭아아이스티"
]);

function isIcedOnlyMenu(menu) {
  return menu && ICED_ONLY_MENUS.has(menu.name);
}

function tempDisplayLabel(temp, menuName) {
  if (temp === "ICED" && ICED_ONLY_MENUS.has(menuName)) return "ONLY ICED";
  return temp;
}

let currentCategory = "Coffee";
const CATEGORY_INDEX = {
  Coffee: 1,
  Tea: 2,
  "Ade/Juice": 3,
  Beverage: 4,
  Blended: 5
};
/** 첫 화면에서 선택: `'매장'` | `'포장'` */
let dineType = null;
let cart = [];
let selectedMenu = null;
let lastCartCommonRefId = null;

let selectedOptions = {
  temp: null,
  sweetness: null,
  ice: null
};

function applyMarkerImage(el, markerId) {
  if (!el) return;
  el.style.background = `url('markers/marker_${markerId}.png') center / 100% 100% no-repeat`;
}

function getMenuHash(menu) {
  // 공통 참조 ID: 카테고리 순 + 카테고리 내 표시 순서(현재 데이터 id 1~30과 동일)
  const commonRefId = Math.max(0, (menu?.id ?? 1) - 1);
  return commonRefId % 6;
}

function getOptionMarkerId() {
  const menuHash = getMenuHash(selectedMenu);
  const temperature =
    selectedOptions.temp == null ? 0 : (selectedOptions.temp === "HOT" ? 2 : 1);
  const sugar = selectedOptions.sweetness == null ? 0 : 1;
  const ice = selectedOptions.ice == null ? 0 : 1;

  return 256 + menuHash * 32 + temperature * 8 + sugar * 4 + ice * 2;
}

function updateBottomMarkers() {
  const left = document.querySelector(".corner-marker--bl");
  const right = document.querySelector(".corner-marker--br");
  if (!left || !right) return;

  const isHome = document.getElementById("screen-home")?.classList.contains("active");
  const isPaymentFlow =
    document.getElementById("screen-payment")?.classList.contains("active") ||
    document.getElementById("screen-payment-complete")?.classList.contains("active");
  const isOptionModalOpen = !document.getElementById("option-modal")?.classList.contains("hidden");
  const hasCartItem = cart.length > 0 && lastCartCommonRefId != null;

  left.style.visibility = "visible";
  right.style.visibility = "visible";

  const markerId = isOptionModalOpen
    ? getOptionMarkerId()
    : isPaymentFlow
      ? 768
      : hasCartItem
        ? 512 + lastCartCommonRefId * 4
        : isHome
          ? 0
          : (CATEGORY_INDEX[currentCategory] ?? 1) * 32;
  applyMarkerImage(left, markerId);
  applyMarkerImage(right, markerId);
}

function formatPrice(value) {
  return `${value.toLocaleString()}원`;
}

let paymentCompleteCountdownTimer = null;

function stopPaymentCompleteCountdown() {
  if (paymentCompleteCountdownTimer !== null) {
    clearInterval(paymentCompleteCountdownTimer);
    paymentCompleteCountdownTimer = null;
  }
}

function startPaymentCompleteCountdown() {
  stopPaymentCompleteCountdown();
  const el = document.getElementById("payment-complete-countdown");
  let remaining = 15;

  function updateText() {
    if (el) el.textContent = `${remaining}초 후에 자동으로 닫혀요`;
  }

  updateText();

  paymentCompleteCountdownTimer = setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      stopPaymentCompleteCountdown();
      finishDemoPaymentToHome();
      return;
    }
    updateText();
  }, 1000);
}

function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach(screen => {
    screen.classList.remove("active");
  });

  document.getElementById(screenId).classList.add("active");

  document.querySelector(".device-frame")?.classList.toggle("on-home-screen", screenId === "screen-home");

  if (screenId === "screen-payment-complete") {
    startPaymentCompleteCountdown();
  } else {
    stopPaymentCompleteCountdown();
  }

  updateBottomMarkers();
}

function openHomeConfirmModal() {
  document.getElementById("home-confirm-modal")?.classList.remove("hidden");
}

function closeHomeConfirmModal() {
  document.getElementById("home-confirm-modal")?.classList.add("hidden");
}

function confirmGoHome() {
  cart = [];
  lastCartCommonRefId = null;
  dineType = null;
  closeModal();
  closeHomeConfirmModal();
  renderOrderSummary();
  showScreen("screen-home");
}

function selectDineType(type) {
  dineType = type;
  // Leave a short moment so press animation is visible on touchscreens.
  setTimeout(() => {
    showScreen("screen-menu");
  }, 120);
}

function setupCategoryButtons() {
  const buttons = document.querySelectorAll(".category");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      currentCategory = button.dataset.category;
      renderMenus();
      updateBottomMarkers();
    });
  });
}

function renderMenus() {
  const grid = document.getElementById("menu-grid");
  grid.innerHTML = "";

  const menus = menuData[currentCategory] || [];

  menus.slice(0, 6).forEach(menu => {
    const card = document.createElement("div");
    card.className = "menu-item-card";
    card.onclick = () => openModal(menu);

    card.innerHTML = `
      ${menu.image ? `<img class="menu-img" src="${menu.image}" alt="${menu.name}">` : ""}
      <div class="menu-title">${menu.name}</div>
      <div class="menu-price">${formatPrice(menu.price)}</div>
    `;

    grid.appendChild(card);
  });
}

function openModal(menu) {
  selectedMenu = menu;

  selectedOptions = {
    temp: null,
    sweetness: null,
    ice: null
  };

  document.getElementById("modal-menu-name").textContent = menu.name;

  renderOptionButtons();
  document.getElementById("option-modal").classList.remove("hidden");
  updateBottomMarkers();
}

function closeModal() {
  document.getElementById("option-modal").classList.add("hidden");
  selectedMenu = null;
  updateBottomMarkers();
}

function areModalOptionsComplete() {
  if (!selectedMenu) return false;
  const { temp, sweetness, ice } = selectedOptions;
  if (temp == null || sweetness == null) return false;
  if (temp === "ICED" && ice == null) return false;
  return true;
}

function updateAddToCartButton() {
  const btn = document.getElementById("add-to-cart-button");
  if (btn) btn.disabled = !areModalOptionsComplete();
}

function renderOptionButtons() {
  const icedOnly = isIcedOnlyMenu(selectedMenu);

  if (icedOnly) {
    createOptionGroup("temp-options", [{ value: "ICED", label: "ONLY ICED" }], selectedOptions.temp, value => {
      selectedOptions.temp = value;
      renderOptionButtons();
    });
  } else {
    createOptionGroup("temp-options", ["ICED", "HOT"], selectedOptions.temp, value => {
      selectedOptions.temp = value;
      if (value === "HOT") selectedOptions.ice = null;
      renderOptionButtons();
    });
  }

  createOptionGroup("sweet-options", ["덜 달게", "당도 보통", "달게"], selectedOptions.sweetness, value => {
    selectedOptions.sweetness = value;
    renderOptionButtons();
  });

  const iceGroup = document.getElementById("ice-group");
  const isIceDisabled = selectedOptions.temp === "HOT";
  iceGroup.classList.toggle("disabled", isIceDisabled);

  createOptionGroup(
    "ice-options",
    ["얼음 적게", "얼음 보통", "얼음 많이"],
    selectedOptions.ice,
    value => {
      selectedOptions.ice = value;
      renderOptionButtons();
    },
    isIceDisabled
  );

  updateAddToCartButton();
  updateBottomMarkers();
}

function createOptionGroup(containerId, options, selected, onClick, disabled = false) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  options.forEach(option => {
    const value = typeof option === "object" && option !== null ? option.value : option;
    const label = typeof option === "object" && option !== null ? option.label : option;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `option-btn ${selected === value ? "active" : ""}`;
    button.textContent = label;
    button.disabled = disabled;
    button.onclick = () => {
      if (!disabled) onClick(value);
    };
    container.appendChild(button);
  });
}

function addToCart() {
  if (!selectedMenu || !areModalOptionsComplete()) return;

  const itemId = `${selectedMenu.id}-${selectedOptions.temp}-${selectedOptions.sweetness}-${selectedOptions.temp === "ICED" ? selectedOptions.ice : "NOICE"}`;

  const existingItem = cart.find(item => item.id === itemId);

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      id: itemId,
      name: selectedMenu.name,
      price: selectedMenu.price,
      quantity: 1,
      temp: selectedOptions.temp,
      sweetness: selectedOptions.sweetness,
      ice: selectedOptions.temp === "ICED" ? selectedOptions.ice : ""
    });
  }
  lastCartCommonRefId = Math.max(0, selectedMenu.id - 1);

  closeModal();
  renderOrderSummary();
}

function renderOrderSummary() {
  const cartListEl = document.getElementById("cart-list");
  const orderCountEl = document.getElementById("order-count");
  const totalPriceEl = document.getElementById("total-price");
  const payButton = document.getElementById("pay-button");

  const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  orderCountEl.textContent = `${totalCount}개`;
  totalPriceEl.textContent = formatPrice(totalPrice);
  payButton.disabled = totalCount === 0;

  if (cart.length === 0) {
    lastCartCommonRefId = null;
    cartListEl.innerHTML = `<div class="cart-empty">담은 메뉴가 없습니다</div>`;
    updateBottomMarkers();
    return;
  }

  cartListEl.innerHTML = "";

  cart.forEach(item => {
    const tempLabel = tempDisplayLabel(item.temp, item.name);
    const optionText =
      item.temp === "ICED"
        ? `${tempLabel} · ${item.sweetness} · ${item.ice}`
        : `${tempLabel} · ${item.sweetness}`;

    const itemEl = document.createElement("div");
    itemEl.className = "cart-item";

    itemEl.innerHTML = `
      <div class="cart-item-top">
        <div>
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-option">${optionText}</div>
        </div>
        <strong class="cart-item-price">${formatPrice(item.price * item.quantity)}</strong>
      </div>

      <div class="cart-qty-row">
        <div class="qty-control">
          <button type="button" aria-label="수량 감소" onclick="changeQuantity('${item.id}', -1)">-</button>
          <strong class="qty-value">${item.quantity}</strong>
          <button type="button" aria-label="수량 증가" onclick="changeQuantity('${item.id}', 1)">+</button>
        </div>
      </div>
    `;

    cartListEl.appendChild(itemEl);
  });
  updateBottomMarkers();
}

function changeQuantity(itemId, delta) {
  const targetItem = cart.find(item => item.id === itemId);
  if (!targetItem) return;

  targetItem.quantity += delta;

  if (targetItem.quantity <= 0) {
    cart = cart.filter(item => item.id !== itemId);
  }

  renderOrderSummary();
}

function renderPaymentReceipt() {
  const container = document.getElementById("payment-receipt-items");
  const countEl = document.getElementById("payment-order-count");
  const totalEl = document.getElementById("payment-total-price");
  const greetEl = document.getElementById("payment-dine-greeting");
  if (!container || !countEl || !totalEl) return;

  if (greetEl) {
    greetEl.textContent =
      dineType === "포장"
        ? "고객님, 포장해 가시는군요!"
        : "고객님, 매장에서 드시고 가시는군요!";
  }

  const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  countEl.textContent = `${totalCount}개`;
  totalEl.textContent = formatPrice(totalPrice);

  container.innerHTML = "";

  cart.forEach(item => {
    const tempLabel = tempDisplayLabel(item.temp, item.name);
    const optionText =
      item.temp === "ICED"
        ? `${tempLabel} · ${item.sweetness} · ${item.ice}`
        : `${tempLabel} · ${item.sweetness}`;

    const itemEl = document.createElement("div");
    itemEl.className = "receipt-item";
    itemEl.innerHTML = `
      <div class="receipt-item-top">
        <div>
          <div class="receipt-item-name">${item.name} · ${item.quantity}개</div>
          <div class="receipt-item-option">${optionText}</div>
        </div>
        <div class="receipt-item-right">
          <strong>${formatPrice(item.price * item.quantity)}</strong>
        </div>
      </div>
    `;
    container.appendChild(itemEl);
  });
}

function goToPayment() {
  if (cart.length === 0) return;
  renderPaymentReceipt();
  showScreen("screen-payment");
}

function completePayment() {
  showScreen("screen-payment-complete");
}

function finishDemoPaymentToHome() {
  stopPaymentCompleteCountdown();
  cart = [];
  lastCartCommonRefId = null;
  dineType = null;
  renderOrderSummary();
  showScreen("screen-home");
}
setupCategoryButtons();
renderMenus();
renderOrderSummary();
updateBottomMarkers();

/** 터치/펜에서 :active 가 약할 때 눌림 모션 유지 (Pointer Events + touch, 종료는 window 캡처) */
(function setupTouchPressFeedback() {
  const root = document.querySelector(".device-frame");
  if (!root) return;

  const CLASS = "touch-pressed";
  let pressed = null;

  function clearPress() {
    if (pressed) {
      pressed.classList.remove(CLASS);
      pressed = null;
    }
  }

  function tryStartPress(e) {
    if (e.pointerType === "mouse") return;
    const btn = e.target.closest("button");
    if (!btn || btn.disabled) return;
    clearPress();
    pressed = btn;
    btn.classList.add(CLASS);
  }

  root.addEventListener("pointerdown", tryStartPress, { passive: true });
  if (!window.PointerEvent) {
    root.addEventListener("touchstart", tryStartPress, { passive: true });
  }

  window.addEventListener("pointerup", clearPress, true);
  window.addEventListener("pointercancel", clearPress, true);
  window.addEventListener("touchend", clearPress, true);
  window.addEventListener("touchcancel", clearPress, true);
})();