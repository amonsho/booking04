/* eslint-disable no-use-before-define */

const UI = {
  toastContainerId: "toast-container",
};

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(accessToken, refreshToken) {
  if (accessToken) localStorage.setItem("access_token", accessToken);
  if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
}

function clearToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

function authHeaders() {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function apiFetch(path, { method = "GET", headers = {}, body } = {}) {
  const res = await fetch(path, {
    method,
    headers: {
      ...headers,
    },
    body,
  });

  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    const message =
      (payload && payload.detail) ||
      (typeof payload === "string" ? payload : "") ||
      `Request failed: ${res.status}`;
    throw new Error(message);
  }
  return payload;
}

function photoUrl(photo) {
  if (!photo) return "";
  if (photo.startsWith("http://") || photo.startsWith("https://")) return photo;
  if (photo.startsWith("/")) return photo;

  // Backend stores photos as either:
  // - "media/<file>" (hotel)
  // - "media/room/<file>" (room)
  // but FastAPI mounts them at "/media/<rest>".
  if (photo.startsWith("media/")) return `/media/${photo.slice("media/".length)}`;
  if (photo.startsWith("room/")) return `/media/${photo}`;
  return `/media/${photo}`;
}

function money(n) {
  const num = typeof n === "number" ? n : Number(n);
  if (!Number.isFinite(num)) return String(n ?? "");
  return num.toFixed(2);
}

function toast(message, { variant = "success" } = {}) {
  const container = document.getElementById(UI.toastContainerId);
  if (!container) return alert(message);

  const bg =
    variant === "error"
      ? "bg-red-600"
      : variant === "warning"
        ? "bg-amber-500"
        : "bg-emerald-600";

  const el = document.createElement("div");
  el.className =
    `px-4 py-3 rounded-xl shadow-lg text-white ${bg} ` +
    "opacity-0 transform translate-y-2 transition duration-200";
  el.textContent = message;
  container.appendChild(el);

  requestAnimationFrame(() => {
    el.classList.remove("opacity-0", "translate-y-2");
  });

  setTimeout(() => {
    el.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => el.remove(), 250);
  }, 2800);
}

function requireAuthOrRedirect() {
  const token = getToken();
  if (token) return true;
  window.location.href = "/ui/login.html";
  return false;
}

function setModalLoading(isLoading) {
  const btn = document.getElementById("book-btn");
  const spinner = document.getElementById("book-spinner");
  if (!btn || !spinner) return;
  btn.disabled = isLoading;
  spinner.classList.toggle("hidden", !isLoading);
}

function getSelectedHotelLabel(hotel) {
  if (!hotel) return "All rooms";
  return `${hotel.name} (${hotel.city})`;
}

function renderEmptyState(el, message) {
  el.innerHTML =
    `<div class="flex items-center justify-center h-48 w-full rounded-2xl ` +
    `border border-dashed border-slate-200 bg-white/70">` +
    `<p class="text-slate-700">${message}</p></div>`;
}

async function fetchHotels() {
  return apiFetch("/hotel/get_all", {
    method: "GET",
    headers: { ...authHeaders() },
  });
}

async function fetchRooms() {
  return apiFetch("/rooms/", {
    method: "GET",
  });
}

function waitForEl(id) {
  return new Promise((resolve) => {
    const el = document.getElementById(id);
    if (el) return resolve(el);
    const timer = setInterval(() => {
      const el2 = document.getElementById(id);
      if (el2) {
        clearInterval(timer);
        resolve(el2);
      }
    }, 50);
  });
}

function createCard({ title, subtitle, description, photoUrl, onAction, actionLabel }) {
  const actionBtn = onAction
    ? `<button data-action="card-action" ` +
      `class="mt-4 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white ` +
      `hover:bg-slate-800 transition">` +
      `${actionLabel || "Open"}</button>`
    : "";

  return `
    <div class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white/70 backdrop-blur">
      <div class="aspect-[16/10] w-full overflow-hidden bg-slate-100">
        ${photoUrl ? `<img alt="" src="${photoUrl}" class="h-full w-full object-cover transition duration-300 group-hover:scale-105" />` : ""}
      </div>
      <div class="p-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h3 class="text-base font-bold text-slate-900">${title || ""}</h3>
            <p class="text-sm text-slate-600">${subtitle || ""}</p>
          </div>
        </div>
        ${description ? `<p class="mt-2 text-sm text-slate-700 line-clamp-2">${description}</p>` : ""}
        ${actionBtn}
      </div>
    </div>
  `;
}

