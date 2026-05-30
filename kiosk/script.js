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

// 화면 전환 공통 함수 (마커 트리거 바인딩 완료)
function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach(screen => {
    screen.classList.remove("active");
  });

  document.getElementById(screenId).classList.add("active");
  
  // 화면이 바뀔 때마다 아루코 마커 실시간 업데이트
  updateArucoIndicator();
}

function selectDineType(type) {
  dineType = type;

  document.getElementById("receipt-dine-type").textContent =
    type === "매장" ? "매장에서 먹고 갈게요" : "포장해서 갈게요";

  showScreen("screen-menu");
}

function setupCategoryButtons() {
  const buttons = document.querySelectorAll(".category");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      currentCategory = button.dataset.category;
      renderMenus();
      
      // 카테고리 변경 시 아루코 마커 즉각 업데이트 (32, 64, 96, 128, 160)
      updateArucoIndicator();
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
  
  // 모달이 열리는 순간 256번대 상세 옵션 마커 발동
  updateArucoIndicator();
}

function closeModal() {
  document.getElementById("option-modal").classList.add("hidden");
  selectedMenu = null;
  
  // 모달이 닫히면 다시 원래 카테고리 탭 마커로 복귀
  updateArucoIndicator();
}

function renderOptionButtons() {
  createOptionGroup("temp-options", ["ICED", "HOT"], selectedOptions.temp, value => {
    selectedOptions.temp = value;
    renderOptionButtons();
    // 옵션 버튼(온도) 클릭할 때마다 연산식 마커 즉각 업데이트
    updateArucoIndicator();
  });

  createOptionGroup("sweet-options", ["덜 달게", "보통", "달게"], selectedOptions.sweetness, value => {
    selectedOptions.sweetness = value;
    renderOptionButtons();
    // 옵션 버튼(당도) 클릭할 때마다 연산식 마커 즉각 업데이트
    updateArucoIndicator();
  });

  const iceGroup = document.getElementById("ice-group");

  if (selectedOptions.temp === "ICED") {
    iceGroup.style.display = "block";

    createOptionGroup("ice-options", ["얼음 많이", "얼음 보통", "얼음 적게"], selectedOptions.ice, value => {
      selectedOptions.ice = value;
      renderOptionButtons();
      // 옵션 버튼(얼음) 클릭할 때마다 연산식 마커 즉각 업데이트
      updateArucoIndicator();
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

  closeModal(); // 내부에서 updateArucoIndicator() 자동 실행됨
  renderOrderSummary();
}

// [추가] 장바구니 내 수량 변경 함수 구현 (HCI 평가 연계 마커 트래킹 포함)
function changeQuantity(itemId, change) {
  const item = cart.find(i => i.id === itemId);
  if (!item) return;

  item.quantity += change;

  if (item.quantity <= 0) {
    cart = cart.filter(i => i.id !== itemId);
  }

  renderOrderSummary();
  // 장바구니 리스트 변동 시 마커 상태 동기화 재처리
  updateArucoIndicator();
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
      </div>

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

  showScreen("screen-receipt"); // 내부에서 updateArucoIndicator() 자동 호출 (512번대 돌입)
}

function completePayment(method) {
  showToast(`${method} 결제가 완료되었습니다.`);

  setTimeout(() => {
    cart = [];
    renderOrderSummary();
    showScreen("screen-home"); // 내부에서 updateArucoIndicator()가 0번(리셋)으로 자동 복귀시킴
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

// [ArUco 마커 연계 자동화 엔진]

function updateArucoIndicator() {
  try {
    let markerId = 0;
    
    // 1. 현재 활성화된 화면 요소 찾기
    const activeScreen = document.querySelector('.screen.active');
    if (!activeScreen) return;
    const screenId = activeScreen.id;

    // 2. 각 스크린 ID별 예외 없는 완벽 가드 연산
    if (screenId === "screen-home") {
      markerId = 0;
    } 
    else if (screenId === "screen-menu") {
      const modal = document.getElementById("option-modal");
      
      // 모달창 팝업이 숨겨져 있는 상태 (카테고리 선택 단계)
      if (!modal || modal.classList.contains("hidden")) {
        const catText = String(currentCategory || "Coffee").trim().toLowerCase();
        if (catText.includes("coffee")) markerId = 32;
        else if (catText.includes("tea")) markerId = 64;
        else if (catText.includes("ade") || catText.includes("juice")) markerId = 96;
        else if (catText.includes("beverage")) markerId = 128;
        else if (catText.includes("blended")) markerId = 160;
        else markerId = 32;
      } 
      // 모달창 팝업이 열려 있는 상태 (상세 옵션 선택 단계)
      else {
        // [★ 핵심 방어] selectedMenu가 null인 상태에서 .id를 조회하여 뻗는 현상 차단
        if (selectedMenu && selectedMenu.id) {
          const menuHash = (parseInt(selectedMenu.id) - 1) % 6;
          
          let tempBit = (selectedOptions.temp === "ICED") ? 1 : ((selectedOptions.temp === "HOT") ? 2 : 0);
          let sugarBit = (selectedOptions.sweetness !== "보통") ? 1 : 0;
          let iceBit = (selectedOptions.ice === "얼음 보통") ? 0 : 1;
          
          markerId = 256 + (menuHash * 32) + (tempBit * 8) + (sugarBit * 4) + (iceBit * 2);
        } else {
          // 메뉴 데이터 로딩 전 안전 패딩값
          markerId = 256; 
        }
      }
    } 
    else if (screenId === "screen-receipt") {
      if (cart && cart.length > 0 && cart[0].id) {
        const rawId = parseInt(cart[0].id.split('-')[0]) - 1;
        markerId = 512 + (rawId * 4);
      } else {
        markerId = 512;
      }
    } 
    else if (screenId === "screen-payment") {
      markerId = 768;
    }

    // 3. HTML 이미지 객체 안전 제어
    const indicator = document.getElementById("aruco-indicator");
    if (indicator) {
      const formattedId = String(markerId).padStart(4, '0');
      
      // 경로가 안 맞아서 엑박이 뜨는 걸 원천 차단하기 위해 원격 가드 주소 사용
      // 만약 로컬 폴더로 온전히 돌리고 싶다면 아래 주소를 `vision/kiosk_aruco_markers/...`로 원복하셔도 됩니다.
      indicator.src = `vision/kiosk_aruco_markers/aruco_${formattedId}.png`;
      
      // 파일 탐색 실패 시 키오스크 자체가 굳어버리는 인터럽트 차단
      indicator.onerror = function() {
        console.log(`[ArUco] 마커 로드 유실 가드 (ID: ${formattedId})`);
      };
    }
  } catch (error) {
    // 예기치 못한 비트 연산 버그가 터지더라도 UI 전역 락이 걸리지 않도록 무조건 방어
    console.error("[ArUco 전역 가드 통과]: ", error);
  }
}

// 초기 로딩 이벤트 설정
setupCategoryButtons();
renderMenus();
renderOrderSummary();
updateArucoIndicator(); // 앱이 최초 켜질 때 0번 마커 초기 구동