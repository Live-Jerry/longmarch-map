/* -*- coding: utf-8 -*- */
/**
 * @file    nodes.js
 * @brief   节点交互模块
 * @details V1.1.0: 按 active_sections 过滤显示, 图片固定在面板顶部不随内容滚动
 */

/** @type {number} 当前激活的节点编号 */
let currentNodeId = null;

/** @type {number} 当前步骤（0~4） */
let currentStep = 0;

/** @type {Object|null} 当前节点数据 */
let currentNodeData = null;

/** @type {string|null} 当前节点图片URL */
let currentNodeImageUrl = null;

/** @type {Array} 节点活跃内容字段列表 */
let currentActiveSections = [];

/** 节点内容的步骤定义（5步流程） */
const NODE_STEPS = [
    { key: "time",                  label: "历史时间" },
    { key: "famous_battle",         label: "著名战役" },
    { key: "important_meeting",     label: "重要会议" },
    { key: "history_event",         label: "历史事件" },
    { key: "historical_significance", label: "历史意义" },
];

/** 其他内容（扩展信息） */
const NODE_EXTRA = [
    { key: "core_site",             label: "核心遗址" },
    { key: "poem_article",          label: "诗词文章" },
    { key: "typical_story",         label: "典型故事" },
    { key: "typical_people",        label: "典型人物" },
    { key: "spark_remains",         label: "星火遗存" },
];

/**
 * @function showNodePanel
 * @brief 打开节点信息面板
 * @param {Object} node 节点数据
 */
function showNodePanel(node) {
    currentNodeData = node;
    currentNodeId   = node.node_id;
    currentStep     = 0;

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

    // 渲染图片区（固定在顶部，不随内容滚动）
    renderImageSection();

    // 渲染第一步内容
    renderStep(0);
    updateStepIndicator();

    // 显示面板
    document.getElementById("info-panel").classList.add("visible");

    // 关闭留言板
    hideMessageBoard();
}

/**
 * @function renderImageSection
 * @brief 在 panel-image 区域渲染节点图片
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
 * @function renderStep
 * @brief 渲染指定步骤的内容，跳过 inactive 步骤
 * @param {number} stepIdx 步骤索引（0~4）
 */
function renderStep(stepIdx) {
    if (!currentNodeData) return;
    currentStep = stepIdx;

    // 找到第一个 active 的步骤
    const steps = getActiveSteps();
    if (steps.length === 0) {
        document.getElementById("panel-body").innerHTML = '<div class="empty-state">暂无内容</div>';
        return;
    }

    // 确保 currentStep 指向有效的步骤
    if (stepIdx >= steps.length) {
        currentStep = steps.length - 1;
        stepIdx = currentStep;
    }

    const stepKey = steps[stepIdx];
    const stepDef = NODE_STEPS.find(s => s.key === stepKey) || { key: stepKey, label: stepKey };
    let value = currentNodeData[stepKey] || "";
    
    // 如果value为空或无意义，也跳过
    if (!value || value.trim() === '' || value.trim() === '无') {
        value = '';
    }

    const body = document.getElementById("panel-body");
    let html = '';

    // 渲染主步骤内容
    if (value) {
        html += `
            <div class="info-section">
                <div class="section-title">${stepDef.label}</div>
                <div class="section-content">${escapeHtml(value)}</div>
            </div>
        `;
    }

    // 渲染扩展信息（只显示 active 的）
    let extraHtml = "";
    NODE_EXTRA.forEach(ex => {
        if (!currentActiveSections.includes(ex.key)) return;
        const val = currentNodeData[ex.key];
        if (val && typeof val === "string" && val.trim().length > 0 && val.trim() !== '无') {
            extraHtml += `
                <div class="info-section">
                    <div class="section-title">${ex.label}</div>
                    <div class="section-content">${escapeHtml(val)}</div>
                </div>`;
        }
    });

    if (extraHtml) {
        html += `
            <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1)">
                <div style="font-size:11px;color:#95a5a6;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px">更多信息</div>
                ${extraHtml}
            </div>`;
    }

    body.innerHTML = html || '<div class="empty-state">暂无相关内容</div>';
    updateStepIndicator();
}

/**
 * @function getActiveSteps
 * @brief 获取当前节点活跃的主步骤列表（过滤掉 inactive 的步骤）
 * @return {Array<string>} step keys
 */
function getActiveSteps() {
    const allSteps = NODE_STEPS.map(s => s.key);
    if (currentActiveSections.length > 0) {
        return allSteps.filter(k => currentActiveSections.includes(k));
    }
    return allSteps; // fallback: show all if no active_sections data
}

/**
 * @function updateStepIndicator
 * @brief 更新左侧步骤指示器
 */
function updateStepIndicator() {
    const el = document.getElementById("step-indicator");
    if (!el) return;

    const steps = getActiveSteps();
    const total = steps.length;
    if (total === 0) {
        el.classList.remove("visible");
        return;
    }

    const currentStepKey = steps[currentStep] || steps[0];
    const stepDef = NODE_STEPS.find(s => s.key === currentStepKey) || { label: currentStepKey };
    const pct = ((currentStep + 1) / total) * 100;

    el.querySelector(".step-title").textContent =
        `${currentStep + 1}. ${stepDef.label}`;
    el.querySelector(".step-progress-bar").style.width = `${pct}%`;

    el.classList.add("visible");
}

/**
 * @function nextStep
 * @brief 显示下一步内容
 */
function nextStep() {
    const steps = getActiveSteps();
    if (currentStep < steps.length - 1) {
        renderStep(currentStep + 1);
    }
}

/**
 * @function prevStep
 * @brief 显示上一步内容
 */
function prevStep() {
    if (currentStep > 0) {
        renderStep(currentStep - 1);
    }
}

/**
 * @function closeNodePanel
 * @brief 关闭节点信息面板
 */
function closeNodePanel() {
    document.getElementById("info-panel").classList.remove("visible");
    document.getElementById("step-indicator").classList.remove("visible");
    currentNodeId   = null;
    currentNodeData = null;
    currentStep     = 0;
    currentActiveSections = [];
    stopSpeech();
}

/**
 * @function readCurrentStep
 * @brief 朗读当前步骤内容（使用 Web Speech API）
 */
function readCurrentStep() {
    if (!currentNodeData) return;
    const steps = getActiveSteps();
    if (currentStep >= steps.length) return;
    const stepKey = steps[currentStep];
    const text = currentNodeData[stepKey] || "";
    if (!text) return;
    speakText(text);
}

// ============================================================================
// TTS（文字转语音）— 基于 Web Speech API
// ============================================================================

/** @type {SpeechSynthesisUtterance|null} 当前朗读实例 */
let currentUtterance = null;

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
    const utter      = new SpeechSynthesisUtterance(text);
    utter.lang       = "zh-CN";
    utter.rate       = 0.9;
    utter.pitch      = 1.0;
    utter.volume     = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const zhVoice = voices.find(v => v.lang.includes("zh") && v.lang.includes("CN"))
                 || voices.find(v => v.lang.includes("zh"));
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

// 导出
window.showNodePanel   = showNodePanel;
window.nextStep        = nextStep;
window.prevStep        = prevStep;
window.closeNodePanel  = closeNodePanel;
window.readCurrentStep = readCurrentStep;
window.stopSpeech      = stopSpeech;
window.openSparkForm   = openSparkForm;
window.submitSpark     = submitSpark;
window.escapeHtml      = escapeHtml;
window.buildPlaceholderFlag = buildPlaceholderFlag;
