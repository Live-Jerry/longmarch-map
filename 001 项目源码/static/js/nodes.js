/* -*- coding: utf-8 -*- */
/**
 * @file    nodes.js
 * @brief   节点交互模块 — V1.1.0
 * @details 显示激活节点信息面板。
 *          按V003§3.3步骤2：标志图片→战役→会议→事件→遗址→诗词→故事→人物→意义。
 *          所有活跃内容一次性渲染为上下可滚动的列表。无翻页，无步骤指示器。
 */

/** @type {number} 当前激活的节点编号 */
let currentNodeId = null;

/** @type {Object|null} 当前节点数据 */
let currentNodeData = null;

/** @type {string|null} 当前节点图片URL */
let currentNodeImageUrl = null;

/** @type {Array} 节点活跃内容字段列表 */
let currentActiveSections = [];

/**
 * @const CONTENT_ORDER
 * @brief 节点内容显示顺序（V003 §3.3 步骤2）
 * @details 标志图片固定在最上方，后续内容按此顺序从上到下排列。
 *          无内容的项跳过不显示。
 */
const CONTENT_ORDER = [
    { key: "famous_battle",         label: "著名战役" },
    { key: "important_meeting",     label: "重要会议" },
    { key: "history_event",         label: "历史事件" },
    { key: "core_site",             label: "核心遗址" },
    { key: "poem_article",          label: "诗词文章" },
    { key: "typical_story",         label: "典型故事" },
    { key: "typical_people",        label: "典型人物" },
    { key: "historical_significance", label: "历史意义" },
];

/**
 * @function showNodePanel
 * @brief 打开节点信息面板，一次性渲染所有活跃内容
 * @param {Object} node 节点数据
 */
function showNodePanel(node) {
    currentNodeData = node;
    currentNodeId   = node.node_id;

    // 解析活跃字段列表
    currentActiveSections = [];
    if (node.active_sections) {
        if (Array.isArray(node.active_sections)) {
            currentActiveSections = node.active_sections;
        } else if (typeof node.active_sections === 'string') {
            try {
                currentActiveSections = JSON.parse(node.active_sections);
            } catch(e) {
                currentActiveSections = [];
            }
        }
    }

    // 填充面板基本信息
    document.getElementById("panel-title").textContent = node.title || "";
    document.getElementById("panel-meta").textContent  = `${node.time || ""} · ${node.location || ""}`;

    // 设置节点图片URL
    currentNodeImageUrl = `/node-image/${node.node_id}`;

    // 渲染图片区（固定顶部）
    renderImageSection();

    // 渲染所有活跃内容（一次性，可滚动）
    renderAllContent();

    // 显示面板
    document.getElementById("info-panel").classList.add("visible");

    // 关闭留言板
    hideMessageBoard();

    // 全局语音开时自动朗读
    if (window.voiceEnabled) {
        // 延迟一点让面板渲染完成
        setTimeout(() => {
            if (typeof readCurrentContent === "function") {
                readCurrentContent();
            }
        }, 300);
    }
}

/**
 * @function renderImageSection
 * @brief 在 panel-image 区域渲染节点图片（固定顶部不滚动）
 */
function renderImageSection() {
    const imgUrl = currentNodeImageUrl || `/node-image/${currentNodeId}`;
    const container = document.getElementById("panel-image");
    if (!container) return;
    container.innerHTML = `
        <img src="${imgUrl}" alt="${currentNodeData?.title || ''}"
             class="node-image"
             onerror="this.onerror=null; this.parentElement.innerHTML=buildPlaceholderFlag();">
    `;
}

/**
 * @function renderAllContent
 * @brief 一次性渲染所有活跃内容段，按设计顺序从上到下排列
 * @details 无内容的段跳过不显示。整个 panel-body 可上下滑动。
 */
function renderAllContent() {
    if (!currentNodeData) return;
    const body = document.getElementById("panel-body");
    if (!body) return;

    let html = "";

    // 是否活跃的判断
    const isActive = (key) => {
        if (currentActiveSections.length > 0) {
            return currentActiveSections.includes(key);
        }
        // fallback：检查数据中是否有内容
        const val = currentNodeData[key];
        return val && typeof val === "string" && val.trim().length > 0 && val.trim() !== "无";
    };

    CONTENT_ORDER.forEach(item => {
        if (!isActive(item.key)) return;
        const val = currentNodeData[item.key];
        if (!val || typeof val !== "string" || val.trim() === "" || val.trim() === "无" || val.trim().indexOf("无。") === 0) return;
        html += `
            <div class="info-section">
                <div class="section-title">${item.label}</div>
                <div class="section-content">${escapeHtml(val)}</div>
            </div>
        `;
    });

    if (!html) {
        html = '<div class="empty-state">暂无相关内容</div>';
    }

    body.innerHTML = html;
}

