const menuData = {
  Coffee: [
    { id: 1, name: "아메리카노", price: 1500, image: "아메리카노.png" },
    { id: 2, name: "카페라떼", price: 2000 },
    { id: 3, name: "바닐라라떼", price: 2500 },
    { id: 4, name: "연유라떼", price: 2300 },
    { id: 5, name: "카라멜마끼아또", price: 2800 },
    { id: 6, name: "카페모카", price: 2600 }
  ],
  Tea: [
    { id: 7, name: "복숭아아이스티", price: 3500 },
    { id: 8, name: "캐모마일티", price: 2000 },
    { id: 9, name: "페퍼민트티", price: 2000 },
    { id: 10, name: "얼그레이티", price: 2500 },
    { id: 11, name: "유자티", price: 2200 },
    { id: 12, name: "레몬티", price: 2300 }
  ],
  "Ade/Juice": [
    { id: 13, name: "레몬에이드", price: 2800 },
    { id: 14, name: "자몽에이드", price: 2800 },
    { id: 15, name: "청포도에이드", price: 3000 },
    { id: 16, name: "딸기주스", price: 2600 },
    { id: 17, name: "오렌지주스", price: 2900 },
    { id: 18, name: "망고주스", price: 2900 }
  ],
  Beverage: [
    { id: 19, name: "초코라떼", price: 2700 },
    { id: 20, name: "말차라떼", price: 2800 },
    { id: 21, name: "고구마라떼", price: 2800 },
    { id: 22, name: "딸기라떼", price: 2900 },
    { id: 23, name: "바나나라떼", price: 3000 },
    { id: 24, name: "블랙펄라떼", price: 2200, image: "블랙펄라떼.png" }
  ],
  Blended: [
    { id: 25, name: "딸기스무디", price: 3200 },
    { id: 26, name: "망고스무디", price: 3200 },
    { id: 27, name: "블루베리스무디", price: 3500 },
    { id: 28, name: "요거트스무디", price: 3500 },
    { id: 29, name: "초코프라페", price: 3600 },
    { id: 30, name: "밀크쉐이크", price: 3500 }
  ]
};

let currentCategory = "Coffee";
let dineType = "매장";
let cart = [];
let selectedMenu = null;

let selectedOptions = {
  temp: "ICED",
  sweetness: "보통",
  ice: "얼음 보통"
};

function formatPrice(value) {
  return `${value.toLocaleString()}원`;
}

function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach(screen => {
    screen.classList.remove("active");
  });

  document.getElementById(screenId).classList.add("active");

  updateStateMarker();
}

function selectDineType(type) {
  dineType = type;

  document.getElementById("receipt-dine-type").textContent =
    type === "매장" ? "매장에서 먹고 갈게요" : "포장해서 갈게요";

  showScreen("screen-menu");

  updateStateMarker();
}

function setupCategoryButtons() {
  const buttons = document.querySelectorAll(".category");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      currentCategory = button.dataset.category;
      renderMenus();
      updateStateMarker();
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
    temp: "ICED",
    sweetness: "보통",
    ice: "얼음 보통"
  };

  document.getElementById("modal-menu-name").textContent = menu.name;

  renderOptionButtons();
  document.getElementById("option-modal").classList.remove("hidden");

  updateStateMarker();
}

function closeModal() {
  document.getElementById("option-modal").classList.add("hidden");
  selectedMenu = null;

  updateStateMarker();
}

function renderOptionButtons() {
  createOptionGroup("temp-options", ["ICED", "HOT"], selectedOptions.temp, value => {
    selectedOptions.temp = value;
    updateStateMarker();
    renderOptionButtons();
  });

  createOptionGroup("sweet-options", ["덜 달게", "보통", "달게"], selectedOptions.sweetness, value => {
    selectedOptions.sweetness = value;
    updateStateMarker();
    renderOptionButtons();
  });

  const iceGroup = document.getElementById("ice-group");

  if (selectedOptions.temp === "ICED") {
    iceGroup.style.display = "block";

    createOptionGroup("ice-options", ["얼음 많이", "얼음 보통", "얼음 적게"], selectedOptions.ice, value => {
      selectedOptions.ice = value;
      updateStateMarker();
      renderOptionButtons();
    });
  } else {
    iceGroup.style.display = "none";
  }
}

function createOptionGroup(containerId, options, selected, onClick) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  options.forEach(option => {
    const button = document.createElement("button");
    button.className = `option-btn ${selected === option ? "active" : ""}`;
    button.textContent = option;
    button.onclick = () => onClick(option);
    container.appendChild(button);
  });
}

function addToCart() {
  if (!selectedMenu) return;

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

  closeModal();
  renderOrderSummary();

  updateStateMarker();
}