async function initLogin() {
  const form = document.getElementById("login-form");
  const errorEl = document.getElementById("login-error");
  const btn = document.getElementById("login-submit");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.classList.add("hidden");
    btn.disabled = true;
    const oldText = btn.textContent;
    btn.textContent = "Signing in...";

    try {
      const email = document.getElementById("login-email").value.trim();
      const password = document.getElementById("login-password").value;

      const body = new URLSearchParams();
      body.set("username", email);
      body.set("password", password);

      const data = await apiFetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: body.toString(),
      });

      setToken(data.access_token, data.refresh_token);
      toast("Signed in successfully");
      window.location.href = "/ui/index.html";
    } catch (err) {
      errorEl.textContent = err.message || "Login failed";
      errorEl.classList.remove("hidden");
      toast(err.message || "Login failed", { variant: "error" });
    } finally {
      btn.disabled = false;
      btn.textContent = oldText;
    }
  });
}

async function initRegister() {
  const form = document.getElementById("register-form");
  const errorEl = document.getElementById("register-error");
  const successEl = document.getElementById("register-success");
  const btn = document.getElementById("register-submit");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.classList.add("hidden");
    successEl.classList.add("hidden");
    btn.disabled = true;
    const oldText = btn.textContent;
    btn.textContent = "Creating account...";

    try {
      const payload = {
        name: document.getElementById("register-name").value.trim(),
        email: document.getElementById("register-email").value.trim(),
        password: document.getElementById("register-password").value,
        password2: document.getElementById("register-password2").value,
      };

      await apiFetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify(payload),
      });

      successEl.textContent = "Account created. Please log in.";
      successEl.classList.remove("hidden");
      toast("Account created");
      btn.textContent = oldText;
      setTimeout(() => {
        window.location.href = "/ui/login.html";
      }, 900);
    } catch (err) {
      errorEl.textContent = err.message || "Register failed";
      errorEl.classList.remove("hidden");
      toast(err.message || "Register failed", { variant: "error" });
    } finally {
      btn.disabled = false;
      btn.textContent = oldText;
    }
  });

  // Google register button (Identity Services)
  const googleBtnEl = document.getElementById("google-btn");
  if (googleBtnEl) {
    const clientId = googleBtnEl.dataset.googleClientId || "";

    const waitForGoogle = () =>
      new Promise((resolve) => {
        const timer = setInterval(() => {
          if (window.google && window.google.accounts && window.google.accounts.id) {
            clearInterval(timer);
            resolve();
          }
        }, 50);
        setTimeout(() => {
          clearInterval(timer);
          resolve();
        }, 10000);
      });

    await waitForGoogle();

    if (!clientId) {
      toast("Set YOUR_GOOGLE_CLIENT_ID in register page", { variant: "warning" });
      return;
    }

    try {
      if (!window.google || !window.google.accounts || !window.google.accounts.id) {
        throw new Error("Google script not loaded yet");
      }
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (resp) => {
          try {
            const idToken = resp.credential;
            if (!idToken) throw new Error("No Google credential received");

            const data = await apiFetch("/auth/google/register", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ id_token: idToken }),
            });

            setToken(data.access_token, data.refresh_token);
            toast("Signed in with Google");
            window.location.href = "/ui/index.html";
          } catch (err) {
            errorEl.textContent = err.message || "Google sign-in failed";
            errorEl.classList.remove("hidden");
            toast(err.message || "Google sign-in failed", { variant: "error" });
          }
        },
      });

      window.google.accounts.id.renderButton(googleBtnEl, {
        theme: "outline",
        size: "large",
      });
    } catch (err) {
      toast(err.message || "Google init failed", { variant: "error" });
    }
  }
}