/**
 * @function closeNodePanel
 * @brief 关闭节点信息面板
 */
function closeNodePanel() {
    document.getElementById("info-panel").classList.remove("visible");
    currentNodeId   = null;
    currentNodeData = null;
    currentActiveSections = [];
    stopSpeech();
}

/**
 * @function readCurrentContent
 * @brief 朗读面板中所有可视内容（使用 Web Speech API）
 */
function readCurrentContent() {
    if (!currentNodeData) return;

    // 收集所有活跃的内容文本
    const isActive = (key) => {
        if (currentActiveSections.length > 0) return currentActiveSections.includes(key);
        const val = currentNodeData[key];
        return val && typeof val === "string" && val.trim().length > 0 && val.trim() !== "无";
    };

    let texts = [];

    // 开头朗读节点名称和时间
    const nodeTitle = currentNodeData.title || "";
    const nodeTime = currentNodeData.time || "";
    if (nodeTitle) texts.push(nodeTitle);
    if (nodeTime) texts.push(nodeTime);

    // 各内容字段
    CONTENT_ORDER.forEach(item => {
        if (!isActive(item.key)) return;
        const val = currentNodeData[item.key];
        if (val && typeof val === "string" && val.trim() !== "" && val.trim() !== "无" && val.trim().indexOf("无。") !== 0) {
            texts.push(item.label + "：" + val);
        }
    });

    if (texts.length === 0) return;

    // 朗读开始：移除所有旧高亮，给第一个 section 添加 reading 类
    document.querySelectorAll('.info-section.reading').forEach(el => el.classList.remove('reading'));
    const firstSection = document.querySelector('.info-section');
    if (firstSection) {
        firstSection.classList.add('reading');
    }

    // 关联 currentUtterance 的 onend 以清理高亮
    speakText(texts.join("。"));
    if (currentUtterance) {
        const originalOnEnd = currentUtterance.onend;
        currentUtterance.onend = function() {
            document.querySelectorAll('.info-section.reading').forEach(el => el.classList.remove('reading'));
            if (typeof originalOnEnd === 'function') originalOnEnd.call(this);
        };
    }
}

// ============================================================================
// TTS（文字转语音）— 基于 Web Speech API
// ============================================================================

/** @type {SpeechSynthesisUtterance|null} 当前朗读实例 */
let currentUtterance = null;

/** @type {SpeechSynthesisVoice[]} 缓存的语音列表 */
let cachedVoices = [];

/** @type {boolean} 语音列表是否已加载完成 */
let voicesReady = false;

/** @type {boolean} 是否已对 Chrome 语音引擎做初始化 */
let speechEnginePrimed = false;

/**
 * @function initVoices
 * @brief 预加载语音列表（解决 Chrome 首次 getVoices() 返回空的问题）
 * @details 在页面加载时调用，触发语音异步加载并监听 voiceschanged 事件。
 *          首次调用 getVoices() 触发后台加载，加载完成后通过 voiceschanged
 *          拿到完整列表。同时做 Chrome 语音引擎初始化。
 */
function initVoices() {
    if (!("speechSynthesis" in window)) return;

    // 触发异步加载
    cachedVoices = window.speechSynthesis.getVoices();
    if (cachedVoices.length > 0) {
        voicesReady = true;
        primeSpeechEngine();
    }

    // 监听语音加载完成事件
    window.speechSynthesis.onvoiceschanged = function() {
        cachedVoices = window.speechSynthesis.getVoices();
        voicesReady = true;
        primeSpeechEngine();
    };
}

/**
 * @function primeSpeechEngine
 * @brief Chrome 语音引擎初始化
 * @details Chrome 有一个已知 bug（crbug.com/435233）：首次 speak()
 *          调用有时不发音。在页面加载后先生成一个极低音量的哑发言
 *          来初始化语音引擎。
 */
function primeSpeechEngine() {
    if (speechEnginePrimed) return;
    if (!("speechSynthesis" in window)) return;
    try {
        const dummy = new SpeechSynthesisUtterance("");
        dummy.volume = 0.01;
        dummy.rate = 1.0;
        dummy.lang = "zh-CN";
        window.speechSynthesis.speak(dummy);
        speechEnginePrimed = true;
    } catch (e) {
        // 静默失败
    }
}

/**
 * @function getChineseVoice
 * @brief 获取第一个可用的中文语音
 * @returns {SpeechSynthesisVoice|null} 找到的中文语音，未找到返回 null
 */
function getChineseVoice() {
    const list = voicesReady ? cachedVoices : window.speechSynthesis.getVoices();
    return list.find(function(v) { return v.lang.startsWith("zh-CN"); })
        || list.find(function(v) { return v.lang.startsWith("zh"); });
}

