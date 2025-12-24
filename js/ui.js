// --- TAB NAVIGATION ---
export function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');
    const tabLogin = document.getElementById('tab-login');
    const tabReg = document.getElementById('tab-register');

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
        tabLogin.className = "flex-1 py-4 text-center font-bold text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50";
        tabReg.className = "flex-1 py-4 text-center font-medium text-slate-400 hover:text-slate-600";
    } else {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        tabReg.className = "flex-1 py-4 text-center font-bold text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50/50";
        tabLogin.className = "flex-1 py-4 text-center font-medium text-slate-400 hover:text-slate-600";
    }
}

export function showLoginScreen() {
    document.getElementById('auth-container').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
}

export function showAppScreen() {
    document.getElementById('auth-container').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
}

// --- POPUP MODAL ---
export function showGlobalModal(title, content) {
    document.getElementById('popup-title').innerHTML = `<i class="fa-solid fa-bell mr-2"></i> ${title}`;
    document.getElementById('popup-content').innerText = content;
    document.getElementById('global-modal').classList.remove('hidden');
}

export function closeModal() {
    document.getElementById('global-modal').classList.add('hidden');
}

// --- APP UI ---
export function updateStats(total, available) {
    document.getElementById('stat-total').innerText = total;
    document.getElementById('stat-available').innerText = available;
}

export function createClassCard(id, data) {
    const isAvail = parseInt(data.slots) > 0;
    const isError = data.slots === '?' || data.slots === 'Lỗi' || data.slots === 'Unknown';
    
    let statusBadge = isAvail 
        ? `<span class="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Có Slot</span>`
        : (isError ? `<span class="bg-yellow-100 text-yellow-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Check</span>` 
                   : `<span class="bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Full</span>`);

    return `
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-md transition-all relative overflow-hidden group">
            <div class="flex justify-between items-start mb-3">
                <div class="flex-1 pr-2">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">${data.code}</span>
                        ${statusBadge}
                    </div>
                    <h3 class="font-bold text-slate-800 text-sm leading-tight line-clamp-2 h-10" title="${data.name}">${data.name}</h3>
                </div>
            </div>
            <div class="bg-slate-50 rounded-lg p-2 mb-3 flex justify-between items-center border border-slate-100">
                    <div class="text-xs text-slate-500">Mã: <span class="font-mono font-bold text-slate-700 select-all">${data.registration_code}</span></div>
                    <button onclick="navigator.clipboard.writeText('${data.registration_code}')" class="text-slate-400 hover:text-indigo-600"><i class="fa-regular fa-copy"></i></button>
            </div>
            <div class="flex justify-between items-end border-t border-slate-100 pt-3">
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-semibold">Slot</div>
                    <div class="text-2xl font-black ${isAvail ? 'text-green-600' : 'text-slate-700'}">${data.slots}</div>
                </div>
                <div class="flex items-center gap-3 opacity-100 md:opacity-0 group-hover:opacity-100 transition-opacity">
                    <a href="${data.url}" target="_blank" class="text-blue-500 hover:text-blue-700 text-sm font-medium">Link</a>
                    <button onclick="window.deleteClass('${id}')" class="text-slate-300 hover:text-red-500 p-1"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
        </div>
    `;
}