async function initIndex() {
  const hotelsGrid = document.getElementById("hotels-grid");
  const roomsGrid = document.getElementById("rooms-grid");
  const filterLabel = document.getElementById("filter-label");
  const logoutBtn = document.getElementById("logout-btn");
  const profileLink = document.getElementById("profile-link");
  const adminLink = document.getElementById("admin-link");
  const signInCTA = document.getElementById("signin-cta");

  if (!hotelsGrid || !roomsGrid) return;

  let hotels = [];
  let rooms = [];
  let selectedHotelId = null;

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearToken();
      window.location.href = "/ui/login.html";
    });
  }

  if (profileLink && profileLink.href) {
    if (!getToken()) profileLink.classList.add("hidden");
    else profileLink.classList.remove("hidden");
  }
  if (adminLink && adminLink.href) {
    if (!getToken()) adminLink.classList.add("hidden");
    else adminLink.classList.remove("hidden");
  }

  const hasAuth = !!getToken();
  if (signInCTA) signInCTA.classList.toggle("hidden", hasAuth);
  if (logoutBtn) logoutBtn.classList.toggle("hidden", !hasAuth);

  try {
    rooms = await fetchRooms();
  } catch (err) {
    renderEmptyState(roomsGrid, err.message || "Failed to load rooms");
    return;
  }

  const renderRooms = () => {
    const visibleRooms = selectedHotelId
      ? rooms.filter((r) => r.hotel_id === selectedHotelId)
      : rooms;

    filterLabel.textContent = getSelectedHotelLabel(
      selectedHotelId ? hotels.find((h) => h.id === selectedHotelId) : null
    );

    if (!visibleRooms.length) {
      renderEmptyState(roomsGrid, "No rooms found for this hotel.");
      return;
    }

    roomsGrid.innerHTML = visibleRooms
      .map((r) => {
        const hotel = hotels.find((h) => h.id === r.hotel_id);
        const wifiBadge = r.wifi ? "WiFi included" : "No WiFi";
        const photo = photoUrl(r.photo);
        return `
          <div class="group rounded-2xl border border-slate-200 bg-white/70 backdrop-blur overflow-hidden">
            <div class="aspect-[16/10] bg-slate-100 overflow-hidden">
              ${photo ? `<img alt="" src="${photo}" class="h-full w-full object-cover transition duration-300 group-hover:scale-105" />` : ""}
            </div>
            <div class="p-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <h3 class="text-base font-bold text-slate-900">${r.room_type}</h3>
                  <p class="text-sm text-slate-600">${hotel ? hotel.name : `Hotel #${r.hotel_id}`}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm text-slate-500">Per night</p>
                  <p class="text-lg font-extrabold text-slate-900">$${money(r.price)}</p>
                </div>
              </div>

              <div class="mt-3 flex flex-wrap gap-2">
                <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  ${wifiBadge}
                </span>
              </div>

              <button
                class="mt-4 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 transition"
                data-book-room-id="${r.id}"
              >
                Book
              </button>
            </div>
          </div>
        `;
      })
      .join("");
  };

  const renderHotels = () => {
    hotelsGrid.innerHTML = "";

    const allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className =
      "w-full rounded-2xl border border-slate-200 bg-white/70 backdrop-blur px-4 py-4 text-left hover:bg-white transition mb-3";
    allBtn.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="text-sm font-semibold text-slate-900">All hotels</div>
          <div class="text-xs text-slate-600">Browse rooms</div>
        </div>
        <div class="text-xs font-bold text-slate-900">${rooms.length}</div>
      </div>
    `;
    allBtn.addEventListener("click", () => {
      selectedHotelId = null;
      renderHotelsActive(allBtn);
      renderRooms();
    });
    hotelsGrid.appendChild(allBtn);

    const hotelCards = hotels
      .map((h) => {
        const photo = photoUrl(h.photo);
        const card = document.createElement("div");
        card.innerHTML = createCard({
          title: h.name,
          subtitle: h.city,
          description: h.address,
          photoUrl: photo,
          actionLabel: "Show rooms",
        });
        const root = card.firstElementChild;
        root.classList.add("cursor-pointer");

        root.addEventListener("click", () => {
          selectedHotelId = h.id;
          renderRooms();
          // quick active styling
          for (const child of Array.from(hotelsGrid.children)) {
            child.classList.remove("ring-2", "ring-slate-900");
          }
          root.classList.add("ring-2", "ring-slate-900");
        });
        return root;
      })
      .filter(Boolean);

    for (const cardEl of hotelCards) hotelsGrid.appendChild(cardEl);

    // default
    renderRooms();
  };

  const renderHotelsActive = () => {
    // no-op placeholder to keep code simple
  };

  // Modal
  const modal = document.getElementById("booking-modal");
  const modalClose = document.getElementById("booking-modal-close");
  const selectedRoomIdEl = document.getElementById("selected-room-id");
  const modalRoomTitle = document.getElementById("booking-room-title");
  const modalRoomPrice = document.getElementById("booking-room-price");
  const modalRoomWifi = document.getElementById("booking-room-wifi");
  const modalRoomPhoto = document.getElementById("booking-room-photo");

  const dateFromEl = document.getElementById("booking-date-from");
  const dateToEl = document.getElementById("booking-date-to");
  const guestsEl = document.getElementById("booking-guests");

  let selectedRoom = null;

  if (modalClose) {
    modalClose.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  }

  document.addEventListener("click", (e) => {
    const btn = e.target && e.target.closest ? e.target.closest("[data-book-room-id]") : null;
    if (!btn) return;
    if (!requireAuthOrRedirect()) return;

    const roomId = Number(btn.getAttribute("data-book-room-id"));
    selectedRoom = rooms.find((r) => r.id === roomId);
    if (!selectedRoom) return;

    selectedRoomIdEl.value = String(selectedRoom.id);
    modalRoomTitle.textContent = selectedRoom.room_type;
    modalRoomPrice.textContent = `$${money(selectedRoom.price)} / night`;
    modalRoomWifi.textContent = selectedRoom.wifi ? "WiFi included" : "No WiFi";
    modalRoomPhoto.src = photoUrl(selectedRoom.photo);

    modal.classList.remove("hidden");
  });

  const bookingForm = document.getElementById("booking-form");
  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setModalLoading(true);
      try {
        if (!selectedRoom) throw new Error("No room selected");
        const date_from = dateFromEl.value;
        const date_to = dateToEl.value;
        const guests = Number(guestsEl.value || 1);

        if (!date_from || !date_to) throw new Error("Please select dates");
        if (date_to <= date_from) throw new Error("date_to must be greater than date_from");
        if (!Number.isFinite(guests) || guests < 1) throw new Error("Guests must be >= 1");

        await apiFetch("/booking/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
          },
          body: JSON.stringify({
            room_id: selectedRoom.id,
            date_from,
            date_to,
            guests,
          }),
        });

        toast("Booking created");
        modal.classList.add("hidden");
        bookingForm.reset();
      } catch (err) {
        toast(err.message || "Booking failed", { variant: "error" });
        // keep modal open for correction
      } finally {
        setModalLoading(false);
      }
    });
  }

  // If user has auth, hotels list is available
  if (hasAuth) {
    try {
      hotels = await fetchHotels();
    } catch (err) {
      // If token invalid, show hotels section empty but still show rooms
      hotels = [];
      toast(err.message || "Failed to load hotels", { variant: "warning" });
    }
  }

  // Render
  if (hasAuth && hotels.length) renderHotels();
  else {
    // still show rooms
    filterLabel.textContent = "Browse rooms";
    selectedHotelId = null;
    renderRooms();

    // hotels section hint
    const hint = document.getElementById("hotels-hint");
    if (hint) hint.classList.remove("hidden");
    if (hotelsGrid) hotelsGrid.innerHTML = "";
  }
}

