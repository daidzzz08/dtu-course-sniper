import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { ref, set, onValue, get, child } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";
import { auth, db } from "./config.js";
import { showLoginScreen, showAppScreen, showGlobalModal, switchTab } from "./ui.js";
import { renderAdminPanel, loadAdminAnnouncementSettings } from "./admin.js";
import { listenToClasses } from "./app.js";

// Biến global lưu trạng thái
export let currentUser = null;
export let isExpired = true;
export let isAdmin = false;

// --- HANDLE AUTH ACTION (LOGIN/REGISTER) ---
export async function handleAuth(e, type) {
    e.preventDefault();
    const email = document.getElementById(type === 'login' ? 'login-email' : 'reg-email').value;
    const pass = document.getElementById(type === 'login' ? 'login-pass' : 'reg-pass').value;
    const errorMsg = document.getElementById(type === 'login' ? 'login-error' : 'reg-error');
    const btn = document.getElementById(type === 'login' ? 'login-btn' : 'reg-btn');
    
    errorMsg.classList.add('hidden');
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';

    try {
        if (type === 'register') {
            const userCredential = await createUserWithEmailAndPassword(auth, email, pass);
            await createNewUserProfile(userCredential.user.uid, email);
            alert("Đăng ký thành công! Vui lòng liên hệ Admin để kích hoạt.");
            switchTab('login');
        } else {
            await signInWithEmailAndPassword(auth, email, pass);
        }
    } catch (error) {
        let msg = error.message;
        if(msg.includes('invalid-credential')) msg = "Sai email hoặc mật khẩu.";
        if(msg.includes('email-already-in-use')) msg = "Email đã tồn tại.";
        errorMsg.innerText = msg;
        errorMsg.classList.remove('hidden');
    } finally {
        btn.innerHTML = type === 'login' ? 'Đăng Nhập' : 'Đăng Ký Ngay';
    }
}

// --- CREATE PROFILE ---
async function createNewUserProfile(uid, email) {
    const expiredAt = Date.now() - 1000; // Hết hạn ngay lập tức
    await set(ref(db, 'users/' + uid), {
        email: email,
        role: 'user',
        expired_at: expiredAt,
        created_at: Date.now()
    });
}

// --- CHECK USER STATUS ---
export async function checkUserStatus(uid) {
    currentUser = auth.currentUser;
    const userRef = ref(db, 'users/' + uid);
    
    onValue(userRef, (snapshot) => {
        const userData = snapshot.val();
        
        if (!userData) {
            createNewUserProfile(uid, currentUser.email);
            return;
        }

        isAdmin = userData.role === 'admin';
        const now = Date.now();
        isExpired = userData.expired_at < now;
        
        updateHeaderUI(userData);
        handleAccessControl();
        
        showAppScreen();
        listenToClasses(uid); // Load danh sách lớp
    });
}

function updateHeaderUI(userData) {
    document.getElementById('user-email-display').innerHTML = `
        <div class="flex flex-col items-end">
            <span class="font-bold text-slate-700 text-sm">${userData.email}</span>
            <span class="text-[10px] text-slate-400 uppercase tracking-wide">${isAdmin ? 'Administrator' : 'Khách hàng'}</span>
        </div>
    `;
}

function handleAccessControl() {
    const expiryBadge = document.getElementById('expiry-badge');
    const addBtn = document.getElementById('add-class-btn');
    const adminSection = document.getElementById('admin-section');
    const contactBanner = document.getElementById('contact-banner');

    if (isAdmin) {
        expiryBadge.className = "px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-bold border border-purple-200 shadow-sm";
        expiryBadge.innerHTML = `<i class="fa-solid fa-crown mr-1"></i> ADMIN PANEL`;
        addBtn.disabled = false;
        adminSection.classList.remove('hidden');
        contactBanner.classList.add('hidden');
        
        renderAdminPanel();
        loadAdminAnnouncementSettings();

    } else if (isExpired) {
        expiryBadge.className = "px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold border border-red-200";
        expiryBadge.innerHTML = `<i class="fa-solid fa-lock mr-1"></i> Chưa kích hoạt`;
        addBtn.disabled = true;
        addBtn.classList.add('opacity-50', 'cursor-not-allowed');
        adminSection.classList.add('hidden');
        contactBanner.classList.remove('hidden');
    } else {
        // Tính ngày còn lại (Logic đơn giản để hiển thị)
        // Cần lấy data lại để tính chính xác, nhưng ở đây ta dùng logic hiển thị
        expiryBadge.className = "px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold border border-green-200";
        expiryBadge.innerHTML = `<i class="fa-solid fa-clock mr-1"></i> Đã kích hoạt`;
        addBtn.disabled = false;
        addBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        adminSection.classList.add('hidden');
        contactBanner.classList.add('hidden');
    }
}

// --- LOAD SYSTEM ANNOUNCEMENT ---
export function loadSystemAnnouncement() {
    get(child(ref(db), 'system_settings/announcement')).then((snapshot) => {
        if (snapshot.exists()) {
            const data = snapshot.val();
            if (data.is_active === true) {
                showGlobalModal(data.title || "Thông báo", data.content || "");
            }
        }
    }).catch(console.error);
}

export function logout() {
    signOut(auth);
}