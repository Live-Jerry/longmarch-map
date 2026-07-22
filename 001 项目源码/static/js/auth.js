/* -*- coding: utf-8 -*- */
/**
 * @file    auth.js
 * @brief   用户认证模块
 * @details 处理登录、注册、令牌存储、请求拦截（自动附加 Token）等。
 * @author  长征文化数字地图项目组
 * @date    2026-07-15
 */

/** @type {string|null} 当前登录用户的令牌 */
let authToken = localStorage.getItem("lm_token");

/** @type {Object|null} 当前登录用户信息 */
let currentUser = null;

/**
 * @function initAuth
 * @brief 初始化认证状态（页面加载时调用）
 * @details 从 localStorage 恢复登录状态，并验证令牌有效性
 * @async
 */
async function initAuth() {
    if (authToken) {
        try {
            const resp = await fetch("/api/v1/auth/me", {
                headers: { "Authorization": `Bearer ${authToken}` },
            });
            const json = await resp.json();

            if (json.code === 0 && json.data) {
                currentUser = json.data;
                console.log("[Auth] 已恢复登录:", currentUser.username);
            } else {
                // 令牌失效，清除
                logout();
            }
        } catch (err) {
            console.error("[Auth] 令牌验证失败:", err);
        }
    }
    // 无论是否登录，都初始化按钮状态
    updateAuthUI();
}

// =============================================================================
// 认证弹窗控制
// =============================================================================

/**
 * @function openAuthModal
 * @brief 打开认证弹窗
 * @param {string} [tab="login"] 默认显示的标签页: login|register|reset
 */
function openAuthModal(tab) {
    if (currentUser) {
        logout();
        return;
    }
    const modal = document.getElementById("auth-modal");
    if (!modal) return;
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
    switchAuthTab(tab || "login");
    // 清除所有状态信息
    document.querySelectorAll("#auth-modal .form-status").forEach(function(el) {
        el.textContent = "";
        el.className = "form-status";
    });
}

/**
 * @function closeAuthModal
 * @brief 关闭认证弹窗
 */
function closeAuthModal() {
    const modal = document.getElementById("auth-modal");
    if (!modal) return;
    modal.style.display = "none";
    document.body.style.overflow = "";
}

/**
 * @function switchAuthTab
 * @brief 切换认证弹窗标签页（登录/注册/忘记密码）
 * @param {string} tab "login"|"register"|"reset"
 */
function switchAuthTab(tab) {
    // 切换标签按钮高亮
    document.querySelectorAll("#auth-modal .auth-tab").forEach(function(btn) {
        btn.classList.toggle("active", btn.dataset.tab === tab);
    });
    // 切换表单显示
    var panels = ["auth-login", "auth-register", "auth-reset"];
    panels.forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.style.display = "none";
    });
    var targetEl = document.getElementById("auth-" + tab);
    if (targetEl) targetEl.style.display = "block";
    // 清除状态消息
    document.querySelectorAll("#auth-modal .form-status").forEach(function(el) {
        el.textContent = "";
        el.className = "form-status";
    });
}

// =============================================================================
// 表单提交处理
// =============================================================================

/**
 * @function handleLoginForm
 * @brief 处理登录表单提交
 */
async function handleLoginForm(e) {
    e.preventDefault();
    var form = e.target;
    var username = form.querySelector("[name='username']").value.trim();
    var password = form.querySelector("[name='password']").value;
    var statusEl = form.querySelector(".form-status");

    if (!username || !password) {
        statusEl.textContent = "请输入用户名和密码";
        statusEl.className = "form-status error";
        return;
    }

    var submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "登录中..."; }

    try {
        var result = await login(username, password);
        if (result.success) {
            statusEl.textContent = "✅ 登录成功";
            statusEl.className = "form-status success";
            setTimeout(closeAuthModal, 1000);
        } else {
            statusEl.textContent = "❌ " + result.message;
            statusEl.className = "form-status error";
        }
    } catch (err) {
        statusEl.textContent = "❌ 网络错误，请重试";
        statusEl.className = "form-status error";
    } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = "登 录"; }
    }
}

/**
 * @function handleRegisterForm
 * @brief 处理注册表单提交
 */
async function handleRegisterForm(e) {
    e.preventDefault();
    var form = e.target;
    var username = form.querySelector("[name='username']").value.trim();
    var password = form.querySelector("[name='password']").value;
    var password2 = form.querySelector("[name='password2']").value;
    var statusEl = form.querySelector(".form-status");

    if (password !== password2) {
        statusEl.textContent = "两次输入的密码不一致";
        statusEl.className = "form-status error";
        return;
    }

    var submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "注册中..."; }

    try {
        var result = await register(username, password);
        if (result.success) {
            statusEl.textContent = "✅ 注册成功！已自动登录";
            statusEl.className = "form-status success";
            setTimeout(closeAuthModal, 1000);
        } else {
            statusEl.textContent = "❌ " + result.message;
            statusEl.className = "form-status error";
        }
    } catch (err) {
        statusEl.textContent = "❌ 网络错误，请重试";
        statusEl.className = "form-status error";
    } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = "注 册"; }
    }
}

/**
 * @function handleResetForm
 * @brief 处理忘记密码表单提交
 */