async function initProfile() {
  if (!requireAuthOrRedirect()) return;

  const bookingsBody = document.getElementById("bookings-body");
  const tableHint = document.getElementById("bookings-hint");
  if (!bookingsBody) return;

  try {
    const [bookings, rooms, hotels] = await Promise.all([
      apiFetch("/booking/me", { method: "GET", headers: { ...authHeaders() } }),
      fetchRooms(),
      fetchHotels(),
    ]);

    const roomById = new Map(rooms.map((r) => [r.id, r]));
    const hotelById = new Map(hotels.map((h) => [h.id, h]));

    if (!bookings.length) {
      bookingsBody.innerHTML = "";
      if (tableHint) tableHint.classList.remove("hidden");
      return;
    }

    if (tableHint) tableHint.classList.add("hidden");

    bookingsBody.innerHTML = bookings
      .map((b) => {
        const room = roomById.get(b.room_id);
        const hotel = room ? hotelById.get(room.hotel_id) : null;
        const status = b.status || "pending";
        const statusBg =
          status === "approved"
            ? "bg-emerald-600"
            : status === "rejected"
              ? "bg-red-600"
              : "bg-amber-500";

        return `
          <tr class="border-t border-slate-200">
            <td class="px-4 py-3 text-sm text-slate-700">#${b.id}</td>
            <td class="px-4 py-3 text-sm font-semibold text-slate-900">${hotel ? hotel.name : `Hotel #${room?.hotel_id || "?"}`}</td>
            <td class="px-4 py-3 text-sm text-slate-700">${room ? room.room_type : `Room #${b.room_id}`}</td>
            <td class="px-4 py-3 text-sm text-slate-700">${b.date_from} → ${b.date_to}</td>
            <td class="px-4 py-3 text-sm text-slate-700">${b.guests}</td>
            <td class="px-4 py-3 text-sm text-slate-700">${b.total_price != null ? `$${money(b.total_price)}` : "-"}</td>
            <td class="px-4 py-3">
              <span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold text-white ${statusBg}">
                ${status}
              </span>
            </td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    toast(err.message || "Failed to load profile", { variant: "error" });
    bookingsBody.innerHTML = "";
    if (tableHint) {
      tableHint.classList.remove("hidden");
      tableHint.textContent = err.message || "Failed to load bookings";
    }
  }
}

async function initAdmin() {
  if (!requireAuthOrRedirect()) return;

  const usersBody = document.getElementById("users-body");
  const usersHint = document.getElementById("users-hint");
  const refreshBtn = document.getElementById("admin-refresh-btn");
  const adminHotelsRefreshBtn = document.getElementById("admin-hotels-refresh-btn");
  const adminRoomsRefreshBtn = document.getElementById("admin-rooms-refresh-btn");

  if (!usersBody) return;

  const roomForm = document.getElementById("admin-room-form");
  const roomHotelSelect = document.getElementById("admin-room-hotel-id");
  const roomsBody = document.getElementById("admin-rooms-body");
  const roomsHint = document.getElementById("admin-rooms-hint");

  let adminHotels = [];

  const load = async () => {
    try {
      const users = await apiFetch("/admin/users", {
        method: "GET",
        headers: { ...authHeaders() },
      });

      if (usersHint) usersHint.classList.add("hidden");

      usersBody.innerHTML = (users || [])
        .map((u) => {
          const role = u.role || "user";
          const roleUserSelected = role === "user" ? "selected" : "";
          const roleAdminSelected = role === "admin" ? "selected" : "";

          return `
            <tr class="border-t border-slate-200">
              <td class="px-4 py-3 text-sm text-slate-700">#${u.id}</td>
              <td class="px-4 py-3 text-sm font-semibold text-slate-900">${u.name || ""}</td>
              <td class="px-4 py-3 text-sm text-slate-700">${u.email || ""}</td>
              <td class="px-4 py-3">
                <select
                  id="role-${u.id}"
                  class="w-40 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-slate-900/20"
                >
                  <option value="user" ${roleUserSelected}>user</option>
                  <option value="admin" ${roleAdminSelected}>admin</option>
                </select>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <button
                    type="button"
                    data-admin-set-role="${u.id}"
                    class="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    data-admin-delete-user="${u.id}"
                    class="rounded-xl bg-red-600 px-3 py-2 text-xs font-bold text-white hover:bg-red-500 transition"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          `;
        })
        .join("");

      // Bind actions after render
      const saveButtons = document.querySelectorAll("[data-admin-set-role]");
      for (const btn of saveButtons) {
        btn.addEventListener("click", async () => {
          const userId = btn.getAttribute("data-admin-set-role");
          const selectEl = document.getElementById(`role-${userId}`);
          const role = selectEl ? selectEl.value : "user";

          try {
            await apiFetch(`/admin/users/${userId}/role`, {
              method: "PATCH",
              headers: { "Content-Type": "application/json", ...authHeaders() },
              body: JSON.stringify({ role }),
            });
            toast("Role updated");
            await load();
          } catch (err) {
            toast(err.message || "Failed to update role", { variant: "error" });
          }
        });
      }

      const deleteButtons = document.querySelectorAll("[data-admin-delete-user]");
      for (const btn of deleteButtons) {
        btn.addEventListener("click", async () => {
          const userId = btn.getAttribute("data-admin-delete-user");
          const ok = window.confirm("Delete this user?");
          if (!ok) return;

          try {
            await apiFetch(`/admin/users/${userId}`, {
              method: "DELETE",
              headers: { ...authHeaders() },
            });
            toast("User deleted", { variant: "warning" });
            await load();
          } catch (err) {
            toast(err.message || "Failed to delete user", { variant: "error" });
          }
        });
      }
    } catch (err) {
      if (usersHint) {
        usersHint.classList.remove("hidden");
        usersHint.textContent = err.message || "Failed to load users";
      }

      // If token invalid or user is not admin, redirect.
      if (String(err.message || "").toLowerCase().includes("admin")) {
        toast(err.message || "Admin only", { variant: "error" });
        setTimeout(() => {
          window.location.href = "/ui/index.html";
        }, 800);
      }
      usersBody.innerHTML = "";
    }
  };

  if (refreshBtn) refreshBtn.addEventListener("click", load);

  await load();

  // Hotels section (admin can create)
  const hotelForm = document.getElementById("admin-hotel-form");
  const hotelsGrid = document.getElementById("admin-hotels-grid");
  const hotelsHint = document.getElementById("admin-hotels-hint");
  const hotelSubmitBtn = document.getElementById("admin-hotel-submit");

  const loadHotels = async () => {
    if (!hotelsGrid || !hotelsHint) return;

    hotelsHint.textContent = "Loading...";
    try {
      const hotels = await fetchHotels();
      adminHotels = hotels || [];
      hotelsHint.textContent = adminHotels && adminHotels.length ? "" : "No hotels yet";

      if (!adminHotels || !adminHotels.length) {
        hotelsGrid.innerHTML = "";
        return;
      }

      // fill hotel select for room creation
      if (roomHotelSelect) {
        roomHotelSelect.innerHTML = "";
        for (const h of adminHotels) {
          const opt = document.createElement("option");
          opt.value = String(h.id);
          opt.textContent = `${h.name} (${h.city})`;
          roomHotelSelect.appendChild(opt);
        }
      }

      hotelsGrid.innerHTML = hotels
        .map((h) =>
          createCard({
            title: h.name,
            subtitle: h.city,
            description: h.address,
            photoUrl: photoUrl(h.photo),
          })
        )
        .join("");
    } catch (err) {
      hotelsHint.textContent = err.message || "Failed to load hotels";
      hotelsGrid.innerHTML = "";
    }
  };

  if (adminHotelsRefreshBtn) adminHotelsRefreshBtn.addEventListener("click", loadHotels);

  if (hotelForm) {
    hotelForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!hotelSubmitBtn) return;

      hotelSubmitBtn.disabled = true;
      const oldText = hotelSubmitBtn.textContent;
      hotelSubmitBtn.textContent = "Creating...";

      try {
        const name = document.getElementById("admin-hotel-name")?.value || "";
        const city = document.getElementById("admin-hotel-city")?.value || "";
        const address = document.getElementById("admin-hotel-address")?.value || "";
        const description =
          document.getElementById("admin-hotel-description")?.value?.trim() || "";

        const photoEl = document.getElementById("admin-hotel-photo");
        const file = photoEl && photoEl.files ? photoEl.files[0] : null;
        if (!file) throw new Error("Choose hotel photo");

        const formData = new FormData();
        formData.append("name", name);
        formData.append("city", city);
        formData.append("address", address);
        if (description) formData.append("description", description);
        formData.append("photo", file);

        await apiFetch("/hotel/", {
          method: "POST",
          headers: { ...authHeaders() },
          body: formData,
        });

        toast("Hotel created");
        hotelForm.reset();
        await loadHotels();
      } catch (err) {
        toast(err.message || "Failed to create hotel", { variant: "error" });
      } finally {
        hotelSubmitBtn.disabled = false;
        hotelSubmitBtn.textContent = oldText;
      }
    });
  }

  // Rooms section
  const loadRooms = async () => {
    if (!roomsBody || !roomsHint) return;
    roomsHint.classList.add("hidden");

    const selectedHotelId = roomHotelSelect ? roomHotelSelect.value : "";
    const roomsAll = await fetchRooms();
    const rooms = selectedHotelId
      ? roomsAll.filter((r) => String(r.hotel_id) === String(selectedHotelId))
      : roomsAll;

    if (!rooms || !rooms.length) {
      roomsBody.innerHTML = "";
      roomsHint.classList.remove("hidden");
      roomsHint.textContent = "No rooms yet for this hotel.";
      return;
    }

    roomsBody.innerHTML = rooms
      .map((r) => {
        const photo = photoUrl(r.photo);
        return `
          <tr class="border-t border-slate-200">
            <td class="px-4 py-3 text-sm text-slate-700">#${r.id}</td>
            <td class="px-4 py-3 text-sm font-semibold text-slate-900">${r.room_type}</td>
            <td class="px-4 py-3 text-sm text-slate-700">$${money(r.price)}</td>
            <td class="px-4 py-3 text-sm text-slate-700">${r.wifi ? "Yes" : "No"}</td>
            <td class="px-4 py-3">
              ${photo ? `<img alt="" src="${photo}" class="h-10 w-14 rounded-lg object-cover border border-slate-200 bg-white" />` : "-"}
            </td>
            <td class="px-4 py-3">
              <button
                type="button"
                data-admin-delete-room="${r.id}"
                class="rounded-xl bg-red-600 px-3 py-2 text-xs font-bold text-white hover:bg-red-500 transition"
              >
                Delete
              </button>
            </td>
          </tr>
        `;
      })
      .join("");

    const deleteBtns = document.querySelectorAll("[data-admin-delete-room]");
    for (const btn of deleteBtns) {
      btn.addEventListener("click", async () => {
        const roomId = btn.getAttribute("data-admin-delete-room");
        const ok = window.confirm("Delete this room?");
        if (!ok) return;

        try {
          await apiFetch(`/rooms/${roomId}`, {
            method: "DELETE",
            headers: { ...authHeaders() },
          });
          toast("Room deleted", { variant: "warning" });
          await loadRooms();
        } catch (err) {
          toast(err.message || "Failed to delete room", { variant: "error" });
        }
      });
    }
  };

  if (roomHotelSelect) {
    roomHotelSelect.addEventListener("change", async () => {
      await loadRooms();
    });
  }

  if (adminRoomsRefreshBtn) {
    adminRoomsRefreshBtn.addEventListener("click", async () => {
      await loadRooms();
    });
  }

  if (roomForm) {
    roomForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!roomHotelSelect) return;
      const hotel_id = roomHotelSelect.value;

      const room_type = document.getElementById("admin-room-type")?.value?.trim() || "";
      const priceVal = document.getElementById("admin-room-price")?.value || "";
      const wifiEl = document.getElementById("admin-room-wifi");
      const wifi = wifiEl && wifiEl.checked ? "true" : "false";
      const photoEl = document.getElementById("admin-room-photo");
      const file = photoEl && photoEl.files ? photoEl.files[0] : null;

      if (!hotel_id) {
        toast("Select hotel", { variant: "warning" });
        return;
      }
      if (!room_type) {
        toast("Enter room type", { variant: "warning" });
        return;
      }
      if (!priceVal) {
        toast("Enter price", { variant: "warning" });
        return;
      }
      if (!file) {
        toast("Choose room photo", { variant: "warning" });
        return;
      }

      const formData = new FormData();
      formData.append("hotel_id", hotel_id);
      formData.append("room_type", room_type);
      formData.append("price", String(priceVal));
      formData.append("wifi", wifi);
      formData.append("photo", file);

      const submitBtn = document.getElementById("admin-room-submit");
      if (submitBtn) submitBtn.disabled = true;
      try {
        await apiFetch("/rooms/", {
          method: "POST",
          headers: { ...authHeaders() },
          body: formData,
        });

        toast("Room created");
        roomForm.reset();
        await loadHotels();
        await loadRooms();
      } catch (err) {
        toast(err.message || "Failed to create room", { variant: "error" });
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  await loadHotels();
  await loadRooms();
}

function initCommonNavigation() {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearToken();
      window.location.href = "/ui/login.html";
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initCommonNavigation();

  const page = document.body.dataset.page;
  if (page === "login") initLogin();
  if (page === "register") initRegister();
  if (page === "index") initIndex();
  if (page === "profile") initProfile();
  if (page === "admin") initAdmin();
});

