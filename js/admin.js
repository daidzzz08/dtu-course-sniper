import { ref, onValue, set, get, update } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";
import { db } from "./config.js";
import { isAdmin } from "./auth.js";

export function loadAdminAnnouncementSettings() {
    if (!isAdmin) return;
    onValue(ref(db, 'system_settings/announcement'), (snapshot) => {
        const data = snapshot.val() || { is_active: false, title: "", content: "" };
        document.getElementById('admin-ann-toggle').checked = data.is_active;
        document.getElementById('admin-ann-title').value = data.title || "";
        document.getElementById('admin-ann-content').value = data.content || "";
    });
}

export function saveAnnouncement() {
    if (!isAdmin) return;
    const isActive = document.getElementById('admin-ann-toggle').checked;
    const title = document.getElementById('admin-ann-title').value;
    const content = document.getElementById('admin-ann-content').value;
    const btn = event.target; 
    const originalText = btn.innerText;
    btn.innerText = "Đang lưu..."; btn.disabled = true;

    set(ref(db, 'system_settings/announcement'), {
        is_active: isActive, title: title, content: content, updated_at: Date.now()
    }).then(() => { alert("✅ Đã lưu cấu hình!"); btn.innerText = originalText; btn.disabled = false; })
      .catch((error) => { alert("❌ Lỗi: " + error.message); btn.innerText = originalText; btn.disabled = false; });
}

export function renderAdminPanel() {
    if (!isAdmin) return;
    const listContainer = document.getElementById('user-list');
    listContainer.innerHTML = '<tr><td colspan="3" class="p-4 text-center"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</td></tr>';

    onValue(ref(db, 'users'), (snapshot) => {
        const users = snapshot.val();
        listContainer.innerHTML = ''; 
        if (!users) { listContainer.innerHTML = '<tr><td colspan="3" class="p-4 text-center">Empty</td></tr>'; return; }
        
        const userArray = Object.keys(users).map(key => ({ uid: key, ...users[key] }));
        userArray.sort((a, b) => {
            if (a.role === 'admin') return -1;
            if (b.role === 'admin') return 1;
            return (b.created_at || 0) - (a.created_at || 0);
        });

        userArray.forEach(u => {
            const now = Date.now();
            const daysLeft = Math.ceil((u.expired_at - now) / (1000 * 60 * 60 * 24));
            
            let statusHtml = '';
            if (u.role === 'admin') statusHtml = '<span class="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded">ADMIN</span>';
            else if (u.expired_at < now) statusHtml = '<span class="bg-red-100 text-red-800 text-[10px] font-bold px-2 py-0.5 rounded">HẾT HẠN</span>';
            else statusHtml = `<span class="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded">CÒN ${daysLeft} NGÀY</span>`;

            const vipBtn = u.role !== 'admin' ? `<button onclick="window.openVipModal('${u.uid}')" class="bg-amber-100 hover:bg-amber-200 text-amber-700 w-8 h-8 rounded-lg flex items-center justify-center shadow-sm mr-2" title="Cấu hình VIP"><i class="fa-solid fa-key"></i></button>` : '';
            const extendBtns = u.role !== 'admin' ? `
                <button onclick="window.extendUser('${u.uid}', 1)" class="bg-white border hover:bg-teal-50 text-teal-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm mr-1">+1D</button>
                <button onclick="window.extendUser('${u.uid}', 7)" class="bg-white border hover:bg-blue-50 text-blue-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm mr-1">+7D</button>
                <button onclick="window.extendUser('${u.uid}', 30)" class="bg-white border hover:bg-indigo-50 text-indigo-600 text-[10px] font-bold px-2 py-1 rounded shadow-sm mr-1">+30D</button>
                <button onclick="window.extendUser('${u.uid}', -1)" class="bg-white border hover:bg-red-50 text-red-500 px-2 py-1 rounded shadow-sm"><i class="fa-solid fa-lock"></i></button>
            ` : '';

            const row = document.createElement('tr');
            row.className = "border-b border-slate-50 hover:bg-slate-50/50";
            row.innerHTML = `<td class="p-3"><div class="font-bold text-slate-700 text-xs">${u.email}</div><div class="text-[9px] text-slate-400 font-mono">${u.uid}</div></td><td class="p-3">${statusHtml}</td><td class="p-3 text-right flex justify-end items-center">${vipBtn}${extendBtns}</td>`;
            listContainer.appendChild(row);
        });
    });
}

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

export function openVipModal(uid) {
    if(!isAdmin) return;
    document.getElementById('vip-uid').value = uid;
    document.getElementById('vip-student-id').value = '';
    document.getElementById('vip-student-pass').value = '';
    document.getElementById('vip-active-toggle').checked = false;

    get(ref(db, `users/${uid}/student_account`)).then(snap => {
        if(snap.exists()) {
            const data = snap.val();
            document.getElementById('vip-student-id').value = data.id || '';
            document.getElementById('vip-student-pass').value = data.pass || '';
        }
    });
    get(ref(db, `users/${uid}/is_vip`)).then(snap => { if(snap.exists()) document.getElementById('vip-active-toggle').checked = snap.val(); });
    document.getElementById('vip-modal').classList.remove('hidden');
}
export function closeVipModal() { document.getElementById('vip-modal').classList.add('hidden'); }
export function saveVipConfig() {
    if(!isAdmin) return;
    const uid = document.getElementById('vip-uid').value;
    const stdId = document.getElementById('vip-student-id').value;
    const stdPass = document.getElementById('vip-student-pass').value;
    const isVip = document.getElementById('vip-active-toggle').checked;
    const updates = {};
    updates[`users/${uid}/student_account`] = { id: stdId, pass: stdPass };
    updates[`users/${uid}/is_vip`] = isVip;
    update(ref(db), updates).then(() => { alert("✅ Đã lưu!"); closeVipModal(); }).catch(err => alert("❌ Lỗi: " + err.message));
}