import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { ref, set, onValue, get, child } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";
import { auth, db } from "./config.js";
import { showLoginScreen, showAppScreen, showGlobalModal, switchTab } from "./ui.js";
import { renderAdminPanel, loadAdminAnnouncementSettings } from "./admin.js";
import { listenToClasses } from "./app.js";

export let currentUser = null;
export let isExpired = true;
export let isAdmin = false;

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

async function createNewUserProfile(uid, email) {
    const expiredAt = Date.now() - 1000;
    await set(ref(db, 'users/' + uid), {
        email: email, role: 'user', expired_at: expiredAt, created_at: Date.now()
    });
}

export async function checkUserStatus(uid) {
    currentUser = auth.currentUser;
    const userRef = ref(db, 'users/' + uid);
    onValue(userRef, (snapshot) => {
        const userData = snapshot.val();
        if (!userData) { createNewUserProfile(uid, currentUser.email); return; }

        isAdmin = userData.role === 'admin';
        const now = Date.now();
        isExpired = userData.expired_at < now;
        
        document.getElementById('user-email-display').innerHTML = `
            <div class="flex flex-col items-end">
                <span class="font-bold text-slate-700 text-sm">${userData.email}</span>
                <span class="text-[10px] text-slate-400 uppercase tracking-wide">${isAdmin ? 'Administrator' : 'Khách hàng'}</span>
            </div>
        `;

        if (isAdmin) {
            document.getElementById('expiry-badge').className = "px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-bold border border-purple-200 shadow-sm";
            document.getElementById('expiry-badge').innerHTML = `<i class="fa-solid fa-crown mr-1"></i> ADMIN PANEL`;
            document.getElementById('add-class-btn').disabled = false;
            document.getElementById('admin-section').classList.remove('hidden');
            document.getElementById('contact-banner').classList.add('hidden');
            renderAdminPanel();
            loadAdminAnnouncementSettings();
        } else if (isExpired) {
            document.getElementById('expiry-badge').className = "px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold border border-red-200";
            document.getElementById('expiry-badge').innerHTML = `<i class="fa-solid fa-lock mr-1"></i> Chưa kích hoạt`;
            document.getElementById('add-class-btn').disabled = true;
            document.getElementById('add-class-btn').classList.add('opacity-50', 'cursor-not-allowed');
            document.getElementById('admin-section').classList.add('hidden');
            document.getElementById('contact-banner').classList.remove('hidden');
        } else {
            const daysLeft = Math.ceil((userData.expired_at - now) / (1000 * 60 * 60 * 24));
            document.getElementById('expiry-badge').className = "px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold border border-green-200";
            document.getElementById('expiry-badge').innerHTML = `<i class="fa-solid fa-clock mr-1"></i> Còn ${daysLeft} ngày`;
            document.getElementById('add-class-btn').disabled = false;
            document.getElementById('add-class-btn').classList.remove('opacity-50', 'cursor-not-allowed');
            document.getElementById('admin-section').classList.add('hidden');
            document.getElementById('contact-banner').classList.add('hidden');
        }
        showAppScreen();
        listenToClasses(uid);
    });
}

export function loadSystemAnnouncement() {
    get(child(ref(db), 'system_settings/announcement')).then((snapshot) => {
        if (snapshot.exists()) {
            const data = snapshot.val();
            if (data.is_active === true) showGlobalModal(data.title || "Thông báo", data.content || "");
        }
    }).catch(console.error);
}
export function logout() { signOut(auth); }