async function handleResetForm(e) {
    e.preventDefault();
    var form = e.target;
    var username = form.querySelector("[name='username']").value.trim();
    var newPassword = form.querySelector("[name='new_password']").value;
    var newPassword2 = form.querySelector("[name='new_password2']").value;
    var statusEl = form.querySelector(".form-status");

    if (newPassword !== newPassword2) {
        statusEl.textContent = "两次输入的新密码不一致";
        statusEl.className = "form-status error";
        return;
    }
    if (newPassword.length < 6) {
        statusEl.textContent = "密码至少需要 6 个字符";
        statusEl.className = "form-status error";
        return;
    }

    var submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "重置中..."; }

    try {
        var result = await resetPassword(username, newPassword);
        if (result.success) {
            statusEl.textContent = "✅ 密码重置成功，请登录";
            statusEl.className = "form-status success";
            // 2秒后切换到登录页
            setTimeout(function() { switchAuthTab("login"); }, 2000);
        } else {
            statusEl.textContent = "❌ " + result.message;
            statusEl.className = "form-status error";
        }
    } catch (err) {
        statusEl.textContent = "❌ 网络错误，请重试";
        statusEl.className = "form-status error";
    } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = "重置密码"; }
    }
}

/**
 * @function login
 * @brief 用户登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @async
 * @return {Object} { success: boolean, message: string }
 */
async function login(username, password) {
    try {
        const resp = await fetch("/api/v1/auth/login", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ username, password }),
        });
        const json = await resp.json();

        if (json.code === 0 && json.data) {
            authToken   = json.data.token;
            currentUser = json.data.user;
            localStorage.setItem("lm_token", authToken);
            updateAuthUI();
            return { success: true, message: "登录成功" };
        } else {
            return { success: false, message: json.message || "登录失败" };
        }
    } catch (err) {
        return { success: false, message: "网络错误，请稍后重试" };
    }
}

/**
 * @function register
 * @brief 用户注册
 * @param {string} username 用户名
 * @param {string} password 密码
 * @async
 * @return {Object} { success: boolean, message: string }
 */
async function register(username, password) {
    try {
        const resp = await fetch("/api/v1/auth/register", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ username, password }),
        });
        const json = await resp.json();

        if (json.code === 0 && json.data) {
            authToken   = json.data.token;
            currentUser = json.data.user;
            localStorage.setItem("lm_token", authToken);
            updateAuthUI();
            return { success: true, message: "注册成功" };
        } else {
            return { success: false, message: json.message || "注册失败" };
        }
    } catch (err) {
        return { success: false, message: "网络错误，请稍后重试" };
    }
}

/**
 * @function resetPassword
 * @brief 忘记密码 — 重设密码
 * @param {string} username 用户名
 * @param {string} newPassword 新密码
 * @async
 * @return {Object} { success: boolean, message: string }
 */
async function resetPassword(username, newPassword) {
    try {
        const resp = await fetch("/api/v1/auth/reset-password", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ username, new_password: newPassword }),
        });
        const json = await resp.json();

        if (json.code === 0) {
            return { success: true, message: json.message || "密码重置成功" };
        } else {
            return { success: false, message: json.message || "重置失败" };
        }
    } catch (err) {
        return { success: false, message: "网络错误，请稍后重试" };
    }
}

/**
 * @function logout
 * @brief 用户登出
 */
function logout() {
    authToken   = null;
    currentUser = null;
    localStorage.removeItem("lm_token");
    updateAuthUI();
    console.log("[Auth] 已登出");
}

/**
 * @function updateAuthUI
 * @brief 更新页面认证状态（顶部用户信息、导航等）
 */
function updateAuthUI() {
    // 更新顶部用户信息栏（若存在）
    const userEl = document.getElementById("current-user");
    if (userEl) {
        if (currentUser) {
            userEl.textContent = `${currentUser.username}（${currentUser.role}）`;
        } else {
            userEl.textContent = "";
        }
    }

    // 更新登录/登出按钮
    const loginBtn = document.getElementById("btn-login");
    if (loginBtn) {
        if (currentUser) {
            loginBtn.innerHTML = '<span class="icon">👤</span><span class="label">退出</span>';
            loginBtn.onclick = logout;
            loginBtn.title = "退出登录";
        } else {
            loginBtn.innerHTML = '<span class="icon">👤</span><span class="label">登录</span>';
            loginBtn.onclick = function() { openAuthModal("login"); };
            loginBtn.title = "用户登录/注册";
        }
    }

    // 管理后台按钮：仅 admin / super 可见
    const adminBtn = document.getElementById("btn-admin");
    if (adminBtn) {
        if (currentUser && ["admin", "super"].includes(currentUser.role)) {
            adminBtn.style.display = "";
        } else {
            adminBtn.style.display = "none";
        }
    }
}

/**
 * @function apiRequest
 * @brief 带认证令牌的统一请求封装
 * @param {string} url    请求 URL
 * @param {Object} opts   fetch 选项
 * @return {Promise<Object>}  响应 JSON
 */
async function apiRequest(url, opts = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(opts.headers || {}),
    };

    if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
    }

    const resp = await fetch(url, { ...opts, headers });
    return resp.json();
}

/**
 * @function requireAuth
 * @brief 检查登录状态，未登录则跳转登录页
 * @return {boolean} 是否已登录
 */
function requireAuth() {
    if (!authToken || !currentUser) {
        location.href = "/login";
        return false;
    }
    return true;
}

// 初始化
window.initAuth         = initAuth;
window.login            = login;
window.register         = register;
window.resetPassword    = resetPassword;
window.logout           = logout;
window.apiRequest       = apiRequest;
window.requireAuth      = requireAuth;
window.openAuthModal    = openAuthModal;
window.closeAuthModal   = closeAuthModal;
window.switchAuthTab    = switchAuthTab;
window.handleLoginForm  = handleLoginForm;
window.handleRegisterForm = handleRegisterForm;
window.handleResetForm  = handleResetForm;