/**
 * @function speakText
 * @brief 使用 Web Speech API 朗读文本
 * @param {string} text 要朗读的文本
 */
function speakText(text) {
    if (!("speechSynthesis" in window)) {
        alert("当前浏览器不支持语音朗读功能");
        return;
    }
    stopSpeech();

    // 如果语音还没加载好，尝试触发一次并立即返回
    // 即使没有特定语音，设置 lang=zh-CN 浏览器也会用默认中文语音
    if (!voicesReady) {
        // 再试一次直接获取
        const immediate = window.speechSynthesis.getVoices();
        if (immediate.length > 0) {
            cachedVoices = immediate;
            voicesReady = true;
            primeSpeechEngine();
        } else {
            // 语音尚未加载，但先让浏览器用默认语音开始朗读
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = "zh-CN";
            utter.rate = 0.9;
            utter.pitch = 1.0;
            utter.volume = 1.0;
            currentUtterance = utter;
            window.speechSynthesis.speak(utter);
            return;
        }
    }

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "zh-CN";
    utter.rate = 0.9;
    utter.pitch = 1.0;
    utter.volume = 1.0;

    const zhVoice = getChineseVoice();
    if (zhVoice) utter.voice = zhVoice;

    currentUtterance = utter;
    window.speechSynthesis.speak(utter);
}

/**
 * @function stopSpeech
 * @brief 停止当前朗读
 */
function stopSpeech() {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    currentUtterance = null;
}

// ============================================================================
// 星火入口
// ============================================================================

/**
 * @function openSparkForm
 * @brief 打开星火投稿表单
 */
function openSparkForm() {
    if (!currentNodeId) return;
    const content = prompt(
        `【星火投稿】\n节点：${currentNodeData?.title}\n\n` +
        `请输入您要提交的历史资料或回忆内容：`
    );
    if (!content || !content.trim()) return;
    const title = prompt("请输入投稿标题：");
    if (!title || !title.trim()) return;
    submitSpark({
        node_id: currentNodeId,
        title:   title.trim(),
        content: content.trim(),
    });
}

/**
 * @function submitSpark
 * @brief 提交星火内容到后端
 * @param {Object} data
 * @async
 */
async function submitSpark(data) {
    const token = localStorage.getItem("lm_token");
    if (!token) { alert("请先登录后再投稿"); location.href = "/login"; return; }
    try {
        const resp = await fetch("/api/v1/sparks", {
            method:  "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        });
        const json = await resp.json();
        if (json.code === 0) {
            alert("投稿成功！感谢您为长征文化传承贡献力量。");
        } else {
            alert("投稿失败：" + json.message);
        }
    } catch (err) {
        alert("网络错误，请稍后重试");
    }
}

// ============================================================================
// 工具函数
// ============================================================================

/**
 * @function escapeHtml
 * @brief HTML 特殊字符转义
 */
function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/\n/g, "<br>");
}

/**
 * @function buildPlaceholderFlag
 * @brief 生成图片加载失败时的占位军旗HTML
 */
function buildPlaceholderFlag() {
    return '<div class="node-image-placeholder">' +
        '<div class="placeholder-flag">' +
        '<svg width="160" height="100" viewBox="0 0 160 100" xmlns="http://www.w3.org/2000/svg">' +
        '<rect x="20" y="15" width="120" height="55" rx="2" fill="#c0392b" stroke="rgba(255,255,255,0.3)" stroke-width="0.8"/>' +
        '<rect x="14" y="10" width="4" height="70" rx="1" fill="#8B4513"/>' +
        '<polygon points="50,32 55,46 70,46 58,55 62,70 50,60 38,70 42,55 30,46 45,46" fill="#ffd700"/>' +
        '<text x="80" y="45" font-family="sans-serif" font-size="9" fill="rgba(255,255,255,0.4)" text-anchor="middle">暂无照片</text>' +
        '<text x="80" y="57" font-family="sans-serif" font-size="7" fill="rgba(255,255,255,0.25)" text-anchor="middle">红一方面军军旗</text>' +
        '</svg></div></div>';
}

/**
 * @function hideMessageBoard
 * @brief 关闭留言板
 */
function hideMessageBoard() {
    const mb = document.getElementById("message-board");
    if (mb) mb.classList.remove("visible");
}

// 在页面加载时初始化语音系统
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initVoices);
} else {
    initVoices();
}

// 导出
window.showNodePanel   = showNodePanel;
window.closeNodePanel  = closeNodePanel;
window.readCurrentContent = readCurrentContent;
window.speakText       = speakText;
window.stopSpeech      = stopSpeech;
window.openSparkForm   = openSparkForm;
window.submitSpark     = submitSpark;
window.escapeHtml      = escapeHtml;
window.buildPlaceholderFlag = buildPlaceholderFlag;
