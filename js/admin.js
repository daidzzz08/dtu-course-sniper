import { ref, onValue, set, get, update } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";
import { db } from "./config.js";
import { isAdmin } from "./auth.js";

// --- LOAD SETTINGS ---
export function loadAdminAnnouncementSettings() {
    if (!isAdmin) return;
    onValue(ref(db, 'system_settings/announcement'), (snapshot) => {
        const data = snapshot.val() || { is_active: false, title: "", content: "" };
        document.getElementById('admin-ann-toggle').checked = data.is_active;
        document.getElementById('admin-ann-title').value = data.title || "";
        document.getElementById('admin-ann-content').value = data.content || "";
    });
}

// --- SAVE SETTINGS ---
export function saveAnnouncement() {
    if (!isAdmin) return;
    
    const isActive = document.getElementById('admin-ann-toggle').checked;
    const title = document.getElementById('admin-ann-title').value;
    const content = document.getElementById('admin-ann-content').value;
    const btn = event.target; 
    
    const originalText = btn.innerText;
    btn.innerText = "Đang lưu...";
    btn.disabled = true;

    set(ref(db, 'system_settings/announcement'), {
        is_active: isActive,
        title: title,
        content: content,
        updated_at: Date.now()
    })
    .then(() => {
        alert("✅ Đã lưu cấu hình thông báo!");
        btn.innerText = originalText;
        btn.disabled = false;
    })
    .catch((error) => {
        alert("❌ Lỗi: " + error.message);
        btn.innerText = originalText;
        btn.disabled = false;
    });
}

// --- RENDER USER TABLE ---
export function renderAdminPanel() {
    if (!isAdmin) return;
    const listContainer = document.getElementById('user-list');
    listContainer.innerHTML = '<tr><td colspan="3" class="p-4 text-center"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</td></tr>';

    onValue(ref(db, 'users'), (snapshot) => {
        const users = snapshot.val();
        listContainer.innerHTML = ''; 

        if (!users) {
            listContainer.innerHTML = '<tr><td colspan="3" class="p-4 text-center">Empty</td></tr>';
            return;
        }
        
        const userArray = Object.keys(users).map(key => ({ uid: key, ...users[key] }));
        userArray.sort((a, b) => (b.created_at || 0) - (a.created_at || 0));

        userArray.forEach(u => {
            const now = Date.now();
            const isUserExpired = u.expired_at < now;
            let statusHtml = u.role === 'admin' 
                ? '<span class="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded">ADMIN</span>'
                : (isUserExpired ? '<span class="bg-red-100 text-red-800 text-[10px] font-bold px-2 py-0.5 rounded">HẾT HẠN</span>' 
                : `<span class="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded">CÒN HẠN</span>`);

            let actionHtml = u.role === 'admin' ? '' : `
                <div class="flex gap-1 justify-end">
                    <button onclick="window.extendUser('${u.uid}', 1)" class="bg-white border hover:bg-teal-50 text-teal-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm">+1D</button>
                    <button onclick="window.extendUser('${u.uid}', 7)" class="bg-white border hover:bg-blue-50 text-blue-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm">+7D</button>
                    <button onclick="window.extendUser('${u.uid}', 30)" class="bg-white border hover:bg-indigo-50 text-indigo-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm">+30D</button>
                    <button onclick="window.extendUser('${u.uid}', -1)" class="bg-white border hover:bg-red-50 text-red-500 text-[10px] font-bold px-2 py-1 rounded shadow-sm"><i class="fa-solid fa-lock"></i></button>
                </div>`;

            const row = document.createElement('tr');
            row.className = "border-b border-slate-50 hover:bg-slate-50/50";
            row.innerHTML = `
                <td class="p-3"><div class="font-bold text-slate-700 text-xs">${u.email}</div><div class="text-[9px] text-slate-400 font-mono">${u.uid}</div></td>
                <td class="p-3">${statusHtml}</td>
                <td class="p-3 text-right">${actionHtml}</td>
            `;
            listContainer.appendChild(row);
        });
    });
}

// --- EXTEND USER FUNCTION ---
export function extendUser(uid, days) {
    if (!isAdmin) return;
    const userRef = ref(db, 'users/' + uid);
    get(userRef).then((snapshot) => {
        if (snapshot.exists()) {
            const currentExpiry = snapshot.val().expired_at || Date.now();
            const now = Date.now();
            const baseTime = currentExpiry < now ? now : currentExpiry;
            let newExpiry = days === -1 ? now - 1000 : baseTime + (days * 24 * 60 * 60 * 1000);
            update(userRef, { expired_at: newExpiry });
        }
    });
}