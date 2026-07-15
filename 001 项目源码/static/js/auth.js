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
    if (!authToken) return;

    try {
        const resp = await fetch("/api/v1/auth/me", {
            headers: { "Authorization": `Bearer ${authToken}` },
        });
        const json = await resp.json();

        if (json.code === 0 && json.data) {
            currentUser = json.data;
            updateAuthUI();
            console.log("[Auth] 已恢复登录:", currentUser.username);
        } else {
            // 令牌失效，清除
            logout();
        }
    } catch (err) {
        console.error("[Auth] 令牌验证失败:", err);
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
            loginBtn.textContent = "退出";
            loginBtn.onclick = logout;
        } else {
            loginBtn.textContent = "登录";
            loginBtn.onclick = () => { location.href = "/login"; };
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
window.initAuth   = initAuth;
window.login      = login;
window.register   = register;
window.logout     = logout;
window.apiRequest = apiRequest;
window.requireAuth = requireAuth;