function changeQuantity(itemId, change) {
  const item = cart.find(i => i.id === itemId);
  if (!item) return;

  item.quantity += change;

  if (item.quantity <= 0) {
    cart = cart.filter(i => i.id !== itemId);
  }

  renderOrderSummary();
  updateStateMarker();
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
    cartListEl.innerHTML = `<div class="cart-empty">담은 메뉴가 없습니다.</div>`;
    return;
  }

  cartListEl.innerHTML = "";

  cart.forEach(item => {
    const optionText =
      item.temp === "ICED"
        ? `${item.temp} · ${item.sweetness} · ${item.ice}`
        : `${item.temp} · ${item.sweetness}`;

    const itemEl = document.createElement("div");
    itemEl.className = "cart-item";

    itemEl.innerHTML = `
      <div class="cart-item-top">
        <div>
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-option">${optionText}</div>
        </div>
        <strong class="cart-item-price">${formatPrice(item.price * item.quantity)}</strong>
      </strong>

      <div class="cart-qty-row">
        <div class="qty-control">
          <button onclick="changeQuantity('${item.id}', -1)">-</button>
          <strong>${item.quantity}</strong>
          <button onclick="changeQuantity('${item.id}', 1)">+</button>
        </div>
      </div>
    `;

    cartListEl.appendChild(itemEl);
  });
}

function goToReceipt() {
  if (cart.length === 0) return;

  const receiptItems = document.getElementById("receipt-items");
  const receiptTotalPrice = document.getElementById("receipt-total-price");

  receiptItems.innerHTML = "";

  cart.forEach(item => {
    const optionText =
      item.temp === "ICED"
        ? `${item.temp} · ${item.sweetness} · ${item.ice}`
        : `${item.temp} · ${item.sweetness}`;

    const itemEl = document.createElement("div");
    itemEl.className = "receipt-item";

    itemEl.innerHTML = `
      <div class="receipt-item-top">
        <div>
          <div class="receipt-item-name">${item.name}</div>
          <div class="receipt-item-option">${optionText}</div>
        </div>
        <div class="receipt-item-right">
          <div>수량 ${item.quantity}</div>
          <strong>${formatPrice(item.price * item.quantity)}</strong>
        </div>
      </div>
    `;

    receiptItems.appendChild(itemEl);
  });

  const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  receiptTotalPrice.textContent = formatPrice(totalPrice);

  showScreen("screen-receipt");

  updateStateMarker();
}

function completePayment(method) {
  showToast(`${method} 결제가 완료되었습니다.`);

  setTimeout(() => {
    cart = [];
    renderOrderSummary();
    showScreen("screen-home");
    updateStateMarker();
  }, 1200);
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 1000);
}

function updateStateMarker() {
  let markerId = 0;

  const activeScreen = document.querySelector(".screen.active");
  if (!activeScreen) return;

  const screenId = activeScreen.id;

  if (screenId === "screen-home") {
    markerId = 0;
  }

  else if (screenId === "screen-menu") {
    const modal = document.getElementById("option-modal");

    if (modal && !modal.classList.contains("hidden")) {
      if (selectedMenu) {
        const menuHash = (selectedMenu.id - 1) % 6;

        const tempValue =
          selectedOptions.temp === "ICED" ? 0 :
          selectedOptions.temp === "HOT" ? 1 : 0;

        const sugarValue =
          selectedOptions.sweetness === "덜 달게" ? 0 :
          selectedOptions.sweetness === "보통" ? 1 :
          selectedOptions.sweetness === "달게" ? 2 : 1;

        const iceValue =
          selectedOptions.ice === "얼음 많이" ? 0 :
          selectedOptions.ice === "얼음 보통" ? 1 :
          selectedOptions.ice === "얼음 적게" ? 2 : 1;

        const optionCode = (tempValue * 9) + (sugarValue * 3) + iceValue;

        markerId = 256 + (menuHash * 32) + optionCode;
      } else {
        markerId = 256;
      }
    } else {
      if (currentCategory === "Coffee") markerId = 32;
      else if (currentCategory === "Tea") markerId = 64;
      else if (currentCategory === "Ade/Juice") markerId = 96;
      else if (currentCategory === "Beverage") markerId = 128;
      else if (currentCategory === "Blended") markerId = 160;
    }
  }

  else if (screenId === "screen-receipt") {
    if (cart.length > 0) {
      const rawMenuId = parseInt(cart[0].id.split("-")[0]) - 1;
      markerId = 512 + (rawMenuId * 4);
    } else {
      markerId = 512;
    }
  }

  else if (screenId === "screen-payment") {
    markerId = 768;
  }

  const marker = document.getElementById("state-marker");
  if (marker) {
    const formattedId = String(markerId);
    marker.src = `./kiosk_aruco_markers/aruco_id_${formattedId}.png`;

    const debugText = document.getElementById("marker-id-debug");
    if (debugText) {
      debugText.textContent = `Current ID: ${formattedId}`;
    }
  }
}

setupCategoryButtons();
renderMenus();
renderOrderSummary();
updateStateMarker();
